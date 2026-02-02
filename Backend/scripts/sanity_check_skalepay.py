import os
import sys
import traceback

# Ensure we're running from the project Backend folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from accounts.services import SkalePayService
from accounts.models import CustomUser

print('>>> SANITY CHECK START')

# Test 1: Consultar saldo
print('\n>>> TESTE 1: Consultar Saldo...')
try:
    saldo = SkalePayService.consultar_saldo_banca()
    if saldo is not None:
        print(f'✅ SUCESSO! Saldo lido: R$ {saldo}')
    else:
        print('⚠️ Aviso: Saldo retornou None (pode ser erro de conexão ou saldo zerado).')
except Exception as e:
    print(f'❌ FALHA NO SALDO: {e}')
    traceback.print_exc()

# Prepare user for deposit test
print('\n>>> TESTE 2: Gerar QR Code de Depósito...')
user = None
try:
    user = CustomUser.objects.filter().first()
    if not user:
        raise Exception('Nenhum usuário encontrado no banco de dados.')
    print(f'Using user: {getattr(user, "username", "<unknown>")}')
    resultado = None
    try:
        resultado = SkalePayService.gerar_pedido_deposito(user, 15.00)
        if isinstance(resultado, dict) and ('id' in resultado or 'qrcode' in resultado):
            print(f"✅ SUCESSO! Depósito gerado. ID: {resultado.get('id')}")
        else:
            print(f"⚠️ Resposta estranha: {resultado}")
    except Exception as e:
        print(f'❌ FALHA NO DEPÓSITO: {e}')
        traceback.print_exc()
except Exception as e:
    print(f'❌ Não foi possível preparar o usuário para depósito: {e}')
    traceback.print_exc()

# Test 3: Solicitar saque (apenas validação de montagem do JSON/Envío)
print('\n>>> TESTE 3: Saque (Apenas validação de envio)...')
try:
    if not user:
        user = CustomUser.objects.filter().first()
    try:
        SkalePayService.solicitar_saque_pix(user, 1.00, "70114581150", "TESTE_FINAL")
    except Exception as e:
        print(f'Resultado esperado (Erro de Rede/403/etc): {e}')
        # not printing traceback to avoid sensitive info
except Exception as e:
    print(f'Erro ao executar teste de saque: {e}')
    traceback.print_exc()

print('\n>>> SANITY CHECK END')
