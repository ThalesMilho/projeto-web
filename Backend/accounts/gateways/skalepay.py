import os
import logging
import json
import requests
from decimal import Decimal, ROUND_HALF_UP
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests.auth import HTTPBasicAuth
from django.conf import settings
from typing import Dict, Any, Optional, Union

# Configuração de Logger específico
logger = logging.getLogger('skalepay_integration')

class SkalePayError(Exception):
    """Exceção base para erros da integração SkalePay."""
    pass

class SkalePayClient:
    """
    Cliente robusto para integração com a SkalePay.
    Implementa padrões de Circuit Breaker (via Retries), Timeouts e Type Safety.
    """
    
    BASE_URL = "https://api.conta.skalepay.com.br/v1"
    TIMEOUT = (3.05, 10)  # (Connect, Read) - 3s para conectar, 10s para ler

    DEFAULT_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Content-Type": "application/json",
    }

    _shared_session: Optional[requests.Session] = None
    _shared_session_api_key: Optional[str] = None
    
    def __init__(self):
        # Carrega a chave das variáveis de ambiente (Segurança)
        self.api_key = os.getenv('SKALEPAY_SECRET_KEY')
        if not self.api_key:
            # Fallback para settings do Django se não estiver no ENV direto
            self.api_key = getattr(settings, 'SKALEPAY_SECRET_KEY', None)
            
        if not self.api_key:
            logger.critical("SKALEPAY_SECRET_KEY não configurada!")
            raise SkalePayError("Credenciais da SkalePay não encontradas.")

        # Configura a sessão HTTP com Retry Strategy (singleton-like)
        if SkalePayClient._shared_session is None or SkalePayClient._shared_session_api_key != self.api_key:
            session = requests.Session()

            # Headers robustos para reduzir bloqueios por WAF
            session.headers.update(self.DEFAULT_HEADERS)

            # Conforme documentação: Basic Auth com User=Key e Pass='x'
            session.auth = HTTPBasicAuth(self.api_key, 'x')

            retry_strategy = Retry(
                total=3,
                backoff_factor=1, # Espera 1s, 2s, 4s
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "POST", "PUT"]
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("https://", adapter)
            session.mount("http://", adapter)

            SkalePayClient._shared_session = session
            SkalePayClient._shared_session_api_key = self.api_key

        self.session = SkalePayClient._shared_session

    def _to_cents(self, value: Union[Decimal, str, float]) -> int:
        """
        Converte valor monetário para centavos de forma segura.
        Elimina o problema do ponto flutuante.
        """
        if isinstance(value, float):
            logger.warning(f"Uso de float detectado na conversão monetária: {value}. Prefira Decimal.")
            value = str(value)
            
        if not isinstance(value, Decimal):
            value = Decimal(value)
            
        # Arredondamento bancário padrão
        cents = int(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) * 100)
        return cents

    def _request(self, method: str, endpoint: str, payload: Optional[Dict] = None) -> Dict:
        """
        Método centralizador de requisições com tratamento de erro e logging seguro.
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        # Log seguro (Sanitização básica)
        log_payload = payload.copy() if payload else {}
        if 'credit_card' in log_payload:
            log_payload['credit_card'] = '***REDACTED***'
            
        logger.info(f"SkalePay Request [{method}] {endpoint}", extra={'payload': log_payload})

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=payload,
                timeout=self.TIMEOUT,
            )
            
            response.raise_for_status()
            
            # Tenta decodificar JSON, se falhar retorna dict vazio ou erro
            try:
                data = response.json()
                return data
            except json.JSONDecodeError:
                return {"status": "success", "raw_content": response.text}

        except requests.exceptions.HTTPError as e:
            error_msg = f"Erro HTTP SkalePay: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            # Tenta extrair mensagem de erro amigável da API se existir
            try:
                error_data = e.response.json()
                raise SkalePayError(error_data.get('message', error_msg))
            except:
                raise SkalePayError(error_msg)
                
        except requests.exceptions.Timeout:
            msg = "Timeout ao conectar com SkalePay. A operação pode ter sido processada ou não."
            logger.error(msg)
            raise SkalePayError(msg)
            
        except requests.exceptions.RequestException as e:
            msg = f"Erro de conexão com SkalePay: {str(e)}"
            logger.error(msg)
            raise SkalePayError(msg)

    # =================================================================
    # MÉTODOS DE NEGÓCIO (Conforme Documentação Anexada)
    # =================================================================

    def consultar_saldo(self, recipient_id: Optional[int] = None) -> Dict:
        """
        Consulta o saldo disponível.
        Endpoint: GET /balance/available
        """
        endpoint = "/balance/available"
        params = {}
        if recipient_id:
            params['recipientId'] = recipient_id
            
        # Nota: requests aceita params no método, mas nossa _request usa json.
        # Pequena adaptação para GET com query params
        try:
            response = self.session.get(
                f"{self.BASE_URL}{endpoint}", 
                params=params, 
                timeout=self.TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao consultar saldo: {e}")
            raise SkalePayError(f"Falha ao consultar saldo: {e}")

    def criar_recebedor(self, razao_social: str, cnpj: str, banco_cod: str, agencia: str, conta: str, digito: str, tipo_conta: str = 'conta_corrente') -> Dict:
        """
        Cria um recebedor para saques.
        Endpoint: POST /recipients
        """
        payload = {
            "legalName": razao_social,
            "document": {
                "number": cnpj.replace('.', '').replace('/', '').replace('-', ''),
                "type": "CNPJ" # Ou CPF logica
            },
            "transferSettings": {
                "transferEnabled": True,
                "automaticAnticipationEnabled": True,
                "anticipatableVolumePercentage": 100
            },
            "bankAccount": {
                "bankCode": banco_cod,
                "agencyNumber": agencia,
                "accountNumber": conta,
                "accountDigit": digito,
                "type": tipo_conta # ajustar conforme enum da API
            }
        }
        return self._request("POST", "/recipients", payload)

    def gerar_pix_deposito(self, valor: Decimal, customer_data: Dict, usuario_id: Optional[int] = None) -> Dict:
        """
        Gera um PIX para depósito (Cash-in).
        NOTA: O endpoint exato de PIX não estava no snippet da doc, 
        estou assumindo o padrão `/transactions` com método de pagamento PIX.
        
        :param valor: Decimal (ex: Decimal('50.00'))
        :param customer_data: Dict com dados do cliente (nome, cpf)
        :param usuario_id: ID do usuário para incluir no metadata (webhook identification)
        """
        cents = self._to_cents(valor)
        
        payload = {
            "amount": cents,
            "paymentMethod": "pix",  # Corrigido para 'pix' minúsculo conforme documentação
            "customer": {
                "name": customer_data.get('nome'),
                "document": {
                    "number": customer_data.get('cpf'),
                    "type": "cpf"
                },
                "email": customer_data.get('email')
            },
            "items": [
                {
                    "title": "Deposito Pix",
                    "unitPrice": cents,
                    "quantity": 1,
                    "tangible": False,
                }
            ],
            "postbackUrl": getattr(settings, 'SKALEPAY_WEBHOOK_URL', None)
        }
        
        # Adiciona metadata com usuario_id para identificação no webhook
        if usuario_id:
            payload["metadata"] = {"usuario_id": usuario_id}
        
        return self._request("POST", "/transactions", payload)

    def solicitar_saque(self, pix_key: str, valor: Decimal, external_ref: Optional[str] = None, recipient_id: Optional[int] = None) -> Dict:
        """
        Realiza uma transferência/saque (Cash-out) via PIX.
        Endpoint: POST /transfers
        
        :param pix_key: Chave PIX de destino
        :param valor: Valor do saque em Decimal
        :param external_ref: Referência externa para rastreamento
        :param recipient_id: ID do recebedor (opcional, usa principal se não informado)
        """
        cents = self._to_cents(valor)
        
        payload = {
            "amount": cents,
            "pixKey": pix_key,
            "description": "Saque Plataforma",
            "postbackUrl": f"{getattr(settings, 'WEBHOOK_URL_BASE', '')}/api/accounts/webhook/skalepay/"
        }
        
        # Adiciona campos opcionais se fornecidos
        if external_ref:
            payload["externalRef"] = str(external_ref)
            
        if recipient_id:
            payload["recipientId"] = recipient_id
        
        return self._request("POST", "/transfers", payload)