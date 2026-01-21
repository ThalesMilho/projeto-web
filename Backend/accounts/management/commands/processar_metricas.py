from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Sum, Count, Q
from django.db.models.functions import ExtractHour
from datetime import timedelta
from decimal import Decimal
from accounts.models import MetricasDiarias, Transacao, CustomUser
from games.models import Aposta

class Command(BaseCommand):
    help = 'ETL Completo: Financeiro, Operacional, Churn e Mapa de Calor.'

    def handle(self, *args, **options):
        # Para testes imediatos use: ontem = timezone.localdate()
        # Para produção: ontem = timezone.localdate() - timedelta(days=1)
        ontem = timezone.localdate() - timedelta(days=1)
        
        self.stdout.write(f"📊 Processando métricas para: {ontem}")

        # --- 1. FINANCEIRO ---
        transacoes_dia = Transacao.objects.filter(data__date=ontem)
        
        resumo_dep = transacoes_dia.filter(tipo='DEPOSITO').aggregate(total=Sum('valor'), qtd=Count('id'))
        dep_val = resumo_dep['total'] or Decimal('0.00')
        dep_qtd = resumo_dep['qtd'] or 0

        resumo_saq = transacoes_dia.filter(tipo='SAQUE').aggregate(total=Sum('valor'), qtd=Count('id'))
        saq_val = resumo_saq['total'] or Decimal('0.00')
        saq_qtd = resumo_saq['qtd'] or 0
        
        bonus_val = transacoes_dia.filter(tipo='BONUS').aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')

        # --- 2. OPERACIONAL & MODALIDADES ---
        apostas_dia = Aposta.objects.filter(criado_em__date=ontem)
        
        resumo_game = apostas_dia.aggregate(
            apostado=Sum('valor'),
            premios=Sum('valor_premio', filter=Q(ganhou=True))
        )
        total_apostado = resumo_game['apostado'] or Decimal('0.00')
        total_premios = resumo_game['premios'] or Decimal('0.00')
        house_edge = total_apostado - total_premios

        # JSON Modalidades
        stats_modalidades = apostas_dia.values('tipo_jogo').annotate(
            total_vol=Sum('valor'),
            total_pay=Sum('valor_premio', filter=Q(ganhou=True)),
            qtd=Count('id')
        ).order_by('-total_vol')

        perf_dict = {}
        for item in stats_modalidades:
            modalidade = item['tipo_jogo'] or "Outros"
            vol = float(item['total_vol'] or 0)
            pay = float(item['total_pay'] or 0)
            perf_dict[modalidade] = {
                "apostado": vol, "premios": pay, "lucro": vol - pay, "qtd": item['qtd']
            }

        # --- 3. GAP RESOLVIDO: MAPA DE CALOR (HORÁRIOS DE PICO) ---
        # Agrupa apostas por hora (0 a 23)
        apostas_por_hora = apostas_dia.annotate(hora=ExtractHour('criado_em')).values('hora').annotate(
            vol=Sum('valor'),
            qtd=Count('id')
        ).order_by('hora')

        mapa_horas = {f"{h:02d}h": {"vol": 0.0, "qtd": 0} for h in range(24)}
        for item in apostas_por_hora:
            h_key = f"{item['hora']:02d}h"
            mapa_horas[h_key] = {"vol": float(item['vol']), "qtd": item['qtd']}

        # --- 4. GAP RESOLVIDO: CHURN & ENGAGEMENT ---
        # Novos: entraram ontem
        novos = CustomUser.objects.filter(date_joined__date=ontem).count()
        
        # Ativos: apostaram ontem
        ids_ativos_ontem = set(apostas_dia.values_list('usuario_id', flat=True))
        ativos_count = len(ids_ativos_ontem)
        
        # Lógica de Churn (Simplificada para MVP):
        # Usuários que apostaram há 7 dias atrás, mas NÃO apostaram nos últimos 3 dias (incluindo ontem)
        sete_dias_atras = ontem - timedelta(days=7)
        ids_ativos_semana_passada = set(Aposta.objects.filter(criado_em__date=sete_dias_atras).values_list('usuario_id', flat=True))
        
        # Quem estava lá e sumiu?
        ids_perda = ids_ativos_semana_passada - ids_ativos_ontem
        churn_count = len(ids_perda) # Usuários que "churnaram" ontem

        # FTDs
        ftds_qs = CustomUser.objects.filter(data_primeiro_deposito__date=ontem)
        ftds_qtd = ftds_qs.count()
        ftds_val = Transacao.objects.filter(tipo='DEPOSITO', data__date=ontem, usuario__in=ftds_qs).aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')

        # --- 5. GRAVAÇÃO ---
        MetricasDiarias.objects.update_or_create(
            data=ontem,
            defaults={
                'total_deposito_valor': dep_val, 'total_deposito_qtd': dep_qtd,
                'total_saque_valor': saq_val, 'total_saque_qtd': saq_qtd,
                'total_bonus_concedido': bonus_val,
                'total_apostado': total_apostado, 'total_premios': total_premios,
                'house_edge_valor': house_edge,
                'novos_usuarios': novos, 'usuarios_ativos': ativos_count,
                'ftds_qtd': ftds_qtd, 'ftds_valor': ftds_val,
                
                # Campos Novos/JSONs
                'performance_modalidades': perf_dict,
                'mapa_calor_horas': mapa_horas # <-- Salva o Churn pode ser calculado no front comparando ativos vs novos
            }
        )
        self.stdout.write(self.style.SUCCESS(f"✅ ETL OK. Churn Estimado: {churn_count} users."))