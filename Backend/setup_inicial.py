import os
import django
from datetime import date

# Configura o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from games.models import ParametrosDoJogo, Sorteio
from django.utils import timezone

def popular_banco():
    print(">>> Iniciando Configuração da Banca...")

    # 1. Criar Parâmetros Gerais (Cotações e Limites)
    if not ParametrosDoJogo.objects.exists():
        ParametrosDoJogo.objects.create(
            limite_saque_automatico=500.00,
            tempo_minimo_deposito_saque_minutos=120,
            cotacao_grupo=18.0,
            cotacao_dezena=60.0,
            cotacao_centena=600.0,
            cotacao_milhar=4000.0,
        )
        print("[OK] Parâmetros de Jogo e Cotações criados.")
    else:
        print("[SKIP] Parâmetros já existem.")

    # 2. Criar Sorteios para HOJE usando os CÓDIGOS do Model
    hoje = timezone.now().date()
    
    # Lista exata das siglas definidas no seu models.py (max_length=3)
    siglas_horarios = ['PTM', 'PT', 'PTV', 'FED', 'COR']

    print(f">>> Gerando sorteios para a data: {hoje}")

    for sigla in siglas_horarios:
        # Tenta criar o sorteio se não existir
        obj, created = Sorteio.objects.get_or_create(
            data=hoje,
            horario=sigla, # Agora estamos passando a string curta correta!
            defaults={
                'fechado': False,
                'premio_1': None,
                'premio_2': None,
                'premio_3': None,
                'premio_4': None,
                'premio_5': None,
            }
        )
        
        if created:
            print(f"[OK] Sorteio {sigla} criado.")
        else:
            print(f"[SKIP] Sorteio {sigla} já existe.")
    
    print(">>> Configuração Concluída! Agora os testes vão passar.")

if __name__ == "__main__":
    popular_banco()