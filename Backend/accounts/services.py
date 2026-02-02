import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings
import logging

class SkalePayService:
    BASE_URL = "https://api.conta.skalepay.com.br/v1"

    @staticmethod
    def _get_auth():
        # Basic Auth: Username=SecretKey, Password="x" (conforme doc SkalePay)
        # A documentação SkalePay geralmente usa a Secret Key como 'username'
        # no Basic Auth e a senha vazia ou 'x'. Usamos senha vazia.
        secret_key = getattr(settings, 'SKALEPAY_SECRET_KEY', '')
        return HTTPBasicAuth(secret_key, '')

    @staticmethod
    def _get_headers():
        return {
            "accept": "application/json",
            "content-type": "application/json",
            "User-Agent": "PixLegal/1.0 (Django Backend)"
        }

    @staticmethod
    def gerar_pedido_deposito(usuario, valor_reais):
        """
        Gera QR Code para Entrada de dinheiro (Cash-in).
        Endpoint: /transactions
        """
        endpoint = f"{SkalePayService.BASE_URL}/transactions"
        try:
            amount_cents = int(float(valor_reais) * 100)
        except ValueError:
            raise Exception("Valor inválido para depósito.")

        payload = {
            "amount": amount_cents,
            "paymentMethod": "pix",
            "postbackUrl": f"{getattr(settings, 'WEBHOOK_URL_BASE', '')}/api/accounts/webhook/skalepay/",
            "items": [
                {
                    "title": "Creditos Plataforma",
                    "unitPrice": amount_cents,
                    "quantity": 1,
                    "tangible": False,
                    "externalRef": f"DEP-{usuario.id}"
                }
            ],
            "customer": {
                "name": getattr(usuario, 'nome_completo', None) or "Usuario Sem Nome",
                "email": getattr(usuario, 'email', None),
                "type": "individual",
                "document": {
                    "type": "cpf",
                    "number": getattr(usuario, 'cpf_cnpj', '').replace('.', '').replace('-', '')
                }
            },
            "metadata": {
                "usuario_id": str(getattr(usuario, 'id', '')),
                "ambiente": "producao" if "sk_live" in (getattr(settings, 'SKALEPAY_SECRET_KEY', '') or "") else "sandbox"
            }
        }

        try:
            print(f">>> [SKALEPAY] Enviando Request para: {endpoint}")
            response = requests.post(
                endpoint,
                json=payload,
                auth=SkalePayService._get_auth(),
                headers=SkalePayService._get_headers(),
                timeout=15
            )

            if response.status_code >= 400:
                logger.error(f"Erro SkalePay: {response.text}")
                raise Exception(f"Falha no Gateway: {response.status_code} - {response.text}")

            dados = response.json()
            pix_data = dados.get('pix', {})

            return {
                "transaction_id": dados.get('id'),
                "status": dados.get('status'),
                "qr_code": pix_data.get('qrcode'),
                "qr_code_url": pix_data.get('url'),
                "expiration": pix_data.get('expirationDate')
            }

        except Exception as e:
            logger.exception("Erro ao gerar depósito SkalePay")
            raise e

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