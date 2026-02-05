import logging
import requests
from decimal import Decimal
from rest_framework.exceptions import ValidationError

# Gateway client wrapper (new)
from ..gateways.skalepay import SkalePayClient, SkalePayError

class SkalePayService:
    """
    Service layer for SkalePay operations.
    Uses SkalePayClient for all API communications.
    """

    @staticmethod
    def gerar_pedido_deposito(usuario, valor_reais):
        """
        Gera QR Code para Entrada de dinheiro (Cash-in).
        Endpoint: /transactions
        """
        client = SkalePayClient()
        try:
            # Ensure value is Decimal for precise currency handling
            valor_decimal = Decimal(str(valor_reais))

            dados_cliente = {
                "nome": getattr(usuario, 'nome_completo', '') or getattr(usuario, 'first_name', ''),
                "cpf": getattr(usuario, 'cpf_cnpj', ''),
                "email": getattr(usuario, 'email', None)
            }

            resposta = client.gerar_pix_deposito(valor_decimal, dados_cliente, usuario.id)

            return {
                "qr_code": resposta.get('pix', {}).get('qrcode'),
                "copy_paste": resposta.get('pix', {}).get('url'),
                "transaction_id": resposta.get('id')
            }

        except SkalePayError as e:
            logger.exception("Erro ao gerar depósito via SkalePayClient")
            raise ValidationError(f"Erro no processamento financeiro: {str(e)}")

    @staticmethod
    def solicitar_saque_pix(usuario, valor_reais, chave_pix, referencia_interna):
        """
        Envia Pix REAL para o usuário (Cash-out).
        Endpoint: /transfers
        """
        client = SkalePayClient()
        try:
            # Ensure value is Decimal for precise currency handling
            valor_decimal = Decimal(str(valor_reais))
            
            resposta = client.solicitar_saque(
                pix_key=str(chave_pix),
                valor=valor_decimal,
                external_ref=str(referencia_interna)
            )
            
            return resposta
            
        except SkalePayError as e:
            logger.exception("Erro ao solicitar saque via SkalePayClient")
            if "timeout" in str(e).lower():
                raise requests.exceptions.ReadTimeout(str(e))
            raise ValidationError(f"Erro no processamento financeiro: {str(e)}")

    @staticmethod
    def consultar_saldo_banca():
        """
        Consulta o saldo disponível na conta da SkalePay antes de tentar pagar.
        Doc: GET /v1/balance/available
        """
        client = SkalePayClient()
        try:
            resposta = client.consultar_saldo()
            # API retorna centavos, converte para reais
            return float(resposta.get('availableAmount', 0)) / 100.0
        except SkalePayError:
            return None

    @staticmethod
    def consultar_status_transferencia(id_transferencia_externo):
        """
        Verifica o status real de uma transferência na SkalePay.
        Doc: GET /v1/transfers/{id}
        """
        client = SkalePayClient()
        try:
            response = client._request("GET", f"/transfers/{id_transferencia_externo}")
            return response.get('status')
        except SkalePayError:
            return "ERRO_COMUNICACAO"

# Module logger
logger = logging.getLogger(__name__)