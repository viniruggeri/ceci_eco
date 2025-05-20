# services/faq_service.py
import os
import json 
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import normalize
from langdetect import detect


MODEL = SentenceTransformer(
    'all-MiniLM-L6-v2',
    device="cpu"
)

SIM_THRESHOLD = 0.75

faq_ccr_raw        = json.load(open("data/faq_ccr.json",        "r", encoding="utf-8"))
faq_passageiro_raw = json.load(open("data/faq_passageiro.json", "r", encoding="utf-8"))

def _extract_list(raw: list, key: str):
    for item in raw:
        if isinstance(item, dict) and key in item:
            return item[key]
    return []

faq_ccr        = _extract_list(faq_ccr_raw,        "faqs_colaborador")
faq_passageiro = _extract_list(faq_passageiro_raw, "faqs_passageiro")

_all_faq = [*faq_ccr, *faq_passageiro]

_perguntas = [f["question"] for f in _all_faq]
_respostas = [f["answer"]   for f in _all_faq]

# Gera embeddings (já embarca em INT8) e normaliza
_embs = MODEL.encode(_perguntas, convert_to_numpy=True, batch_size=8)
_embs = normalize(_embs, axis=1)

# Constroi índice FAISS
d = _embs.shape[1]
nlist = 26
quantizer = faiss.IndexFlatIP(d)
index = faiss.IndexIVFFlat(quantizer, d, nlist, faiss.METRIC_INNER_PRODUCT)
index.train(_embs)
index.add(_embs)


def resposta_faq(user_query: str) -> str:
    lang = detect(user_query)
    if lang.startswith("en"):
        saudacao = "Sure! "
    elif lang.startswith("es"):
        saudacao = "¡Claro! "
    else:
        saudacao = ""

    q_emb = MODEL.encode([user_query], convert_to_numpy=True)
    q_emb = normalize(q_emb, axis=1)
    
    sim_scores, indices = index.search(q_emb, 1)
    best_sim = float(sim_scores[0][0])
    idx      = int(indices[0][0])

    if best_sim < SIM_THRESHOLD:
        if lang.startswith("en"):
            return "Sorry, I couldn’t find an answer for your question."
        elif lang.startswith("es"):
            return "Lo siento, no pude encontrar una respuesta a tu pregunta."
        else:
            return f"Não consegui responder essa pergunta: “{user_query}”."

    resposta_match = _respostas[idx]
    return f"{saudacao}{resposta_match}"