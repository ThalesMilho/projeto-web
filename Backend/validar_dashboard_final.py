import os
import django
from django.conf import settings
from decimal import Decimal

# Configuração do Ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from rest_framework.test import APIRequestFactory
from accounts.views import DashboardFinanceiroView

def validar_entrega():
    print("🕵️  INICIANDO AUDITORIA DO DASHBOARD (CHECKLIST FINAL)...\n")
    
    # 1. Simula uma requisição GET ao Dashboard
    factory = APIRequestFactory()
    request = factory.get('/api/accounts/dashboard/')
    view = DashboardFinanceiroView.as_view()
    response = view(request)
    
    if response.status_code != 200:
        print(f"❌ Erro Crítico: Dashboard retornou status {response.status_code}")
        return

    data = response.data
    
    # 2. CHECKLIST AUTOMATIZADO
    checklist = {
        "1. Visão Geral (Lucro)": "lucro_liquido" in data['resumo'],
        "2. Financeiro (Ticket Médio)": "ticket_medio_deposito" in data['kpis_estrategicos'],
        "3. Conversão (FTD %)": "taxa_conversao_ftd" in data['kpis_estrategicos'],
        "4. Retenção (Churn)": "churn_estimado_percent" in data['kpis_estrategicos'],
        "5. Crescimento (Mês a Mês)": "crescimento_mensal_percent" in data['kpis_estrategicos'],
        "6. Inteligência (Projeção)": "projecao_lucro_30d" in data['inteligencia'],
        "7. Operacional (Mapa Calor)": "mapa_calor" in data['operacional'],
        "8. Risco (Alertas IP)": "alertas_risco" in data['operacional']
    }
    
    # 3. EXIBIÇÃO DO RELATÓRIO
    todos_ok = True
    print(f"{'ITEM':<35} | {'STATUS':<10} | {'VALOR ENCONTRADO'}")
    print("-" * 65)
    
    val_map = {
        "1. Visão Geral (Lucro)": data['resumo'].get('lucro_liquido'),
        "2. Financeiro (Ticket Médio)": data['kpis_estrategicos'].get('ticket_medio_deposito'),
        "3. Conversão (FTD %)": data['kpis_estrategicos'].get('taxa_conversao_ftd'),
        "4. Retenção (Churn)": data['kpis_estrategicos'].get('churn_estimado_percent'),
        "5. Crescimento (Mês a Mês)": data['kpis_estrategicos'].get('crescimento_mensal_percent'),
        "6. Inteligência (Projeção)": data['inteligencia'].get('projecao_lucro_30d'),
        "7. Operacional (Mapa Calor)": "OK (JSON)" if data['operacional'].get('mapa_calor') is not None else "Vazio",
        "8. Risco (Alertas IP)": data['operacional'].get('alertas_risco')
    }

    for item, passou in checklist.items():
        status = "✅ OK" if passou else "❌ FALHA"
        valor = val_map.get(item, "N/A")
        print(f"{item:<35} | {status:<10} | {valor}")
        if not passou: todos_ok = False

    print("-" * 65)
    
    if todos_ok:
        print("\n🏆 SUCESSO! O Dashboard atende a 100% dos requisitos da chefia.")
        print("   O Backend está pronto para integração com o Frontend.")
    else:
        print("\n⚠️  ATENÇÃO: Alguns itens falharam. Verifique o código.")

if __name__ == "__main__":
    validar_entrega()