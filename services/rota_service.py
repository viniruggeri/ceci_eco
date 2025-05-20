# services/altRotas_services.py
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unicodedata
import requests
import networkx as nx
import json
from nlp_processor import nlp_pipeline

def load_linhas():
    with open("data/data_linhas.json", "r", encoding="utf-8") as f:
        return json.load(f)
    
# Carrega dados de linhas
dados = load_linhas()
TEMPO_BASE = 3
G = nx.Graph()

# Normalização de texto para chaves
def normalize(texto: str) -> str:
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII').casefold()

# Obtém status de operação das linhas
def get_status() -> dict:
    status_operacao = {}
    try:
        resp = requests.get(
            "https://www.diretodostrens.com.br/api/status",
            verify=False,
            timeout=5
        )
        resp.raise_for_status()
        for item in resp.json():
            nome = normalize(item.get("nome", ""))
            status_operacao[nome] = item.get("situacao", "").strip()
    except Exception:
        pass
    return status_operacao

status_operacao = get_status()

# Constrói grafo de estações e linhas
def _build_graph():
    for linha in dados.get("linhas", []):
        nome_linha = linha.get("nome")
        operadora = linha.get("operadora")
        estacoes = linha.get("estacoes", [])
        for a, b in zip(estacoes[:-1], estacoes[1:]):
            G.add_edge(
                a, b,
                tempo=TEMPO_BASE,
                linha=nome_linha,
                operadora=operadora
            )
    # Baldeações
    for est in list(G.nodes):
        linhas_na_est = [l.get("nome") for l in dados.get("linhas", []) if est in l.get("estacoes", [])]
        if len(linhas_na_est) > 1:
            G.nodes[est]["baldeacoes"] = linhas_na_est
_build_graph()

# Cálculo de peso customizado
def calcular_peso(u, v, modo="rapido"):
    attr = G.get_edge_data(u, v) or {}
    tempo = attr.get("tempo", TEMPO_BASE)
    linha = attr.get("linha", "")
    situacao = status_operacao.get(normalize(linha), "")
    if any(p in situacao.lower() for p in ["reduzida", "falha", "interrup"]):
        tempo += 10
    if modo == "simples" and G.nodes[u].get("baldeacoes"):
        tempo += 3
    elif modo == "acessivel":
        tempo += 2
    return tempo

# Função para calcular custo total de um caminho
def custo_total(caminho, modo):
    total = 0
    for u, v in zip(caminho[:-1], caminho[1:]):
        total += calcular_peso(u, v, modo)
    return total

# Identifica transferências em um caminho
def detectar_baldeacoes(caminho):
    baldeacoes = []
    # Obtém linhas dos segmentos
    segmentos = []
    for u, v in zip(caminho[:-1], caminho[1:]):
        data = G.get_edge_data(u, v) or {}
        segmentos.append(data.get("linha", ""))
    # Verifica onde a linha muda
    for i in range(1, len(segmentos)):
        if segmentos[i] != segmentos[i-1]:
            est_transferencia = caminho[i]
            linha_anterior = segmentos[i-1]
            linha_nova = segmentos[i]
            baldeacoes.append((est_transferencia, linha_anterior, linha_nova))
    return baldeacoes

# Gera rota única otimizada entre orig e dest
def obter_melhor_rota(origem: str = None, destino: str = None) -> str:
    # Extrai origem/destino se não fornecidos
    if not origem or not destino:
        resultado = nlp_pipeline(f"{origem or ''} para {destino or ''}")
        if "error" in resultado:
            return resultado["error"]  # erro de NLP
        origem, destino = resultado["origem"], resultado["destino"]

    modos = ["rapido", "simples", "acessivel"]
    melhores = {}
    for modo in modos:
        try:
            if modo == "simples":
                caminho = nx.dijkstra_path(
                    G, origem, destino,
                    weight=lambda u, v, d: calcular_peso(u, v, modo)
                )
            else:
                caminho = nx.astar_path(
                    G, origem, destino,
                    heuristic=lambda u, v: TEMPO_BASE * (len(nx.shortest_path(G, u, v)) - 1),
                    weight=lambda u, v, d: calcular_peso(u, v, modo)
                )
            custo = custo_total(caminho, modo)
            melhores[modo] = {"caminho": caminho, "custo": custo}
        except nx.NetworkXNoPath:
            continue
    if not melhores:
        return f"Não há rota disponível de {origem} até {destino}."

    # Escolhe o modo de menor custo
    melhor_modo = min(melhores, key=lambda m: melhores[m]["custo"])
    dados_rota = melhores[melhor_modo]
    caminho = dados_rota["caminho"]
    custo = dados_rota["custo"]

    # Detecta baldeações
    baldeacoes = detectar_baldeacoes(caminho)
    # Formata a rota e justificativa
    rota_str = " → ".join(caminho)
    texto = (
        f"🚌 **Rota recomendada** de {origem} até {destino}:\n"
        f"   • 🚆 Modo: {melhor_modo.capitalize()}\n"
        f"   • 📍 Caminho: {rota_str}\n"
        f"   • ⏱️ Tempo estimado: {custo:.0f} minutos\n"
    )
    if baldeacoes:
        texto += "   • 🔄 Trocas de linha:\n"
        for est, ant, novo in baldeacoes:
            texto += f"      – Em {est}: de {ant} para {novo}\n"
    else:
        texto += "   • 🔄 Sem trocas de linha\n"
    texto += "   • 🧭 Motivo: rota mais rápida considerando trocas e falhas."


    return texto

# Valida se estação existe
def validar_estacao(estacao: str) -> bool:
    estacoes = load_linhas().get("linhas", [])
    all_stations = [s for l in estacoes for s in l["estacoes"]]
    return estacao in all_stations

# Função chamada pelo pipeline
def process_user_query(user_input: str) -> str:
    try:
        query = nlp_pipeline(user_input)
        if "error" in query:
            return "Não entendi de onde você quer ir. Tente: “Como chegar de [Origem] até [Destino]”."
        origem, destino = query["origem"], query["destino"]
        if not validar_estacao(origem) or not validar_estacao(destino):
            return f"Não achei a estação “{origem}” ou “{destino}”. Verifique se elas existem."
        return obter_melhor_rota(origem, destino)
    except Exception as e:
        return "Desculpe, algo deu errado ao calcular a rota. Tente novamente em alguns instantes."