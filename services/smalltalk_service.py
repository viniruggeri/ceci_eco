import random

def resposta_smalltalk(intent: str, lang: str = "pt") -> str:
    """
    Retorna uma resposta fixa para intenções de saudação, agradecimento, despedida etc.,
    com base no idioma ('pt', 'en', 'es').
    """
    respostas = {
        "pt": {
            "greeting": [
                "Oi! Como posso ajudar você hoje?",
                "Olá! Em que posso ajudar?",
                "Oi, tudo bem? Conte comigo para o que precisar sobre transporte em SP."
            ],
            "thanks": [
                "De nada! Qualquer coisa, estou aqui.",
                "Imagina! Precisando de outra coisa, só me chamar.",
                "Por nada! Fico feliz em ajudar."
            ],
            "bye": [
                "Até mais! Volte quando quiser ajuda.",
                "Tchau! Qualquer dúvida, é só chamar.",
                "Foi um prazer ajudar. Até logo!"
            ],
            "fallback": [
                "Desculpe, não entendi direito. Poderia reformular?",
                "Ops, não captei. Pode tentar de novo, por favor?",
                "Não consegui entender. Quer dizer de outra forma?"
            ]
        },
        "en": {
            "greeting": [
                "Hi! How can I help you today?",
                "Hello! Need any help with São Paulo's public transport?",
                "Hey there! I'm here to assist you with anything you need."
            ],
            "thanks": [
                "You're welcome!",
                "No problem! Let me know if you need anything else.",
                "Glad I could help!"
            ],
            "bye": [
                "Goodbye! Come back whenever you need help.",
                "See you later! Take care.",
                "It was a pleasure to help. Bye for now!"
            ],
            "fallback": [
                "Sorry, I didn't quite understand. Could you rephrase that?",
                "Oops, I missed that. Mind trying again?",
                "I couldn't catch that. Can you say it differently?"
            ]
        },
        "es": {
            "greeting": [
                "¡Hola! ¿En qué puedo ayudarte hoy?",
                "¡Buenas! ¿Necesitas ayuda con el transporte público de São Paulo?",
                "¡Hola! Estoy aquí para ayudarte con lo que necesites."
            ],
            "thanks": [
                "¡De nada!",
                "No hay problema, cualquier cosa aquí estoy.",
                "¡Con gusto! Me alegra poder ayudarte."
            ],
            "bye": [
                "¡Hasta luego! Vuelve cuando necesites ayuda.",
                "¡Adiós! Estoy aquí si necesitas algo más.",
                "Un placer ayudarte. ¡Nos vemos!"
            ],
            "fallback": [
                "Lo siento, no entendí bien. ¿Puedes reformularlo?",
                "Ups, no capté eso. ¿Podrías repetirlo?",
                "No logré entender. ¿Puedes decirlo de otra manera?"
            ]
        }
    }

    # Usa "pt" como idioma padrão se lang inválido
    idioma = lang if lang in respostas else "pt"
    opções = respostas[idioma].get(intent, respostas[idioma]["fallback"])
    return random.choice(opções)
