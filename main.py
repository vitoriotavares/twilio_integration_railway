from fastapi import FastAPI, Request
import requests
from twilio.rest import Client
import os

app = FastAPI()

# Configurações via variáveis de ambiente
LANGFLOW_URL = os.getenv("LANGFLOW_URL", "https://langflow-staging-41e0.up.railway.app/api/v1/run/1401a05a-4dcb-41d5-81d3-4c483bd02f70")
LANGFLOW_API_KEY = os.getenv("LANGFLOW_API_KEY", "sk-Nfb2msC-PCgjJXVw__a_rhikbclR5mcoVAF_T5UMcCc")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

# Cliente Twilio
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.form()
    mensagem = data.get("Body", "")
    remetente = data.get("From", "")

    headers = {
        'Content-Type': 'application/json',
        'x-api-key': LANGFLOW_API_KEY
    }
    
    payload = {
        "input_value": mensagem,
        "output_type": "chat",
        "input_type": "chat",
        "tweaks": {
            "ChatInput-UkCgz": {},
            "GroqModel-UQb3u": {},
            "ChatOutput-OsWrb": {}
        }
    }

    try:
        resposta = requests.post(
            LANGFLOW_URL,
            headers=headers,
            json=payload,
            params={"stream": "false"}
        )
        resposta_ia = resposta.json().get("output", "Desculpe, não entendi.")
        
        twilio_client.messages.create(
            body=resposta_ia,
            from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
            to=remetente
        )
        
        return {"status": "success"}
    
    except Exception as e:
        print(f"Erro: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.get("/")
async def root():
    return {"status": "running"}
