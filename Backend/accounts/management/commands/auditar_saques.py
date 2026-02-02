import logging
import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction, DatabaseError
from accounts.models import SolicitacaoPagamento, Transacao, CustomUser
from accounts.services import SkalePayService

# Configuração de Logs
logger = logging.getLogger('auditoria_financeira')

class Command(BaseCommand):
    help = 'Audita saques travados em PROCESSANDO e reconcilia com o Banco'

    def handle(self, *args, **kwargs):
        self.stdout.write("=== Iniciando Auditoria de Saques ===")
        
        # 1. Margem de segurança: Só mexe no que está travado há mais de 5 minutos
        # Isso evita conflito com saques que estão acontecendo AGORA.
        delay_seguranca = timezone.now() - datetime.timedelta(minutes=5)
        
        # Pega saques 'PROCESSANDO' antigos
        saques_pendentes = SolicitacaoPagamento.objects.filter(
            tipo='SAQUE',
            status='PROCESSANDO',
            criado_em__lt=delay_seguranca
        ).order_by('criado_em')[:50] # Limite de lote para evitar timeout do script

        if not saques_pendentes.exists():
            self.stdout.write("Nenhum saque pendente de auditoria.")
            return

        self.stdout.write(f"Encontrados {saques_pendentes.count()} saques para auditar.")

        for saque in saques_pendentes:
            self._processar_um_saque(saque)

        self.stdout.write("=== Auditoria Finalizada ===")

    def _processar_um_saque(self, saque_ref):
        """
        Processa um único saque dentro de uma transação atômica isolada.
        Se um falhar, não atrapalha os outros.
        """
        try:
            with transaction.atomic():
                # [LOCK] Bloqueia a linha no DB para garantir que o Webhook não mexa aqui agora
                saque = SolicitacaoPagamento.objects.select_for_update(nowait=True).get(id=saque_ref.id)

                # Re-checa status após o lock (vai que mudou milissegundos antes)
                if saque.status != 'PROCESSANDO':
                    self.stdout.write(f"Saque {saque.id}: Status mudou para {saque.status}. Pulando.")
                    return

                # CASO 1: Sem ID Externo (Falha pré-envio ou timeout severo)
                # Risco: O dinheiro pode ter saído, mas não salvamos o ID.
                # Ação: Não estornamos automático. Jogamos para Humano.
                if not saque.id_externo:
                    saque.status = 'EM_ANALISE'
                    saque.analise_motivo = "Auditoria: Sem ID Externo. Verificar manualmente na SkalePay."
                    saque.save()
                    self.stdout.write(f"Saque {saque.id}: Movido para EM_ANALISE (Sem ID).")
                    return

                # CASO 2: Com ID Externo (Consulta API)
                status_real = SkalePayService.consultar_status_transferencia(saque.id_externo)
                
                if status_real == 'ERRO_COMUNICACAO':
                    self.stdout.write(f"Saque {saque.id}: API SkalePay indisponível. Tentaremos depois.")
                    return

                # Decisão baseada na resposta do Banco
                if status_real == 'PAID':
                    self._aprovar_saque(saque)
                
                elif status_real in ['FAILED', 'CANCELED', 'REJECTED', 'NAO_ENCONTRADO']:
                    self._estornar_saque(saque, status_real)
                
                else:
                    # PROCESSING, SCHEDULED, ou status desconhecido
                    self.stdout.write(f"Saque {saque.id}: Ainda processando no banco ({status_real}). Aguardando.")

        except DatabaseError:
            self.stdout.write(f"Saque {saque_ref.id}: Linha travada por outro processo. Pulando.")
        except Exception as e:
            logger.error(f"Erro crítico auditando saque {saque_ref.id}: {e}")
            self.stdout.write(f"ERRO CRÍTICO no saque {saque_ref.id}: {e}")

    def _aprovar_saque(self, saque):
        saque.status = 'APROVADO'
        saque.data_aprovacao = timezone.now()
        saque.analise_motivo = "Aprovado via Auditoria Automática"
        saque.save()
        self.stdout.write(f"Saque {saque.id}: CONFIRMADO PAGO ✅")

    def _estornar_saque(self, saque, motivo_banco):
        # 1. Lock no Usuário para devolver saldo
        user = CustomUser.objects.select_for_update().get(id=saque.usuario.id)
        
        # 2. Devolve a grana
        user.saldo += saque.valor
        user.save()

        # 3. Marca como recusado
        saque.status = 'RECUSADO'
        saque.analise_motivo = f"Auditoria: Banco retornou {motivo_banco}"
        saque.save()

        # 4. Gera Extrato de Estorno
        Transacao.objects.create(
            usuario=user,
            tipo='ESTORNO',
            valor=saque.valor,
            saldo_anterior=user.saldo - saque.valor,
            saldo_posterior=user.saldo,
            descricao=f"Estorno Automático ({motivo_banco})",
            origem_solicitacao=saque
        )
        self.stdout.write(f"Saque {saque.id}: ESTORNADO 💰")