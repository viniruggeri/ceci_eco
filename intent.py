# intent.py

import re

# → Padrões de smalltalk (saudação, agradecimento, despedida) em PT, EN e ES
SMALLTALK_PATTERNS = {
    "greeting": [
        # Português
        r"\b(oi|ol[áa]|opa|eai|fala|bom dia|boa tarde|boa noite|saudações)\b",
        # Inglês
        r"\b(hello|hi|hey|good morning|good afternoon|good evening)\b",
        # Espanhol
        r"\b(hola|buenos días|buenas tardes|buenas noches)\b"
    ],
    "thanks": [
        # Português
        r"\b(obrigad[oa]|valeu|brigad[oa]|agradecido|obrigadíssimo)\b",
        # Inglês
        r"\b(thank you|thanks|appreciate|much obliged)\b",
        # Espanhol
        r"\b(gracias|muchas gracias|te lo agradezco)\b"
    ],
    "bye": [
        # Português
        r"\b(tchau|até mais|até logo|falou|falou e até)\b",
        # Inglês
        r"\b(bye|goodbye|see you|see ya)\b",
        # Espanhol
        r"\b(adiós|adios|hasta luego|nos vemos)\b"
    ]
}

# → Padrões de intenções funcionais (rota, faq_passageiro, relatorio)
FUNCTIONAL_PATTERNS = {
    "rota": [
        # Português
        r"\brota\b",
        r"\bcomo chegar\b",
        r"\bcaminho\b",
        r"\bir até\b",
        r"\bdireção\b",
        r"\bchegar em\b",
        r"\bcomo vou\b",
        # Inglês
        r"\broute\b",
        r"\bdirections\b",
        r"\bget to\b",
        r"\bhow to go\b",
        r"\bway to\b",
        # Espanhol
        r"\bruta\b",
        r"\bllegar a\b",
        r"\bcómo llegar\b",
        r"\bcómo voy\b"
    ],
    "faq_passageiro": [
        # Português
        r"\bfaq\b",
        r"\binformação\b",
        r"\bduvid[ao]\b",
        r"\bpergunta\b",
        r"\bpreciso saber\b",
        r"\bcomo faço\b",
        r"\bcomo funciona\b",
        r"\bonde posso\b",
        # Inglês
        r"\b(question|questions)\b",
        r"\binfo\b",
        r"\bhow do i\b",
        r"\bwhere can i\b",
        r"\bcan i\b",
        r"\bcan we\b",
        r"\bhelp me\b",
        # Espanhol
        r"\bduda\b",
        r"\bpregunta\b",
        r"\bcómo puedo\b",
        r"\bdónde puedo\b"
    ],
    "relatorio": [
        # Português
        r"\brelatório\b",
        r"\bdados\b",
        r"\bestatística\b",
        r"\bmétricas\b",
        r"\binforme\b",
        # Inglês
        r"\breport\b",
        r"\bstatistics\b",
        r"\bdata\b",
        r"\bmetrics\b",
        r"\bgenerate report\b",
        # Espanhol
        r"\binforme\b",
        r"\bestadísticas\b",
        r"\bdatos\b",
        r"\bmetrics\b"
    ]
}


def detect_intent(user_input: str) -> str:
    """
    Retorna uma das seguintes strings:
    - "greeting", "thanks", "bye"
    - "rota", "faq_passageiro", "relatorio"
    - "fallback" (quando não encontrar nenhum padrão)
    """

    text = user_input.lower()

    # 1) Verifica SMALLTALK (saudações, agradecimentos, despedidas)
    for intent, patterns in SMALLTALK_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, text, re.IGNORECASE):
                return intent  # "greeting", "thanks" ou "bye"

    # 2) Verifica INTENÇÕES FUNCIONAIS (rota, faq_passageiro, relatorio)
    for intent, patterns in FUNCTIONAL_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, text, re.IGNORECASE):
                return intent

    # 3) Se nada bateu, retorna “fallback”
    return "fallback"
