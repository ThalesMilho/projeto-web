from __future__ import annotations

from decimal import Decimal
from typing import Optional, Any

from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.exceptions import ValidationError

from accounts.models import Transacao, SolicitacaoPagamento


class WalletService:
    @staticmethod
    def debit(user_id: int, amount: Decimal, description: str, related_object: Optional[Any] = None, tipo: str = 'APOSTA') -> Transacao:
        if amount is None:
            raise ValidationError("Amount is required")

        amount = Decimal(str(amount)).quantize(Decimal('0.01'))
        if amount <= Decimal('0.00'):
            raise ValidationError("Amount must be positive")

        User = get_user_model()

        with transaction.atomic():
            user = User.objects.select_for_update().get(pk=user_id)
            saldo_anterior = user.saldo

            if saldo_anterior < amount:
                raise ValidationError("Saldo insuficiente")

            user.saldo = saldo_anterior - amount
            user.save(update_fields=['saldo'])

            tx_kwargs = {
                'usuario': user,
                'tipo': tipo,
                'valor': amount,
                'saldo_anterior': saldo_anterior,
                'saldo_posterior': user.saldo,
                'descricao': description,
            }

            if isinstance(related_object, SolicitacaoPagamento):
                tx_kwargs['origem_solicitacao'] = related_object

            return Transacao.objects.create(**tx_kwargs)

    @staticmethod
    def credit(user_id: int, amount: Decimal, description: str, related_object: Optional[Any] = None, tipo: str = 'PREMIO') -> Transacao:
        if amount is None:
            raise ValidationError("Amount is required")

        amount = Decimal(str(amount)).quantize(Decimal('0.01'))
        if amount <= Decimal('0.00'):
            raise ValidationError("Amount must be positive")

        User = get_user_model()

        with transaction.atomic():
            user = User.objects.select_for_update().get(pk=user_id)
            saldo_anterior = user.saldo

            user.saldo = saldo_anterior + amount
            user.save(update_fields=['saldo'])

            tx_kwargs = {
                'usuario': user,
                'tipo': tipo,
                'valor': amount,
                'saldo_anterior': saldo_anterior,
                'saldo_posterior': user.saldo,
                'descricao': description,
            }

            if isinstance(related_object, SolicitacaoPagamento):
                tx_kwargs['origem_solicitacao'] = related_object

            return Transacao.objects.create(**tx_kwargs)
