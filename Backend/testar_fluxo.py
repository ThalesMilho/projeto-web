import requests
import hmac
import hashlib
import json

# --- CONFIGURAÇÕES ---
BASE_URL = "http://127.0.0.1:8000/api/accounts"
# ATENÇÃO: Se você configurou uma SECRET_KEY no settings.py, coloque a mesma aqui!
# Se não configurou, deixe vazio ou 'teste123' (o código que fizemos aceita vazio em dev)
SKALEPAY_SECRET = "teste123" 

def print_step(msg):
    print(f"\n{'='*50}\n🚀 {msg}\n{'='*50}")

def main():
    # 1. REGISTRO
    print_step("1. Registrando Usuário de Teste...")
    cpf = "12345678901" # CPF Fictício
    payload_registro = {
        "nome_completo": "Investidor Teste",
        "cpf_cnpj": 31817572091,
        "email": "teste@exemplo.com",
        "password": "senha_segura_123",
        "phone": "62999999999"
    }
    
    # Tenta registrar (se já existir, segue pro login)
    resp = requests.post(f"{BASE_URL}/register/", json=payload_registro)
    if resp.status_code == 201:
        print("✅ Usuário Criado!")
    elif resp.status_code == 400 and "já existe" in resp.text:
        print("ℹ️ Usuário já existia, seguindo para login...")
    else:
        print(f"❌ Erro no Registro: {resp.text}")

    # 2. LOGIN
    print_step("2. Fazendo Login...")
    resp = requests.post(f"{BASE_URL}/login/", json={
        "cpf_cnpj": 31817572091 ,
        "password": "senha_segura_123"
    })
    
    if resp.status_code != 200:
        print(f"❌ Falha no Login: {resp.text}")
        return

    tokens = resp.json()
    access_token = tokens['access']
    headers = {"Authorization": f"Bearer {access_token}"}
    print(f"✅ Login OK! Token capturado.")

    # 3. DASHBOARD INICIAL
    print_step("3. Consultando Dashboard (Antes do Depósito)...")
    resp = requests.get(f"{BASE_URL}/dashboard/", headers=headers)
    if resp.status_code == 200:
        dados = resp.json()
        print(f"📊 FTDs Hoje: {dados['hoje']['ftds_qtd']}")
        print(f"💰 Depositos Hoje: R$ {dados['hoje']['depositos']}")
    else:
        print(f"❌ Erro Dashboard: {resp.text}")

    # 4. GERAR DEPÓSITO
    print_step("4. Gerando Intenção de Depósito (R$ 50,00)...")
    valor_deposito = 50.00
    resp = requests.post(f"{BASE_URL}/depositar/", json={"valor": valor_deposito}, headers=headers)
    
    if resp.status_code == 200:
        dados_dep = resp.json()
        id_transacao = dados_dep['id_transacao']
        print(f"✅ QR Code Gerado! ID da Transação: {id_transacao}")
    else:
        print(f"❌ Erro ao Gerar Depósito: {resp.text}")
        return

    # 5. SIMULAR WEBHOOK (O Pulo do Gato)
    print_step("5. Simulando Callback da SkalePay (Webhook)...")
    
    # Monta o payload que a SkalePay enviaria
    webhook_payload = {
        "transaction_id": id_transacao,
        "status": "PAID",
        "amount": valor_deposito,
        "customer_custom_id": 1 # ID fictício, nosso sistema busca pelo id_transacao
    }
    payload_json = json.dumps(webhook_payload).encode('utf-8')

    # Gera a Assinatura de Segurança (HMAC)
    # Isso prova que nosso sistema de segurança funciona!
    signature = hmac.new(
        SKALEPAY_SECRET.encode('utf-8'), 
        payload_json, 
        hashlib.sha256
    ).hexdigest()

    headers_webhook = {
        "Content-Type": "application/json",
        "X-SkalePay-Signature": signature
    }

    # Dispara contra nossa própria API (sem autenticação, pois é webhook)
    resp = requests.post(
        f"{BASE_URL}/webhook/skalepay/", 
        data=payload_json, 
        headers=headers_webhook
    )

    if resp.status_code == 200:
        print("✅ Webhook Recebido e Processado com Sucesso!")
    else:
        print(f"❌ Webhook Falhou (Código {resp.status_code}): {resp.text}")
        print("Dica: Verifique se SKALEPAY_SECRET_KEY no .env bate com o script.")

    # 6. VERIFICAR SALDO E DASHBOARD
    print_step("6. Verificando se o dinheiro caiu...")
    resp = requests.get(f"{BASE_URL}/dashboard/", headers=headers)
    dados = resp.json()
    print(f"💰 Depositos Hoje Agora: R$ {dados['hoje']['depositos']} (Deveria ser 50.00)")
    print(f"📈 FTDs Hoje: {dados['hoje']['ftds_qtd']} (Deveria ser 1)")

    # 7. SOLICITAR SAQUE
    print_step("7. Testando Saque de R$ 10,00...")
    resp = requests.post(f"{BASE_URL}/saque/", json={
        "valor": 10.00,
        "chave_pix": "minha@chave.pix"
    }, headers=headers)

    if resp.status_code == 200:
        print(f"✅ Saque Realizado! {resp.json()['mensagem']}")
        print(f"📉 Novo Saldo: {resp.json()['novo_saldo']}")
    else:
        print(f"❌ Falha no Saque: {resp.json()}")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERRO CRÍTICO: O servidor não está rodando!")
        print("👉 Rode 'python manage.py runserver' em outro terminal antes de testar.")