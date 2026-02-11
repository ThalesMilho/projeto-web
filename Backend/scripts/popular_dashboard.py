import os
import django
from decimal import Decimal
from django.utils import timezone
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import MetricasDiarias

def criar_historico_fake():
    print("🚀 Gerando histórico financeiro para teste de Projeção...")
    
    # Apaga métricas antigas para não duplicar
    MetricasDiarias.objects.all().delete()
    
    hoje = timezone.localdate()
    
    # Gera dados dos últimos 10 dias
    for dias_atras in range(1, 11):
        data_simulada = hoje - timezone.timedelta(days=dias_atras)
        
        # Simula um Lucro (House Edge) variável entre 100 e 500 reais
        lucro_do_dia = Decimal(random.uniform(100.00, 500.00))
        
        MetricasDiarias.objects.create(
            data=data_simulada,
            house_edge_valor=lucro_do_dia, # GGR
            total_deposito_valor=lucro_do_dia * 2,
            total_saque_valor=lucro_do_dia,
            total_apostado=lucro_do_dia * 10,
            novos_usuarios=random.randint(1, 5)
        )
        print(f"📅 {data_simulada}: Lucro R$ {lucro_do_dia:.2f}")

    print("\n✅ Dados injetados! Agora o Dashboard terá base para calcular a projeção.")

if __name__ == '__main__':
    criar_historico_fake()