import os
import requests

# Tenta pegar a chave do ambiente
chave = os.getenv('SKALEPAY_SECRET_KEY')
print(f"Chave detectada: {chave}")

if not chave:
    print("ERRO: SKALEPAY_SECRET_KEY não encontrada no ambiente.")
    exit(1)

endpoint = "https://api.conta.skalepay.com.br/v1/balance"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
auth = (chave, "")

print(f"Conectando em: {endpoint}")
try:
    response = requests.get(endpoint, auth=auth, headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Corpo: {response.text}")
except Exception as e:
    print(f"Erro: {e}")