import os
import requests
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class Command(BaseCommand):
    help = 'Diagnóstico de Conectividade SkalePay (WAF Bypass & Auth Check)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('--- 🚀 INICIANDO DIAGNÓSTICO SKALEPAY ---'))

        # 1. RECUPERAÇÃO DE CHAVE (PRIORIDADE: ENV -> SETTINGS)
        env_key = os.getenv('SKALEPAY_SECRET_KEY')
        settings_key = getattr(settings, 'SKALEPAY_SECRET_KEY', None)
        final_key = env_key or settings_key
        
        if not final_key:
            self.stdout.write(self.style.ERROR('❌ ERRO: Nenhuma chave SKALEPAY_SECRET_KEY encontrada!'))
            return

        masked_key = f"{final_key[:6]}...{final_key[-4:]}"
        self.stdout.write(f'🔑 Chave em uso: {masked_key}')

        # 2. CONFIGURAÇÃO "BLINDADA" (Chrome Mask)
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Content-Type": "application/json",
            "Connection": "keep-alive"
        })

        # Autenticação (Doc: Chave como usuário, 'x' como senha)
        session.auth = HTTPBasicAuth(final_key, 'x')

        # Resiliência (Retry)
        retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        session.mount("https://", HTTPAdapter(max_retries=retry))

        # 3. TESTE DE CONEXÃO (/balance/available)
        url = "https://api.conta.skalepay.com.br/v1/balance/available"
        self.stdout.write(f'📡 Conectando a: {url}')
        
        try:
            response = session.get(url, timeout=10)
            status = response.status_code
            
            if status == 200:
                saldo = response.json().get('availableAmount', 0) / 100
                self.stdout.write(self.style.SUCCESS(f'✅ SUCESSO! Saldo: R$ {saldo:.2f}'))
            elif status == 401:
                self.stdout.write(self.style.WARNING(f'🔓 WAF PASSOU (401)! Mas a chave está inválida.'))
            elif status == 403:
                self.stdout.write(self.style.ERROR(f'🛡️ BLOQUEIO WAF (403): O IP do Render ainda não foi liberado.'))
                self.stdout.write(f'Resposta: {response.text[:100]}')
            else:
                self.stdout.write(self.style.ERROR(f'⚠️ Status Inesperado: {status}'))
                self.stdout.write(response.text)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'💥 ERRO TÉCNICO: {str(e)}'))