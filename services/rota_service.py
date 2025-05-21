# services/altRotas_services.py
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import unicodedata
import requests
import networkx as nx
from nlp_processor import nlp_pipeline, load_linhas

# Carrega dados de linhas
dados = load_linhas()

# Constante base de tempo (em minutos) por aresta
TEMPO_BASE = 3

# Grafo global
G = nx.Graph()

def normalize(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("ASCII").casefold()

def get_status() -> dict:
    """
    (Opcional) Consulta API externa para saber se uma linha está com problema:
    retorna dicionário { 'nome_linha_normalizada': 'situação' }
    Se não precisar, pode deixar vazio.
    """
    status_operacao = {}
    try:
        resp = requests.get(
            "https://www.diretodostrens.com.br/api/status",
            verify=False,
            timeout=5,
        )
        resp.raise_for_status()
        for item in resp.json():
            nome = normalize(item.get("nome", ""))
            status_operacao[nome] = item.get("situacao", "").strip().lower()
    except Exception:
        pass
    return status_operacao

status_operacao = get_status()

def _build_graph():
    """
    Monta o grafo G: cada estação é um nó, cada par adjacente de estações
    vira uma aresta com peso inicial TEMPO_BASE e atributo 'linha'.
    """
    for linha in dados.get("linhas", []):
        nome_linha = linha.get("nome", "")
        estacoes = linha.get("estacoes", [])
        for a, b in zip(estacoes[:-1], estacoes[1:]):
            G.add_edge(a, b, tempo=TEMPO_BASE, linha=nome_linha)

    # Marca baldeações: se uma estação aparece em ≥2 linhas, G.nodes[est]['baldeacoes'] armazenará essa lista de linhas
    for est in list(G.nodes):
        linhas_na_est = [l["nome"] for l in dados.get("linhas", []) if est in l["estacoes"]]
        if len(linhas_na_est) > 1:
            G.nodes[est]["baldeacoes"] = linhas_na_est

# Constroi o grafo uma única vez
_build_graph()

def calcular_peso(u: str, v: str, modo: str = "rapido") -> float:
    """
    Retorna peso da aresta (u,v), aumentando se a linha estiver com falha
    ou se, no modo 'simples', existir baldeação.
    Como estamos usando apenas 'rapido', praticamente devolve TEMPO_BASE (+ penalidade).
    """
    attr = G.get_edge_data(u, v) or {}
    tempo = attr.get("tempo", TEMPO_BASE)
    linha = attr.get("linha", "")
    situacao = status_operacao.get(normalize(linha), "")
    # Se a linha tiver alguma falha, penaliza:
    if any(palavra in situacao for palavra in ["reduzida", "falha", "interrup"]):
        tempo += 10
    # No modo 'simples', penaliza cada baldeação:
    if modo == "simples" and G.nodes[u].get("baldeacoes"):
        tempo += 3
    # No modo 'acessivel', penaliza fixo:
    elif modo == "acessivel":
        tempo += 2
    return tempo

def custo_total(caminho: list[str], modo: str) -> float:
    """
    Soma o peso de cada aresta em 'caminho'
    """
    total = 0.0
    for u, v in zip(caminho[:-1], caminho[1:]):
        total += calcular_peso(u, v, modo)
    return total

def detectar_baldeacoes(caminho: list[str]) -> list[tuple[str,str,str]]:
    """
    Recebe uma lista de estações (caminho), e devolve lista de tuplas
    (estação_de_baldeação, linha_anterior, linha_nova) somente quando 
    a linha do segmento muda de um par para o próximo.
    """
    baldeacoes = []
    # Compila a lista de linhas para cada par adjacente
    segmentos = []
    for u, v in zip(caminho[:-1], caminho[1:]):
        data = G.get_edge_data(u, v) or {}
        segmentos.append(data.get("linha", ""))

    # Se a linha no índice i for diferente de i-1, existe baldeação na estação i
    for i in range(1, len(segmentos)):
        if segmentos[i] != segmentos[i - 1]:
            est_transferencia = caminho[i]
            linha_anterior = segmentos[i - 1]
            linha_nova = segmentos[i]
            baldeacoes.append((est_transferencia, linha_anterior, linha_nova))
    return baldeacoes

def obter_melhor_rota(origem: str = None, destino: str = None) -> str:
    """
    Se origem ou destino for None, usa nlp_pipeline para extrair.
    Só calcula modo “rapido” (A* + heurística de número de saltos).
    """
    if not origem or not destino:
        resultado = nlp_pipeline(f"{origem or ''} até {destino or ''}")
        if "error" in resultado:
            return resultado["error"]
        origem, destino = resultado["origem"], resultado["destino"]

    # Garante que as estações existem:
    all_stations = [s for linha in dados.get("linhas", []) for s in linha.get("estacoes", [])]
    if origem not in all_stations or destino not in all_stations:
        return f"Não encontrei a estação “{origem}” ou “{destino}”."

    modo = "rapido"
    try:
        # Heurística: TEMPO_BASE × (número de saltos)
        heur = lambda u, v: TEMPO_BASE * (len(nx.shortest_path(G, u, v)) - 1)
        caminho = nx.astar_path(
            G, origem, destino,
            heuristic=heur,
            weight=lambda u, v, d: calcular_peso(u, v, modo)
        )
    except nx.NetworkXNoPath:
        return f"Não há rota disponível de {origem} até {destino}."

    custo = custo_total(caminho, modo)
    baldeacoes = detectar_baldeacoes(caminho)
    rota_str = " → ".join(caminho)

    texto = [
        f"🚌 **Rota recomendada** de {origem} até {destino}:",
        f"   • 🚆 Modo: {modo.capitalize()}",
        f"   • 📍 Caminho: {rota_str}",
        f"   • ⏱️ Tempo estimado: {custo:.0f} minutos",
    ]

    if baldeacoes:
        texto.append("   • 🔄 Trocas de linha:")
        for est, ant, novo in baldeacoes:
            texto.append(f"      – Em {est}: de {ant} para {novo}")
    else:
        texto.append("   • 🔄 Sem trocas de linha")

    texto.append("   • 🧭 Motivo: rota mais rápida considerando falhas e transferências.")
    return "\n".join(texto)

def process_user_query(user_input: str) -> str:
    """
    Chamado pelo pipeline. Retorna string formatada (ou mensagem de erro).
    """
    try:
        query = nlp_pipeline(user_input)
        if "error" in query:
            return query["error"]
        origem, destino = query["origem"], query["destino"]
        return obter_melhor_rota(origem, destino)
    except Exception as e:
        return f"Desculpe, algo deu errado ao calcular a rota: {e}"
