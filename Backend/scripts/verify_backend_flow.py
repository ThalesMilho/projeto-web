#!/usr/bin/env python
"""
Backend Integrity Verification Script
Tests: Adapter → Wallet Debit → Persistence → Payout via Strategy Engine
Run via: python manage.py shell < scripts/verify_backend_flow.py
"""

import os
import sys
from decimal import Decimal

# Ensure project root is on path so imports work
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from django.contrib.auth import get_user_model
from django.db import transaction
from games.models import Jogo, Modalidade, Sorteio, Aposta
from games.serializer import CriarApostaSerializer
from games.engine import apurar_sorteio
from accounts.models import Transacao
from accounts.services.wallet import WalletService

User = get_user_model()

def banner(msg):
    print(f"\n{'='*60}")
    print(f"🧪 {msg}")
    print('='*60)

def assert_step(step, condition, msg_ok, msg_fail):
    if condition:
        print(f"✅ STEP {step} PASSED: {msg_ok}")
    else:
        raise AssertionError(f"❌ STEP {step} FAILED: {msg_fail}")

def setup():
    banner("SETUP: Creating test data")
    # 1. User with balance
    user, _ = User.objects.get_or_create(
        username='test_punter',
        defaults={
            'email': 'test@example.com',
            'saldo': Decimal('1000.00'),
            'tipo_usuario': 'CLIENTE',
        }
    )
    user.saldo = Decimal('1000.00')
    user.save(update_fields=['saldo'])
    print(f"👤 User: {user.username} | Balance: R$ {user.saldo}")

    # 2. Ensure Jogo do Bicho exists
    jogo, _ = Jogo.objects.get_or_create(
        nome='Bicho',
        defaults={'tipo': 'bicho', 'ativo': True}
    )
    print(f"🎲 Jogo: {jogo.nome} ({jogo.tipo})")

    # 3. Ensure Modalidade Milhar (code M) exists
    modalidade, _ = Modalidade.objects.get_or_create(
        jogo=jogo,
        nome='Milhar',
        defaults={'cotacao': Decimal('4000.00'), 'quantidade_palpites': 1}
    )
    print(f"🎯 Modalidade: {modalidade.nome} | Cotação: {modalidade.cotacao}")

    # 4. Open Sorteio for today
    from django.utils import timezone
    hoje = timezone.localdate()
    sorteio, _ = Sorteio.objects.get_or_create(
        data=hoje,
        defaults={'fechado': False, 'resultado': None}
    )
    print(f"📅 Sorteio: {sorteio} | Aberto: {not sorteio.fechado}")

    return user, jogo, modalidade, sorteio

def test_adapter(user, sorteio):
    banner("STEP 1: LEGACY ADAPTER TEST")
    payload = {
        "tipo_jogo": "M",       # Legacy String
        "palpite": "1234",      # Legacy String
        "valor": Decimal('10.00'),
        "sorteio": sorteio.id
    }
    serializer = CriarApostaSerializer(data=payload)
    assert_step(1, serializer.is_valid(), f"Serializer valid: {payload}", f"Errors: {serializer.errors}")

    validated = serializer.validated_data
    assert_step(1.1, isinstance(validated.get('modalidade'), Modalidade), "modalidade resolved to Modalidade instance", f"modalidade is {type(validated.get('modalidade'))}")
    assert_step(1.2, isinstance(validated.get('jogo'), Jogo), "jogo resolved to Jogo instance", f"jogo is {type(validated.get('jogo'))}")
    assert_step(1.3, isinstance(validated.get('palpites'), list) and validated['palpites'], "palpites is non-empty list", f"palpites={validated.get('palpites')}")
    print(f"🔁 Adapter resolved modalidade={validated['modalidade'].nome} jogo={validated['jogo'].nome} palpites={validated['palpites']}")

    # Save the bet
    aposta = serializer.save(usuario=user)
    print(f"💾 Aposta criada: id={aposta.id} | valor={aposta.valor} | modalidade={aposta.modalidade.nome}")
    return aposta

def test_wallet_debit(user, aposta):
    banner("STEP 2: WALLET DEBIT TEST")
    user.refresh_from_db()
    assert_step(2, user.saldo == Decimal('990.00'), f"Balance after debit: R$ {user.saldo}", f"Expected R$ 990.00, got R$ {user.saldo}")

    tx = Transacao.objects.filter(usuario=user, tipo='APOSTA', valor=aposta.valor).first()
    assert_step(2.1, tx is not None, f"Transacao APOSTA found: id={tx.id} valor={tx.valor}", "No Transacao APOSTA found")
    print(f"💸 Transação: {tx.tipo} | Valor: R$ {tx.valor} | Saldo Ant/Post: R$ {tx.saldo_anterior}/{tx.saldo_posterior}")

def test_persistence(aposta):
    banner("STEP 3: PERSISTENCE TEST")
    aposta.refresh_from_db()
    assert_step(3, aposta.jogo_id is not None, f"aposta.jogo_id={aposta.jogo_id}", "aposta.jogo_id is NULL")
    assert_step(3.1, aposta.modalidade_id is not None, f"aposta.modalidade_id={aposta.modalidade_id}", "aposta.modalidade_id is NULL")
    print(f"📌 Persisted: jogo_id={aposta.jogo_id} modalidade_id={aposta.modalidade_id} palpites={aposta.palpites}")

def test_payout(user, aposta, sorteio):
    banner("STEP 4: PAYOUT TEST (WINNING)")
    # Set a winning result
    sorteio.resultado = ['1234']
    sorteio.save(update_fields=['resultado'])
    print(f"🎰 Sorteio resultado set to: {sorteio.resultado}")

    # Run payout engine
    apurar_sorteio(sorteio.id)
    print("⚙️ Engine apurar_sorteio executed")

    # Verify bet marked as won
    aposta.refresh_from_db()
    assert_step(4, aposta.ganhou is True, f"aposta.ganhou={aposta.ganhou}", "Bet not marked as won")
    assert_step(4.1, aposta.valor_premio == Decimal('40000.00'), f"valor_premio=R$ {aposta.valor_premio}", f"Expected R$ 40000.00, got R$ {aposta.valor_premio}")
    print(f"🏆 Bet won: premio=R$ {aposta.valor_premio}")

    # Verify balance updated
    user.refresh_from_db()
    expected_final = Decimal('990.00') + Decimal('40000.00')
    assert_step(4.2, user.saldo == expected_final, f"Final balance: R$ {user.saldo}", f"Expected R$ {expected_final}, got R$ {user.saldo}")

    # Verify PREMIO transaction
    tx_premio = Transacao.objects.filter(usuario=user, tipo='PREMIO').first()
    assert_step(4.3, tx_premio is not None, f"Transacao PREMIO found: id={tx_premio.id} valor={tx_premio.valor}", "No Transacao PREMIO found")
    print(f"💰 Prêmio creditado: R$ {tx_premio.valor}")

def main():
    banner("BACKEND INTEGRITY VERIFICATION")
    try:
        with transaction.atomic():
            user, jogo, modalidade, sorteio = setup()
            aposta = test_adapter(user, sorteio)
            test_wallet_debit(user, aposta)
            test_persistence(aposta)
            test_payout(user, aposta, sorteio)
            # Clean up to avoid side effects on reruns
            Transacao.objects.filter(usuario=user).delete()
            Aposta.objects.filter(usuario=user).delete()
            user.delete()
            banner("🎉 ALL STEPS PASSED — Backend flow is production‑ready")
    except AssertionError as e:
        banner("❌ VERIFICATION FAILED")
        print(e)
        raise
    except Exception as exc:
        banner("💥 UNEXPECTED ERROR")
        print(exc)
        raise

if __name__ == '__main__':
    # When run via shell, Django already sets up settings
    main()
