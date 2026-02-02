import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings
import logging

class SkalePayService:
    BASE_URL = "https://api.conta.skalepay.com.br/v1"

    @staticmethod
    def _get_auth():
        # Basic Auth: Username=SecretKey, Password="x" (conforme doc SkalePay)
        secret_key = getattr(settings, 'SKALEPAY_SECRET_KEY', '')
        # Adicionamos o 'x' conforme a doc da SkalePay para validar o Basic Auth
        return HTTPBasicAuth(secret_key, 'x')

    @staticmethod
    def _get_headers():
        # Configuração "Bypass WAF" sugerida pelo Pleno
        return {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
        }

    @staticmethod
    def gerar_pedido_deposito(usuario, valor_reais):
        """
        Gera QR Code para Entrada de dinheiro (Cash-in).
        Endpoint: /transactions
        """
        endpoint = f"{SkalePayService.BASE_URL}/transactions"
        amount_cents = int(float(valor_reais) * 100) # R$ 10,00 -> 1000

        payload = {
            "amount": amount_cents,
            "paymentMethod": "pix",
            "postbackUrl": f"{getattr(settings, 'WEBHOOK_URL_BASE', '')}/api/accounts/webhook/skalepay/",
            "items": [{
                "title": "Credito Plataforma",
                "unit_price": amount_cents,
                "quantity": 1,
                "tangible": False
            }],
            "customer": {
                "name": usuario.nome_completo[:100], # Limita caracteres por segurança
                "email": usuario.email or "cliente@plataforma.com",
                "type": "individual",
                "document": {
                    "type": "cpf",
                    "number": usuario.cpf_cnpj.replace('.', '').replace('-', '') # Remove pontuação
                }
            }
        }

        try:
            response = requests.post(
                endpoint,
                json=payload,
                auth=SkalePayService._get_auth(),
                headers=SkalePayService._get_headers()
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro SkalePay (Depósito): {e.response.text if e.response else str(e)}")

    @staticmethod
    def solicitar_saque_pix(usuario, valor_reais, chave_pix, referencia_interna):
        """
        Envia Pix REAL para o usuário (Cash-out).
        Endpoint: /transfers
        """
        endpoint = f"{SkalePayService.BASE_URL}/transfers"

        # Conversão Decimal -> Centavos (Evita erro de ponto flutuante)
        amount_cents = int(valor_reais * 100)

        payload = {
            "amount": amount_cents,
            "pixKey": str(chave_pix),
            "externalRef": str(referencia_interna),
            "description": "Saque Plataforma",
            "postbackUrl": f"{getattr(settings, 'WEBHOOK_URL_BASE', '')}/api/accounts/webhook/skalepay/"
        }

        # Timeout maior (25s) para dar tempo do banco processar, mas não infinito
        response = requests.post(
            endpoint,
            json=payload,
            auth=SkalePayService._get_auth(),
            headers=SkalePayService._get_headers(),
            timeout=25
        )
        # Se der erro, lançamos uma Exceção com o TEXTO da resposta (o JSON explicativo)
        if response.status_code >= 400:
            msg_erro = f"Erro SkalePay (Saque): {response.status_code} {response.reason} - {response.text}"
            logger.error(msg_erro)
            raise Exception(msg_erro)

        return response.json()

    @staticmethod
    def consultar_saldo_banca():
        """
        Consulta o saldo disponível na conta da SkalePay antes de tentar pagar.
        Doc: GET /v1/balance/available
        """
        endpoint = f"{SkalePayService.BASE_URL}/balance/available"
        
        try:
            response = requests.get(
                endpoint,
                auth=SkalePayService._get_auth(),
                headers={"Accept": "application/json"},
                timeout=5
            )
            response.raise_for_status()
            # Conversão segura: API retorna centavos (int), nós usamos float/decimal
            return float(response.json().get('availableAmount', 0)) / 100.0
        except Exception:
            return None

    @staticmethod
    def consultar_status_transferencia(id_transferencia_externo):
        """
        Verifica o status real de uma transferência na SkalePay.
        Doc: GET /v1/transfers/{id}
        """
        endpoint = f"{SkalePayService.BASE_URL}/transfers/{id_transferencia_externo}"
        
        try:
            response = requests.get(
                endpoint,
                auth=SkalePayService._get_auth(),
                headers={"Accept": "application/json"},
                timeout=15
            )
            if response.status_code == 404:
                return "NAO_ENCONTRADO"
                
            response.raise_for_status()
            return response.json().get('status')
            
        except requests.exceptions.RequestException:
            return "ERRO_COMUNICACAO"

# Module logger
logger = logging.getLogger(__name__)