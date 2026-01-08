import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings

class SkalePayService:
    BASE_URL = "https://api.conta.skalepay.com.br/v1"

    @staticmethod
    def _get_auth():
        # Basic Auth: Username=SecretKey, Password=""
        secret_key = getattr(settings, 'SKALEPAY_SECRET_KEY', '')
        return HTTPBasicAuth(secret_key, '')

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
            "payment_method": "pix",
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
                headers={"Content-Type": "application/json"}
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
        amount_cents = int(float(valor_reais) * 100)

        payload = {
            "amount": amount_cents,
            "pixKey": chave_pix,
            "externalRef": str(referencia_interna) # Envia nosso ID para rastreio
        }

        try:
            response = requests.post(
                endpoint, 
                json=payload, 
                auth=SkalePayService._get_auth(),
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            # Se o erro for "Saldo Insuficiente na SkalePay", o usuário receberá o aviso
            raise Exception(f"Erro SkalePay (Saque): {e.response.text if e.response else str(e)}")