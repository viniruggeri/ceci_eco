# services/utils/nlp_processor.py
import os
import json
import unidecode

def load_linhas():
    """
    Carrega o JSON das linhas e retorna o dicionário completo.
    """
    with open("data/data_linhas.json", "r", encoding="utf-8") as f:
        return json.load(f)

def normalize_text(texto: str) -> str:
    """
    Remove acentos, special chars e coloca tudo em minúsculas.
    """
    return unidecode.unidecode(texto).lower()

def extract_origin_destination(texto: str) -> dict:
    """
    Identifica origem e destino em uma frase, usando correspondência direta
    de substrings (sem spaCy nem tradução). Retorna:
      - {"origem": <station>, "destino": <station>}
      - ou {"error": "<mensagem de erro>"}
    """
    # Normaliza entrada
    norm_input = normalize_text(texto)
    
    # Carrega lista de todas as estações
    linhas_data = load_linhas().get("linhas", [])
    all_stations = [s for linha in linhas_data for s in linha.get("estacoes", [])]
    
    encontrados = []
    # Itera por todas as estações, tentando encontrar como substring
    for station in all_stations:
        norm_station = normalize_text(station)
        if norm_station in norm_input:
            encontrados.append(station)
        if len(encontrados) == 2:
            break

    if len(encontrados) == 2:
        return {"origem": encontrados[0], "destino": encontrados[1]}
    
    return {"error": "Não foi possível extrair origem e destino da frase."}

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
    modos   = ["rapido", "simples", "acessivel"]
    return {"origem": origem, "destino": destino, "modos_de_transporte": modos}