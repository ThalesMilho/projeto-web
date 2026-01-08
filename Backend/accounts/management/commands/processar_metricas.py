from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Sum, Count
from accounts.models import MetricasDiarias, Transacao, CustomUser
from games.models import Aposta 
from datetime import timedelta

class Command(BaseCommand):
    help = 'Calcula e consolida as métricas diárias (ETL) para o Dashboard'

    def handle(self, *args, **options):
        # Por padrão, calcula o dia de ONTEM (fechamento D-1)
        ontem = timezone.localdate() - timedelta(days=1)
        
        self.stdout.write(f"Iniciando processamento para: {ontem}")

        # 1. Financeiro (Caixa)
        depositos = Transacao.objects.filter(tipo='DEPOSITO', data__date=ontem).aggregate(Sum('valor'))['valor__sum'] or 0
        saques = Transacao.objects.filter(tipo='SAQUE', data__date=ontem).aggregate(Sum('valor'))['valor__sum'] or 0
        
        # 2. Operacional (Apostas)
        apostado = Aposta.objects.filter(criado_em__date=ontem).aggregate(Sum('valor'))['valor__sum'] or 0
        premios = Aposta.objects.filter(ganhou=True, criado_em__date=ontem).aggregate(Sum('valor_premio'))['valor_premio__sum'] or 0
        
        # House Edge (Receita Líquida do Jogo)
        receita_jogo = apostado - premios

        # 3. KPIs de Usuários
        novos = CustomUser.objects.filter(date_joined__date=ontem).count()
        # Exemplo de Ativos: quem apostou ou logou ontem
        ativos = CustomUser.objects.filter(last_login__date=ontem).count() 
        
        # FTDs (First Time Deposits) - Lógica aproximada para MVP
        # Conta transações de depósito onde é o primeiro do usuário naquela data
        # (Em produção refinada, usaríamos uma query mais complexa de "Min(data)")
        
        # SALVAR / ATUALIZAR TABELA DE RESUMO
        metrica, created = MetricasDiarias.objects.update_or_create(
            data=ontem,
            defaults={
                'total_deposito': depositos,
                'total_saque': saques,
                'receita_liquida': receita_jogo,
                'total_apostado': apostado,
                'total_premios': premios,
                'novos_usuarios': novos,
                'usuarios_ativos': ativos
            }
        )

        self.stdout.write(self.style.SUCCESS(f"Métricas de {ontem} processadas com sucesso!"))