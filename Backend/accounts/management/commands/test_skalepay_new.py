import os
import base64
import requests
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class Command(BaseCommand):
    help = 'Diagnóstico de Conectividade SkalePay (WAF Bypass & Auth Check) com cURL Forense'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('--- INICIANDO DIAGNÓSTICO SKALEPAY (Forense) ---'))

        # 1. RECUPERAÇÃO DE CHAVE
        env_key = os.getenv('SKALEPAY_SECRET_KEY')
        settings_key = getattr(settings, 'SKALEPAY_SECRET_KEY', None)
        final_key = env_key or settings_key
        
        if not final_key:
            self.stdout.write(self.style.ERROR('ERRO: Nenhuma chave SKALEPAY_SECRET_KEY encontrada!'))
            return

        masked_key = f"{final_key[:6]}...{final_key[-4:]}"
        self.stdout.write(f'Chave em uso: {masked_key}')

        # 2. CONSTRUIR HEADERS "LEVEL 2" (Chrome Mimicry)
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Content-Type": "application/json",
            "sec-ch-ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Upgrade-Insecure-Requests": "1",
            # Manual Basic Auth Header (evita fingerprinting da lib)
            "Authorization": f"Basic {base64.b64encode(f'{final_key}:x'.encode()).decode()}"
        }

        # 3. GERAR COMANDO cURL EQUIVALENTE (Forense)
        url = "https://api.conta.skalepay.com.br/v1/balance/available"
        curl_cmd = f"""curl -v '{url}' \\
  -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36' \\
  -H 'Accept: application/json, text/plain, */*' \\
  -H 'Accept-Language: pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7' \\
  -H 'Connection: keep-alive' \\
  -H 'Cache-Control: no-cache' \\
  -H 'Pragma: no-cache' \\
  -H 'Content-Type: application/json' \\
  -H 'sec-ch-ua: "Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"' \\
  -H 'sec-ch-ua-mobile: ?0' \\
  -H 'sec-ch-ua-platform: "Linux"' \\
  -H 'Sec-Fetch-Site: none' \\
  -H 'Sec-Fetch-Mode: navigate' \\
  -H 'Sec-Fetch-User: ?1' \\
  -H 'Sec-Fetch-Dest: document' \\
  -H 'Upgrade-Insecure-Requests: 1' \\
  -H 'Authorization: Basic {base64.b64encode(f"{final_key}:x".encode()).decode()}' \\
  --compressed
"""
        self.stdout.write(self.style.NOTICE('\n--- COMANDO cURL EQUIVALENTE (Copie e cole manualmente) ---'))
        self.stdout.write(curl_cmd)

        # 4. EXECUTAR REQUISIÇÃO PYTHON (COMPARAÇÃO)
        self.stdout.write(self.style.NOTICE('\n--- EXECUTANDO REQUISIÇÃO PYTHON ---'))
        try:
            response = requests.get(url, headers=headers, timeout=10)
            status = response.status_code
            body_preview = response.text[:500] if response.text else '(empty)'
            
            self.stdout.write(f'Status Code: {status}')
            self.stdout.write(f'Response Headers: {dict(response.headers)}')
            self.stdout.write(f'Body (first 500 chars): {body_preview}')
            
            if status == 200:
                try:
                    saldo_cents = response.json().get('availableAmount', 0)
                    saldo_reais = saldo_cents / 100
                    self.stdout.write(self.style.SUCCESS(f'SUCESSO! Saldo disponível: R$ {saldo_reais:.2f}'))
                except Exception:
                    self.stdout.write(self.style.WARNING('Resposta 200 mas JSON inválido. Verifique body acima.'))
            elif status == 401:
                self.stdout.write(self.style.WARNING('WAF PASSOU (401)! Mas a chave está inválida.'))
            elif status == 403:
                self.stdout.write(self.style.ERROR('BLOQUEIO WAF (403): IP ainda não liberado ou headers insuficientes.'))
                self.stdout.write(self.style.NOTICE('Tente executar o cURL acima manualmente. Se funcionar, é fingerprinting TLS/biblioteca.'))
            else:
                self.stdout.write(self.style.ERROR(f'Status inesperado: {status}'))
                self.stdout.write(self.style.NOTICE('Verifique body e headers acima.'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'ERRO TÉCNICO: {str(e)}'))
            self.stdout.write(self.style.NOTICE('Se o cURL manual funcionar, o problema é no ambiente Python/TLS.'))
