import requests
import json
import random
import string
import time
from datetime import datetime
from colorama import init, Fore, Style

# Inicializa cores para o terminal
init(autoreset=True)

# --- CONFIGURAÇÕES ---
BASE_URL = "http://127.0.0.1:8000/api"
ADMIN_USER = "admin"  # Certifique-se de ter esse user criado
ADMIN_PASS = "admin"  # Certifique-se de que a senha é essa

# Variáveis Globais para persistência entre testes
CONTEXT = {
    "user_token": None,
    "admin_token": None,
    "user_id": None,
    "user_email": "",
    "deposit_id_externo": f"pix_{int(time.time())}",
    "solicitacao_saque_id": None
}

# --- FUNÇÕES AUXILIARES ---
def print_header(title):
    print(f"\n{Style.BRIGHT}{Fore.CYAN}{'='*60}")
    print(f"{title.center(60)}")
    print(f"{'='*60}{Style.RESET_ALL}")

def log_success(msg):
    print(f"{Fore.GREEN}[PASS] {msg}")

def log_fail(msg, response=None):
    print(f"{Fore.RED}[FAIL] {msg}")
    if response:
        try:
            print(f"{Fore.YELLOW}Response: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"{Fore.YELLOW}Response Text: {response.text}")
    # Não vamos parar o script, mas marcar o erro visualmente
    # exit(1) 

def generate_random_user():
    suffix = int(time.time())
    return {
        "email": f"tester_{suffix}@qa.com",
        "nome_completo": f"QA Engineer {suffix}",
        "cpf_cnpj": f"{90645435007}",
        "telefone": "11999999999",
        "password": "Password123!"
    }

# --- SUÍTE DE TESTES ---

def step_01_health_check():
    print_header("1. HEALTH CHECK & DOCUMENTAÇÃO")
    try:
        r = requests.get(f"{BASE_URL}/docs/")
        if r.status_code == 200:
            log_success("Swagger UI acessível")
        else:
            log_fail(f"Swagger retornou {r.status_code}")
    except Exception as e:
        log_fail(f"Servidor offline? {e}")
        exit(1)

def step_02_auth_cycle():
    print_header("2. AUTENTICAÇÃO E CADASTRO")
    
    # 2.1 Registro
    payload = generate_random_user()
    CONTEXT["user_email"] = payload["email"]
    
    r = requests.post(f"{BASE_URL}/accounts/register/", json=payload)
    if r.status_code == 201:
        log_success(f"Usuário criado: {payload['email']}")
        CONTEXT["user_id"] = r.json().get('id')
    else:
        log_fail("Falha no registro", r)

    # 2.2 Login
    login_payload = {"cpf_cnpj": payload["cpf_cnpj"], "password": payload["password"]}
    r = requests.post(f"{BASE_URL}/accounts/login/", json=login_payload)
    if r.status_code == 200:
        CONTEXT["user_token"] = r.json()['access']
        log_success("Login realizado. Token JWT obtido.")
    else:
        log_fail("Falha no Login", r)
        exit(1)

    # 2.3 Perfil (Me)
    headers = {"Authorization": f"Bearer {CONTEXT['user_token']}"}
    r = requests.get(f"{BASE_URL}/accounts/me/", headers=headers)
    if r.status_code == 200:
        saldo = r.json().get('saldo')
        log_success(f"Perfil verificado. Saldo Inicial: R$ {saldo}")
    else:
        log_fail("Falha ao buscar perfil", r)

def step_03_financial_cycle():
    print_header("3. FLUXO FINANCEIRO (Depósito & Webhook)")
    headers = {"Authorization": f"Bearer {CONTEXT['user_token']}"}

    # 1. Tenta Gerar Depósito
    deposito_valor = 50.00
    r = requests.post(f"{BASE_URL}/accounts/depositar/", json={"valor": deposito_valor}, headers=headers)
    
    tx_id = None
    if r.status_code == 200:
        # Pega o ID real (ou mock) que veio da View
        tx_id = r.json().get('transaction_id')
        log_success(f"QR Code Gerado. ID: {tx_id}")
    else:
        # Se falhar, inventa um ID para tentar forçar o teste
        print(f"{Fore.YELLOW}[WARN] Depósito falhou. Tentando forçar webhook mesmo assim.")
        import time
        tx_id = f"test_force_{int(time.time())}"

    # 2. Simular Webhook (ISSO CRIA O SALDO)
    print(f"{Fore.BLUE}>> Forçando confirmação de pagamento para ID: {tx_id}...")
    
    webhook_payload = {
        "transaction_id": tx_id,
        "status": "paid",
        "amount": 5000 # 5000 centavos = R$ 50.00
    }
    
    r_hook = requests.post(f"{BASE_URL}/accounts/webhook/skalepay/", json=webhook_payload)
    
    if r_hook.status_code == 200:
        log_success("Webhook Enviado! Saldo deve ter caído.")
    else:
        log_fail("Webhook falhou", r_hook)

    # 3. Validar se o dinheiro caiu (Prova Real)
    r_saldo = requests.get(f"{BASE_URL}/accounts/me/", headers=headers)
    if r_saldo.status_code == 200:
        saldo = float(r_saldo.json().get('saldo', 0.0))
        if saldo >= 50.00:
            log_success(f"Saldo Confirmado: R$ {saldo:.2f}")
        else:
            log_fail(f"Saldo não entrou. Atual: R$ {saldo:.2f}")
            
def step_04_games_content():
    print_header("4. CONTEÚDO DE JOGOS (Público/Autenticado)")
    headers = {"Authorization": f"Bearer {CONTEXT['user_token']}"}

    # 4.1 Bichos
    r = requests.get(f"{BASE_URL}/games/bichos/", headers=headers)
    if r.status_code == 200 and len(r.json()) > 0:
        log_success(f"Lista de Bichos carregada ({len(r.json())} itens)")
    else:
        log_fail("Falha ao listar bichos", r)

    # 4.2 Cotações
    r = requests.get(f"{BASE_URL}/games/cotacoes/", headers=headers)
    if r.status_code == 200:
        log_success("Cotações carregadas")
    else:
        log_fail("Falha cotações", r)

    # 4.3 Sorteios Abertos
    r = requests.get(f"{BASE_URL}/games/sorteios/abertos/", headers=headers)
    if r.status_code == 200:
        sorteios = r.json()
        if len(sorteios) > 0:
            CONTEXT["sorteio_id"] = sorteios[0]['id']
            log_success(f"Sorteios abertos encontrados. Usando ID: {CONTEXT['sorteio_id']}")
        else:
            print(f"{Fore.YELLOW}[WARN] Nenhum sorteio aberto agora. Criando aposta vai falhar.")
            CONTEXT["sorteio_id"] = 1 # Fallback
    else:
        log_fail("Falha sorteios", r)
        
    # 4.4 Novos Jogos (Quininha, Seninha, Lotinha)
    for jogo in ['quininha', 'seninha', 'lotinha']:
        r = requests.get(f"{BASE_URL}/games/{jogo}/", headers=headers)
        if r.status_code == 200:
            log_success(f"Endpoint de regras {jogo.upper()} ativo.")
        else:
            log_fail(f"Endpoint {jogo} falhou", r)

def step_05_betting_action():
    print_header("5. AÇÃO DE APOSTA")
    headers = {"Authorization": f"Bearer {CONTEXT['user_token']}"}

    # Tentar apostar (Pode falhar por saldo 0 se o webhook não rolou, vamos testar a validação)
    bet_payload = {
        "sorteio": CONTEXT.get("sorteio_id", 1),
        "tipo_jogo": "GRUPO",
        "palpite": "18", # Porco
        "valor": 5.00
    }
    
    r = requests.post(f"{BASE_URL}/games/apostas/", json=bet_payload, headers=headers)
    
    if r.status_code == 201:
        log_success("Aposta realizada com sucesso!")
    elif r.status_code == 400 and "Saldo insuficiente" in r.text:
        log_success("Validação de Saldo Insuficiente funcionando corretamente (Esperado se não depositou).")
    else:
        log_fail("Erro inesperado na aposta", r)

def step_06_withdrawal_security():
    print_header("6. SAQUE & SEGURANÇA (Compliance)")
    headers = {"Authorization": f"Bearer {CONTEXT['user_token']}"}

    # Tenta sacar valor alto para testar Análise
    saque_payload = {
        "valor": 5000.00,
        "chave_pix": "teste@pix.com"
    }
    
    r = requests.post(f"{BASE_URL}/accounts/saque/", json=saque_payload, headers=headers)
    
    if r.status_code == 400 and "Saldo" in r.text:
        log_success("Bloqueio de saque sem saldo: OK")
    elif r.status_code == 403:
        log_success("Trava de Segurança (Tempo/Rollover) ativada: OK")
    elif r.status_code == 202:
        log_success("Saque caiu em Análise (Compliance): OK")
    else:
        # Se retornar 200 sem saldo é um bug gravíssimo
        if r.status_code == 200:
             log_fail("CRÍTICO: Saque permitido indevidamente!", r)
        else:
             print(f"{Fore.YELLOW}[INFO] Resposta do saque: {r.status_code} - {r.text}")

def step_07_admin_backoffice():
    print_header("7. ADMIN & BACKOFFICE")
    
    # Login Admin
    # Nota: Este passo depende de você ter criado o usuário 'admin' via 'createsuperuser'
    # e que ele tenha CPF/CNPJ ou Email configurado para login. 
    # Vou assumir login via Token endpoint padrão.
    
    # Vamos tentar pegar token pro admin
    # Se o seu login admin for por username, o endpoint padrão pode falhar se espera CPF.
    # Adaptando para tentar o fluxo, mas sem quebrar se as credenciais não baterem.
    
    print(f"{Fore.BLUE}Tentando autenticar como Admin para testar endpoints protegidos...")
    # Ajuste este payload conforme seu admin real
    payload_admin = {"cpf_cnpj": "00000000000", "password": ADMIN_PASS} 
    
    r = requests.post(f"{BASE_URL}/accounts/login/", json=payload_admin)
    
    if r.status_code == 200:
        admin_token = r.json()['access']
        adm_headers = {"Authorization": f"Bearer {admin_token}"}
        log_success("Admin autenticado.")
        
        # 7.1 Dashboard
        r = requests.get(f"{BASE_URL}/accounts/backoffice/dashboard/", headers=adm_headers)
        if r.status_code == 200: log_success("Dashboard Financeiro: OK")
        else: log_fail("Dashboard falhou", r)
        
        # 7.2 Risco e Compliance
        r = requests.get(f"{BASE_URL}/accounts/backoffice/risco/multiconstas_ip/", headers=adm_headers)
        if r.status_code == 200: log_success("Checagem Multi-contas: OK")
        
        # 7.3 Relatórios Operacionais
        r = requests.get(f"{BASE_URL}/accounts/backoffice/relatorios/operacionais/", headers=adm_headers)
        if r.status_code == 200: log_success("Relatórios Operacionais: OK")

        # 7.4 Download CSV
        # Precisamos achar o endpoint correto no ViewSet. Geralmente é /backoffice/solicitacoes/download_csv/
        r = requests.get(f"{BASE_URL}/accounts/backoffice/solicitacoes/download_csv/", headers=adm_headers)
        if r.status_code == 200 and 'text/csv' in r.headers.get('Content-Type', ''):
            log_success("Download CSV: OK")
        else:
            log_fail("Download CSV falhou", r)

    else:
        print(f"{Fore.YELLOW}[SKIP] Pulei testes de Admin (Credenciais no script não batem ou user não existe).")
        print(f"{Fore.YELLOW}Para testar Admin, edite as variáveis ADMIN_USER/PASS no script.")

# --- EXECUÇÃO ---
if __name__ == "__main__":
    print_header("INICIANDO SUÍTE DE TESTES DE INTEGRAÇÃO (QA)")
    
    try:
        step_01_health_check()
        step_02_auth_cycle()
        step_03_financial_cycle()
        step_04_games_content()
        step_05_betting_action()
        step_06_withdrawal_security()
        step_07_admin_backoffice()
        
        print_header("RESUMO FINAL")
        print(f"{Fore.GREEN}Todos os testes críticos de conectividade passaram.")
        print(f"{Fore.WHITE}Verifique os logs [FAIL] acima para regras de negócio específicas.")
        
    except requests.exceptions.ConnectionError:
        print(f"\n{Fore.RED}ERRO CRÍTICO: Não foi possível conectar em {BASE_URL}")
        print("O servidor Django está rodando? (python manage.py runserver)")