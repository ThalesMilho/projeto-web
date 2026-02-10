import logging
from decimal import Decimal
from collections import defaultdict

from django.db import transaction, DatabaseError
from django.db.models import F

from .models import Sorteio, Aposta
from .strategies import ValidadorFactory
from accounts.services.wallet import WalletService

logger = logging.getLogger(__name__)

def apurar_sorteio(sorteio_id):
    """
    Processa todas as apostas de um sorteio com estratégia de lote (Batch)
    e agregação financeira para alta performance.
    """
    try:
        # Atomicidade garante que ou tudo é apurado, ou nada muda (Rollback em erro)
        with transaction.atomic():
            # 1. TRAVA DE SEGURANÇA (Lock Pessimista)
            # 'nowait=True' faz a função falhar imediatamente se outro processo já estiver
            # apurando este sorteio, evitando filas de travamento no banco.
            try:
                sorteio = Sorteio.objects.select_for_update(nowait=True).get(id=sorteio_id)
            except DatabaseError:
                logger.warning(f"Sorteio {sorteio_id} já está sendo processado por outra transação.")
                return False

            if sorteio.fechado:
                logger.info(f"Sorteio {sorteio_id} já estava fechado.")
                return True

            logger.info(f"Iniciando apuração otimizada do sorteio {sorteio_id}...")

            # Estruturas para processamento em lote
            apostas_para_atualizar = []
            premios_por_usuario = defaultdict(Decimal)
            BATCH_SIZE = 1000

            # 2. BUSCA OTIMIZADA (Iterator)
            # select_related('modalidade') evita N+1 queries ao acessar a cotação.
            # iterator() traz os dados em chunks, economizando memória RAM.
            apostas_qs = Aposta.objects.filter(sorteio_id=sorteio.pk)\
                                       .select_related('modalidade')\
                                       .iterator(chunk_size=2000)

            for aposta in apostas_qs:
                # Recupera a estratégia correta baseada na modalidade
                strategy = ValidadorFactory.get_strategy(aposta.modalidade) if aposta.modalidade_id else None
                
                ganhou = False
                premio = Decimal('0.00')

                if strategy:
                    # Executa a regra de negócio (Validador)
                    if strategy.verificar(aposta, sorteio):
                        ganhou = True
                        # Calculo seguro com Decimal
                        cotacao = Decimal(str(aposta.modalidade.cotacao))
                        valor_apostado = Decimal(str(aposta.valor))
                        premio = (valor_apostado * cotacao).quantize(Decimal('0.01'))

                        # 3. AGREGAÇÃO FINANCEIRA
                        # Não chamamos a Wallet agora. Apenas somamos o que o usuário deve receber.
                        premios_por_usuario[aposta.usuario_id] += premio

                # Atualiza o objeto em memória (sem salvar no DB ainda)
                aposta.ganhou = ganhou
                aposta.valor_premio = premio
                apostas_para_atualizar.append(aposta)

                # 4. SALVAMENTO EM LOTE (Bulk Update)
                if len(apostas_para_atualizar) >= BATCH_SIZE:
                    _salvar_lote_apostas(apostas_para_atualizar)
                    apostas_para_atualizar = []  # Limpa a lista

            # Salva o restante das apostas que não completaram um lote
            if apostas_para_atualizar:
                _salvar_lote_apostas(apostas_para_atualizar)

            # 5. PROCESSAMENTO FINANCEIRO AGRUPADO
            # Fazemos apenas 1 crédito por usuário vencedor, reduzindo drasticamente as escritas na tabela de transações.
            logger.info(f"Processando pagamentos para {len(premios_por_usuario)} usuários vencedores.")
            for usuario_id, total_premio in premios_por_usuario.items():
                if total_premio > 0:
                    WalletService.credit(
                        user_id=usuario_id,
                        amount=total_premio,
                        description=f"Prêmios acumulados - Sorteio {sorteio.id}",
                        tipo='PREMIO',
                    )

            # Finaliza o sorteio
            sorteio.fechado = True
            sorteio.save(update_fields=['fechado'])
            
            logger.info(f"Sorteio {sorteio_id} apurado com sucesso.")

        return True

    except Sorteio.DoesNotExist:
        logger.error(f"Sorteio ID {sorteio_id} não encontrado.")
        raise ValueError("Sorteio não encontrado.")
    except Exception as e:
        logger.exception(f"Erro crítico ao apurar sorteio {sorteio_id}: {str(e)}")
        raise ValueError(f"Erro ao apurar sorteio: {str(e)}")

def _salvar_lote_apostas(lista_apostas):
    """Helper para executar o bulk_update de forma limpa."""
    if not lista_apostas:
        return
    Aposta.objects.bulk_update(lista_apostas, ['ganhou', 'valor_premio'])