from .models import Sorteio, Aposta
from accounts.services.wallet import WalletService
from django.db import transaction
from decimal import Decimal

from .strategies import ValidadorFactory

def apurar_sorteio(sorteio_id):
    """
    Processa todas as apostas vinculadas a um sorteio específico.
    """
    try:
        with transaction.atomic():
            sorteio = Sorteio.objects.select_for_update().get(id=sorteio_id)

            if sorteio.fechado:
                return True

            for aposta in Aposta.objects.select_for_update().select_related('modalidade').filter(sorteio_id=sorteio.pk):
                strategy = ValidadorFactory.get_strategy(aposta.modalidade) if aposta.modalidade_id else None
                if not strategy:
                    aposta.ganhou = False
                    aposta.valor_premio = Decimal('0.00')
                    aposta.save(update_fields=['ganhou', 'valor_premio'])
                    continue

                ganhou = bool(strategy.verificar(aposta, sorteio))
                aposta.ganhou = ganhou

                if ganhou:
                    premio = (Decimal(str(aposta.valor)) * Decimal(str(aposta.modalidade.cotacao))).quantize(Decimal('0.01'))
                    aposta.valor_premio = premio

                    WalletService.credit(
                        user_id=aposta.usuario_id,
                        amount=premio,
                        description=f"Prêmio do sorteio {sorteio.id}",
                        tipo='PREMIO',
                    )
                else:
                    aposta.valor_premio = Decimal('0.00')

                aposta.save(update_fields=['ganhou', 'valor_premio'])

            sorteio.fechado = True
            sorteio.save(update_fields=['fechado'])

        return True

    except Sorteio.DoesNotExist:
        raise ValueError("Sorteio não encontrado.")
    except Exception as e:
        raise ValueError(f"Erro ao apurar sorteio: {str(e)}")