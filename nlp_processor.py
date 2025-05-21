# services/utils/nlp_processor.py

import os
import json
import unidecode
import re

def load_linhas():
    with open("data/data_linhas.json", "r", encoding="utf-8") as f:
        return json.load(f)

def normalize_text(texto: str) -> str:
    """
    Remove acentos, coloca em minúsculas e normaliza para ASCII.
    """
    return unidecode.unidecode(texto).lower()

def extract_origin_destination(texto: str) -> dict:
    """
    Identifica origem e destino em uma frase, buscando todas as estações por substring,
    ordenando pela posição de aparição, e garantindo que sejam duas estações distintas.
    
    Retorna:
      - {"origem": <station>, "destino": <station>}
      - ou {"error": "<mensagem de erro>"}
    """
    norm_input = normalize_text(texto)

    # Carrega lista de todas as estações
    linhas_data = load_linhas().get("linhas", [])
    all_stations = [s for linha in linhas_data for s in linha.get("estacoes", [])]

    encontrados = []
    # Para cada estação, encontra todas as posições de ocorrência no texto
    for station in all_stations:
        norm_station = normalize_text(station)
        # faz finditer para capturar todas as ocorrências da string "norm_station"
        for match in re.finditer(re.escape(norm_station), norm_input):
            idx = match.start()
            encontrados.append((idx, station))

    # Se não houver pelo menos 2 ocorrências (mesmo que duplicadas), não conseguimos extrair
    if len(encontrados) < 2:
        return {"error": "Não foi possível extrair origem e destino da frase."}

    # Ordena tudo pelo índice de ocorrência
    encontrados.sort(key=lambda x: x[0])  # (posição, nome_da_estação)

    # Agora, selecionamos a primeira estação encontrada como origem
    origem = encontrados[0][1]

    # Procuramos a próxima estação que seja diferente de 'origem'
    destino = None
    for pos, est in encontrados[1:]:
        if est != origem:
            destino = est
            break

    if not destino:
        # Não achamos nenhuma estação diferente, então não dá para extrair um destino válido
        return {"error": "Não foi possível extrair duas estações distintas."}

    return {"origem": origem, "destino": destino}

def nlp_pipeline(user_input: str) -> dict:
    """
    Usa apenas matching de string para extrair origem/destino.
    Retorna dicionário com:
      {"origem": <station>, "destino": <station>, "modos_de_transporte": ["rapido","simples","acessivel"]}
    Ou {"error": "<mensagem>"} caso falhe.
    """
    pair = extract_origin_destination(user_input)
    if "error" in pair:
        return pair

    origem  = pair["origem"]
    destino = pair["destino"]
    return {"origem": origem, "destino": destino}
