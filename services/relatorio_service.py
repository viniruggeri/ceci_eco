# relatorio_service.py
import datetime

def gerar_relatorio(descricao: str) -> dict:
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    return {
        "tipo": "relatorio",
        "titulo": f"Relatório de Incidente - {now.split(' ')[0]}",
        "data_hora": now,
        "contexto": descricao
    }
