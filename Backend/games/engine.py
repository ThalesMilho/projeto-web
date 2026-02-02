from .models import Sorteio, Aposta, Transacao
from django.db import transaction
from decimal import Decimal

def apurar_sorteio(sorteio_id):
    """
    Processa todas as apostas vinculadas a um sorteio específico.
    """
    try:
        sorteio = Sorteio.objects.get(id=sorteio_id)
        if not sorteio.resultado:
            raise ValueError("O sorteio não possui resultado definido.")

        with transaction.atomic():
            for aposta in sorteio.apostas.select_for_update():
                # Verifica se o palpite está nos resultados
                ganhou = any(palpite in sorteio.resultado for palpite in aposta.palpites)
                aposta.ganhou = ganhou

                if ganhou:
                    # Calcula o prêmio com base na cotação
                    premio = aposta.valor_aposta * aposta.modalidade.cotacao
                    aposta.valor_premio = premio

                    # Cria uma transação de prêmio
                    Transacao.objects.create(
                        usuario=aposta.usuario,
                        tipo='PREMIO',
                        valor=premio,
                        saldo_anterior=aposta.usuario.saldo,
                        saldo_posterior=aposta.usuario.saldo + premio,
                        descricao=f"Prêmio do sorteio {sorteio.id}"
                    )

                    # Atualiza o saldo do usuário
                    aposta.usuario.saldo += premio
                    aposta.usuario.save()
                else:
                    aposta.valor_premio = Decimal('0.00')

                aposta.save()

            # Marca o sorteio como fechado
            sorteio.fechado = True
            sorteio.save()

        return True

    except Sorteio.DoesNotExist:
        raise ValueError("Sorteio não encontrado.")
    except Exception as e:
        raise ValueError(f"Erro ao apurar sorteio: {str(e)}")