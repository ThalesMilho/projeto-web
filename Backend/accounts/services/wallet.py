"""
Refactored Wallet Service for "Money as Integer" architecture.
All monetary values are stored and processed as integer cents.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Optional, Any, Union

from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.exceptions import ValidationError

from accounts.models import Transacao, SolicitacaoPagamento


class WalletService:
    """
    Wallet service implementing "Money as Integer" architecture.
    All amounts are stored as integer cents (R$ 10.50 = 1050 cents).
    """
    
    @staticmethod
    def _convert_to_cents(amount: Union[float, Decimal, int, str]) -> int:
        """
        Convert various input formats to integer cents.
        
        Examples:
            10.50 -> 1050
            "10.50" -> 1050
            1050 -> 1050
            "1050" -> 1050
        """
        if isinstance(amount, int):
            return amount
        elif isinstance(amount, float):
            return int(amount * 100)
        elif isinstance(amount, Decimal):
            return int(float(amount) * 100)
        elif isinstance(amount, str):
            # Handle both decimal and integer strings
            if '.' in amount:
                return int(float(amount) * 100)
            else:
                return int(amount)
        else:
            raise ValidationError(f"Invalid amount type: {type(amount)}")
    
    @staticmethod
    def _cents_to_decimal(cents: int) -> Decimal:
        """
        Convert integer cents back to Decimal for display.
        
        Examples:
            1050 -> Decimal('10.50')
            100 -> Decimal('1.00')
        """
        return Decimal(cents) / Decimal('100')
    
    @staticmethod
    def _format_display(cents: int) -> str:
        """
        Format cents for display (R$ 10,50).
        """
        return f"R$ {cents/100:.2f}"
    
    @staticmethod
    def debit(user_id: int, amount: Union[float, Decimal, int, str], description: str, 
                related_object: Optional[Any] = None, tipo: str = 'APOSTA') -> Transacao:
        """
        Debit amount from user wallet using integer cents.
        
        Args:
            user_id: User ID
            amount: Amount in various formats (will be converted to cents)
            description: Transaction description
            related_object: Optional related object
            tipo: Transaction type
            
        Returns:
            Transacao object
            
        Raises:
            ValidationError: If amount is invalid or insufficient balance
        """
        if amount is None:
            raise ValidationError("Amount is required")

        # Convert to cents
        amount_cents = WalletService._convert_to_cents(amount)
        
        if amount_cents <= 0:
            raise ValidationError("Amount must be positive")

        User = get_user_model()

        with transaction.atomic():
            user = User.objects.select_for_update().get(pk=user_id)
            saldo_anterior_cents = user.saldo

            if saldo_anterior_cents < amount_cents:
                # Format for error message
                amount_display = WalletService._format_display(amount_cents)
                balance_display = WalletService._format_display(saldo_anterior_cents)
                raise ValidationError(f"Saldo insuficiente. Tentou debitar {amount_display}, saldo atual: {balance_display}")

            user.saldo = saldo_anterior_cents - amount_cents
            user.save(update_fields=['saldo'])

            tx_kwargs = {
                'usuario': user,
                'tipo': tipo,
                'valor': amount_cents,  # Store as cents
                'saldo_anterior': saldo_anterior_cents,
                'saldo_posterior': user.saldo,
                'descricao': description,
            }

            if isinstance(related_object, SolicitacaoPagamento):
                tx_kwargs['origem_solicitacao'] = related_object

            return Transacao.objects.create(**tx_kwargs)

    @staticmethod
    def credit(user_id: int, amount: Union[float, Decimal, int, str], description: str, 
                 related_object: Optional[Any] = None, tipo: str = 'PREMIO') -> Transacao:
        """
        Credit amount to user wallet using integer cents.
        
        Args:
            user_id: User ID
            amount: Amount in various formats (will be converted to cents)
            description: Transaction description
            related_object: Optional related object
            tipo: Transaction type
            
        Returns:
            Transacao object
            
        Raises:
            ValidationError: If amount is invalid
        """
        if amount is None:
            raise ValidationError("Amount is required")

        # Convert to cents
        amount_cents = WalletService._convert_to_cents(amount)
        
        if amount_cents <= 0:
            raise ValidationError("Amount must be positive")

        User = get_user_model()

        with transaction.atomic():
            user = User.objects.select_for_update().get(pk=user_id)
            saldo_anterior_cents = user.saldo

            user.saldo = saldo_anterior_cents + amount_cents
            user.save(update_fields=['saldo'])

            tx_kwargs = {
                'usuario': user,
                'tipo': tipo,
                'valor': amount_cents,  # Store as cents
                'saldo_anterior': saldo_anterior_cents,
                'saldo_posterior': user.saldo,
                'descricao': description,
            }

            if isinstance(related_object, SolicitacaoPagamento):
                tx_kwargs['origem_solicitacao'] = related_object

            return Transacao.objects.create(**tx_kwargs)
    
    @staticmethod
    def get_balance_cents(user_id: int) -> int:
        """
        Get user balance in cents.
        
        Args:
            user_id: User ID
            
        Returns:
            Balance in integer cents
        """
        User = get_user_model()
        user = User.objects.get(pk=user_id)
        return user.saldo
    
    @staticmethod
    def get_balance_decimal(user_id: int) -> Decimal:
        """
        Get user balance as Decimal for display.
        
        Args:
            user_id: User ID
            
        Returns:
            Balance as Decimal
        """
        cents = WalletService.get_balance_cents(user_id)
        return WalletService._cents_to_decimal(cents)
    
    @staticmethod
    def get_balance_display(user_id: int) -> str:
        """
        Get formatted balance for display.
        
        Args:
            user_id: User ID
            
        Returns:
            Formatted balance string (R$ 10,50)
        """
        cents = WalletService.get_balance_cents(user_id)
        return WalletService._format_display(cents)
    
    @staticmethod
    def transfer(from_user_id: int, to_user_id: int, amount_cents: int, description: str) -> tuple[Transacao, Transacao]:
        """
        Transfer amount between users using integer cents.
        
        Args:
            from_user_id: Source user ID
            to_user_id: Destination user ID
            amount_cents: Amount in cents
            description: Transaction description
            
        Returns:
            Tuple of (debit_transaction, credit_transaction)
            
        Raises:
            ValidationError: If insufficient balance or invalid users
        """
        if amount_cents <= 0:
            raise ValidationError("Transfer amount must be positive")

        User = get_user_model()

        with transaction.atomic():
            # Lock both users to prevent race conditions
            from_user = User.objects.select_for_update().get(pk=from_user_id)
            to_user = User.objects.select_for_update().get(pk=to_user_id)
            
            if from_user.saldo < amount_cents:
                raise ValidationError("Saldo insuficiente para transferência")

            # Debit from source user
            from_saldo_anterior = from_user.saldo
            from_user.saldo -= amount_cents
            from_user.save(update_fields=['saldo'])
            
            # Credit to destination user
            to_saldo_anterior = to_user.saldo
            to_user.saldo += amount_cents
            to_user.save(update_fields=['saldo'])
            
            # Create debit transaction
            debit_tx = Transacao.objects.create(
                usuario=from_user,
                tipo='APOSTA',
                valor=amount_cents,
                saldo_anterior=from_saldo_anterior,
                saldo_posterior=from_user.saldo,
                descricao=f"Transferência para {to_user.cpf_cnpj}: {description}"
            )
            
            # Create credit transaction
            credit_tx = Transacao.objects.create(
                usuario=to_user,
                tipo='DEPOSITO',
                valor=amount_cents,
                saldo_anterior=to_saldo_anterior,
                saldo_posterior=to_user.saldo,
                descricao=f"Transferência de {from_user.cpf_cnpj}: {description}"
            )
            
            return debit_tx, credit_tx
