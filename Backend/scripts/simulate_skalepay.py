import requests
import hmac
import hashlib
import json
import time

# CONFIGURAÇÃO
URL = 'http://localhost:8000/api/accounts/webhook/skalepay/'
SECRET_KEY = '123456'  # Tem que ser igual ao settings.py
USER_ID = 1            # ID do usuário que vai receber o depósito (garanta que existe no banco)

def enviar_webhook_teste():
    # 1. Gera um ID único para o teste (timestamp)
    tx_id = f"skale_test_{int(time.time())}"
    
    payload = {
        "transaction_id": tx_id,
        "status": "PAID",
        "amount": 100.00,
        "customer_custom_id": USER_ID,
        "created_at": "2026-01-07T19:00:00Z"
    }
    
    payload_json = json.dumps(payload)
    
    # 2. Gera a Assinatura (HMAC SHA256)
    signature = hmac.new(
        SECRET_KEY.encode('utf-8'),
        payload_json.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    headers = {
        'Content-Type': 'application/json',
        'X-SkalePay-Signature': signature
    }
    
    print(f"📡 Enviando Webhook Simulado...")
    print(f"ID Transação: {tx_id}")
    print(f"Payload: {payload_json}")
    
    try:
        response = requests.post(URL, data=payload_json, headers=headers)
        print(f"\n✅ Status Code: {response.status_code}")
        print(f"📄 Resposta: {response.text}")
    except Exception as e:
        print(f"\n❌ Erro de conexão: {e}")
        print("Certifique-se que o servidor django está rodando (python manage.py runserver)")

if __name__ == "__main__":
    enviar_webhook_teste()