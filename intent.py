# intent.py

import re

# → Padrões de smalltalk (saudação, agradecimento, despedida) em PT, EN e ES
SMALLTALK_PATTERNS = {
    "greeting": [
        # Português
        r"\b(oi|ol[áa]|opa|eai|fala|bom dia|boa tarde|boa noite)\b",
        # Inglês
        r"\b(hello|hi|hey)\b",
        # Espanhol
        r"\b(hola)\b"
    ],
    "thanks": [
        # Português
        r"\b(obrigad[oa]|valeu|brigad[oa])\b",
        # Inglês
        r"\b(thank you|thanks)\b",
        # Espanhol
        r"\b(gracias)\b"
    ],
    "bye": [
        # Português
        r"\b(tchau|até mais|até logo)\b",
        # Inglês
        r"\b(bye|goodbye)\b",
        # Espanhol
        r"\b(adiós|adios)\b"
    ]
}

# → Padrões de intenções funcional (tudo em PT, mas se quiser adicionar EN/ES, inclua sinônimos)
FUNCTIONAL_PATTERNS = {
    "rota": [
        r"\brota\b",
        r"\bcomo chegar\b",
        r"\bcaminho\b",
        r"\bir até\b",
        # Expressões em inglês/espanhol 
        r"\broute\b",
        r"\bget to\b",
        r"\bcomogetagallego/??"  # se quiser suportar “¿Cómo…” em espanhol
    ],
    "faq_passageiro": [
        r"\bfaq\b",
        r"\binformação\b",
        r"\bduvida\b",
        r"\bpergunta\b",
        # Inglês
        r"\bquestion\b",
        r"\binfo\b",
        # Espanhol
        r"\bduda\b",
        r"\bpregunta\b"
    ],
    "relatorio": [
        r"\brelatório\b",
        r"\bdados\b",
        r"\bestatística\b",
        # Inglês
        r"\breport\b",
        r"\bstatistics\b",
        # Espanhol
        r"\binforme\b",
        r"\bestadísticas\b"
    ]
}

def detect_intent(user_input: str) -> str:
    """
    Retorna uma das seguintes strings:
    - "greeting", "thanks", "bye"
    - "rota", "faq_passageiro", "relatorio"
    - "fallback" (quando não achar nenhum padrão)
    """

    text = user_input.lower()

    # 1) Verifica SMALLTALK (saudação, agradecimento, despedida)
    for intent, patterns in SMALLTALK_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, text, re.IGNORECASE):
                # Retorna logo no primeiro match
                return intent

    # 2) Verifica INTENÇÕES FUNCIONAIS (rota, faq_passageiro, relatorio)
    for intent, patterns in FUNCTIONAL_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, text, re.IGNORECASE):
                return intent

    # 3) Se nada bateu, fallback
    return "fallback"