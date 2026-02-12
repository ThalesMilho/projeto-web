#!/usr/bin/env python3
"""
Money Architecture Verification Script
Tests that all monetary fields use BigIntegerField (Integer Cents)
"""
import os
import sys
from pathlib import Path

# Add current directory to Python path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

# Initialize Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from accounts.models import CustomUser, Transacao, SolicitacaoPagamento, MetricasDiarias
from games.models import Aposta, ParametrosDoJogo

def main():
    print("🔍 Money Architecture Verification")
    print("=" * 40)
    
    # Check CustomUser.saldo
    user = CustomUser.objects.first()
    print(f'✅ CustomUser.saldo: {type(user.saldo).__name__ if user else "N/A"} = {user.saldo if user else "N/A"}')
    
    # Check Transacao monetary fields
    if Transacao.objects.exists():
        trans = Transacao.objects.first()
        print(f'✅ Transacao.valor: {type(trans.valor).__name__} = {trans.valor}')
        print(f'✅ Transacao.saldo_anterior: {type(trans.saldo_anterior).__name__} = {trans.saldo_anterior}')
        print(f'✅ Transacao.saldo_posterior: {type(trans.saldo_posterior).__name__} = {trans.saldo_posterior}')
    
    # Check SolicitacaoPagamento.valor
    if SolicitacaoPagamento.objects.exists():
        sol = SolicitacaoPagamento.objects.first()
        print(f'✅ SolicitacaoPagamento.valor: {type(sol.valor).__name__} = {sol.valor}')
    
    # Check MetricasDiarias fields
    if MetricasDiarias.objects.exists():
        metric = MetricasDiarias.objects.first()
        print(f'✅ MetricasDiarias.total_deposito_valor: {type(metric.total_deposito_valor).__name__} = {metric.total_deposito_valor}')
        print(f'✅ MetricasDiarias.total_apostado: {type(metric.total_apostado).__name__} = {metric.total_apostado}')
    
    # Check Aposta monetary fields
    if Aposta.objects.exists():
        aposta = Aposta.objects.first()
        print(f'✅ Aposta.valor: {type(aposta.valor).__name__} = {aposta.valor}')
        print(f'✅ Aposta.valor_premio: {type(aposta.valor_premio).__name__} = {aposta.valor_premio}')
        print(f'✅ Aposta.comissao_gerada: {type(aposta.comissao_gerada).__name__} = {aposta.comissao_gerada}')
    
    # Check ParametrosDoJogo
    if ParametrosDoJogo.objects.exists():
        params = ParametrosDoJogo.objects.first()
        print(f'✅ ParametrosDoJogo.valor_minimo_para_brinde: {type(params.valor_minimo_para_brinde).__name__} = {params.valor_minimo_para_brinde}')
    
    print('\n🎯 All monetary fields verified!')
    
    # Verify all are BigIntegerField
    all_bigint = True
    expected_fields = [
        (CustomUser, 'saldo'),
        (Transacao, 'valor'),
        (Transacao, 'saldo_anterior'),
        (Transacao, 'saldo_posterior'),
        (SolicitacaoPagamento, 'valor'),
        (MetricasDiarias, 'total_deposito_valor'),
        (MetricasDiarias, 'total_apostado'),
        (Aposta, 'valor'),
        (Aposta, 'valor_premio'),
        (Aposta, 'comissao_gerada'),
        (ParametrosDoJogo, 'valor_minimo_para_brinde'),
    ]
    
    for model, field_name in expected_fields:
        field = model._meta.get_field(field_name)
        if field and field.__class__.__name__ != 'BigIntegerField':
            print(f'❌ FIELD ERROR: {model.__name__}.{field_name} is {field.__class__.__name__}')
            all_bigint = False
    
    if all_bigint:
        print('✅ SUCCESS: All monetary fields are BigIntegerField (Integer Cents)')
        return True
    else:
        print('❌ FAILURE: Some fields are not BigIntegerField')
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
