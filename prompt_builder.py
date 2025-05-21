# prompt_builder.py

import json
from langdetect import detect

# Mapeia código ISO (‘pt’, ‘en’, ‘es’) para nome legível
LANG_NAME = {
    "pt": "português",
    "en": "inglês",
    "es": "espanhol"
}

def build_prompt(contexto: dict, user_input: str) -> str:
    """
    Monta o prompt para a LLM, escolhendo e
    traduzindo o texto de sistema inteiro conforme o idioma detectado.
    """

    # 1) Detecta idioma do usuário (langdetect retorna 'pt', 'en', 'es', etc.)
    lang = detect(user_input)
    idioma_nome = LANG_NAME.get(lang, "português")  # padrão pt se não reconhecer

    tipo = contexto.get("tipo", None)

    # 2) Templates multilíngues para 'relatorio'
    if tipo == "relatorio":
        payload = json.dumps(contexto, ensure_ascii=False, indent=2)

        if lang == "en":
            return (
                f"You are Ceci, CCR’s report‐generation assistant.\n"
                f"The user wrote in {idioma_nome}. Reply **in the same language** ({idioma_nome}).\n"
                f"Generate a final report text using **only** the JSON below as context:\n\n"
                f"{payload}"
            )
        elif lang == "es":
            return (
                f"Eres Ceci, asistente de generación de informes de la CCR.\n"
                f"El usuario escribió en {idioma_nome}. Responde **en el mismo idioma** ({idioma_nome}).\n"
                f"Genera un texto de informe final utilizando **solo** el JSON a continuación como contexto:\n\n"
                f"{payload}"
            )
        else:  # português
            return (
                f"Você é a Ceci, assistente de geração de relatórios da CCR.\n"
                f"O usuário escreveu em {idioma_nome}. Responda **no mesmo idioma** ({idioma_nome}).\n"
                f"Gere um texto final de relatório **usando apenas** o JSON abaixo como contexto:\n\n"
                f"{payload}"
            )

    # 3) Templates multilíngues para 'rota'
    if tipo == "rota":
        texto_rota = contexto.get("texto_rota", "")

        if lang == "en":
            return (
                f"You are Ceci, public‐transport route assistant for São Paulo."
                f"\nThe user wrote in {idioma_nome}. Reply **in the same language** ({idioma_nome})."
                f"\nUse the route description below **exactly as provided**, without modifying any station names or order."
                f"\n\n{texto_rota}"
            )
        elif lang == "es":
            return (
                f"Eres Ceci, asistente de rutas del transporte público de São Paulo."
                f"\nEl usuario escribió en {idioma_nome}. Responde **en el mismo idioma** ({idioma_nome})."
                f"\nUtiliza la descripción de la ruta a continuación **exactamente como se proporcionó**, sin modificar nombres de estaciones o el orden."
                f"\n\n{texto_rota}"
            )
        else:  # português
            return (
                f"Você é a Ceci, assistente de rotas do transporte público de SP."
                f"\nO usuário escreveu em {idioma_nome}. Responda **no mesmo idioma** ({idioma_nome})."
                f"\nUse a descrição de rota abaixo **exatamente como fornecida**, sem alterar nomes de estações nem a ordem."
                f"\n\n{texto_rota}"
            )

    # 4) Templates multilíngues para 'faq'
    if tipo == "faq":
        texto_faq = contexto.get("texto_faq", "")

        if lang == "en":
            return (
                f"You are Ceci, passenger FAQ assistant.\n"
                f"The user wrote in {idioma_nome}. Reply **in the same language** ({idioma_nome}),\n"
                f"based **only** on the text below:\n\n"
                f"{texto_faq}"
            )
        elif lang == "es":
            return (
                f"Eres Ceci, asistente de FAQ para pasajeros.\n"
                f"El usuario escribió en {idioma_nome}. Responde **en el mismo idioma** ({idioma_nome}),\n"
                f"basándote **solo** en el texto a continuación:\n\n"
                f"{texto_faq}"
            )
        else:  # português
            return (
                f"Você é a Ceci, assistente de FAQ para passageiros.\n"
                f"O usuário escreveu em {idioma_nome}. Responda **no mesmo idioma** ({idioma_nome}),\n"
                f"baseando-se **apenas** no texto abaixo:\n\n"
                f"{texto_faq}"
            )

    # 5) Fallback genérico multilíngue (texto livre)
    texto = contexto.get("texto", "")

    if lang == "en":
        return (
            f"You are Ceci, CCR’s virtual assistant.\n"
            f"The user wrote in {idioma_nome}. Reply **in the same language** ({idioma_nome}), "
            f"in a clear and concise way:\n\n"
            f"{texto}"
        )
    elif lang == "es":
        return (
            f"Eres Ceci, asistente virtual de la CCR.\n"
            f"El usuario escribió en {idioma_nome}. Responde **en el mismo idioma** ({idioma_nome}), "
            f"de forma clara y objetiva:\n\n"
            f"{texto}"
        )
    else:  # português
        return (
            f"Você é a Ceci, assistente virtual da CCR.\n"
            f"O usuário escreveu em {idioma_nome}. Responda **no mesmo idioma** ({idioma_nome}) "
            f"de forma clara e objetiva:\n\n"
            f"{texto}"
        )
