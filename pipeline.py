# pipeline.py

import re
from datetime import datetime
from langdetect import detect
from intent import detect_intent
from services import rota_service, faq_service, relatorio_service
from services.smalltalk_service import resposta_smalltalk
from prompt_builder import build_prompt
from llm import stream_response

INTENT_FUNCS = {
    "rota": rota_service.process_user_query,
    "faq_passageiro": faq_service.resposta_faq,
    "relatorio": relatorio_service.gerar_relatorio
}

# Patterns de smalltalk em pt/en/es
SAUDACOES_PT      = re.compile(r"\b(oi|ol[aá]|opa|eai|fala|bom dia|boa tarde|boa noite)\b", re.IGNORECASE)
AGRADECIMENTOS_PT = re.compile(r"\b(obrigad[oa]|valeu|brigad[oa])\b", re.IGNORECASE)
DESPEDIDAS_PT     = re.compile(r"\b(tchau|até mais|até logo)\b", re.IGNORECASE)

SAUDACOES_EN      = re.compile(r"\b(hello|hi|hey)\b", re.IGNORECASE)
AGRADECIMENTOS_EN = re.compile(r"\b(thank you|thanks)\b", re.IGNORECASE)
DESPEDIDAS_EN     = re.compile(r"\b(bye|goodbye)\b", re.IGNORECASE)

SAUDACOES_ES      = re.compile(r"\b(hola)\b", re.IGNORECASE)
AGRADECIMENTOS_ES = re.compile(r"\b(gracias)\b", re.IGNORECASE)
DESPEDIDAS_ES     = re.compile(r"\b(adiós|adios)\b", re.IGNORECASE)


async def process_user_input(user_input: str):
    texto = user_input.strip()

    #  SMALLTALK em Português
    if SAUDACOES_PT.search(texto):
        yield resposta_smalltalk("greeting", "pt")
        return
    if AGRADECIMENTOS_PT.search(texto):
        yield resposta_smalltalk("thanks", "pt")
        return
    if DESPEDIDAS_PT.search(texto):
        yield resposta_smalltalk("bye", "pt")
        return

    #  SMALLTALK em Inglês
    if SAUDACOES_EN.search(texto):
        yield resposta_smalltalk("greeting", "en")
        return
    if AGRADECIMENTOS_EN.search(texto):
        yield resposta_smalltalk("thanks", "en")
        return
    if DESPEDIDAS_EN.search(texto):
        yield resposta_smalltalk("bye", "en")
        return

    #  SMALLTALK em Espanhol
    if SAUDACOES_ES.search(texto):
        yield resposta_smalltalk("greeting", "es")
        return
    if AGRADECIMENTOS_ES.search(texto):
        yield resposta_smalltalk("thanks", "es")
        return
    if DESPEDIDAS_ES.search(texto):
        yield resposta_smalltalk("bye", "es")
        return

    # Caso funcional (rota, faq, relatório) ou fallback
    try:
        user_lang = detect(user_input)
    except:
        user_lang = "pt"

    intent = detect_intent(user_input)
    fn = INTENT_FUNCS.get(intent)

    if fn:
        resultado = fn(user_input)

        if intent == "faq_passageiro":
            context_obj = {"tipo": "faq", "texto_faq": resultado}
        elif intent == "rota":
            context_obj = {"tipo": "rota", "texto_rota": resultado}
        elif intent == "relatorio":
            agora = datetime.now().strftime("%d/%m/%Y %H:%M")
            context_obj = {
                "tipo": "relatorio",
                "titulo": f"Relatório - {agora.split(' ')[0]}",
                "data_hora": agora,
                "conteudo": resultado
            }
        else:
            context_obj = {"texto": resultado}

        prompt = build_prompt(context_obj, user_input)
        async for chunk in stream_response(prompt, user_lang):
            yield chunk
    else:
        # Fallback genérico (LLM lida com a frase curta ou sem intenção)
        context_obj = {"texto": "Desculpe, não entendi exatamente o que você quis dizer. Poderia reformular?"}
        prompt = build_prompt(context_obj, user_input)
        async for chunk in stream_response(prompt, user_lang):
            yield chunk