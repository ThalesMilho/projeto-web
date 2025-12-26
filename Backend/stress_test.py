import os
import django
import threading
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal

# Configura o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from games.models import Sorteio, Aposta
from games.views import RealizarApostaView
from rest_framework.test import APIRequestFactory, force_authenticate 

User = get_user_model()

def reset_cenario():
    print("🔄 Preparando cenário...")
    # Garante usuário com saldo
    user, _ = User.objects.get_or_create(cpf_cnpj="11122233300", defaults={
        "username": "tester", 
        "nome_completo": "Tester Concorrencia"
    })
    user.saldo = Decimal('100.00')
    user.save()
    
    # Garante sorteio aberto
    sorteio, _ = Sorteio.objects.get_or_create(
        data="2025-12-31", 
        horario="COR", 
        defaults={"fechado": False}
    )
    # Garante que não está fechado por testes anteriores
    sorteio.fechado = False
    sorteio.save()
    
    # Limpa apostas antigas para contagem limpa
    Aposta.objects.filter(usuario=user).delete()
    
    return user, sorteio

def tentar_apostar(user_id, sorteio_id, index):
    try:
        factory = APIRequestFactory()
        view = RealizarApostaView.as_view()
        
        # --- CORREÇÃO 1: Palpite Único ---
        # Usa 1000+index para garantir que NUNCA repita o palpite.
        # Assim testamos o SALDO, e não a deduplicação.
        palpite = str(1000 + index)
        
        # --- CORREÇÃO 2: Valor como String ---
        # DRF aceita melhor Decimal como string "10.00" do que float 10.0
        data = {
            "sorteio": sorteio_id,
            "tipo_jogo": "G",
            "valor": "10.00", 
            "palpite": palpite 
        }
        
        request = factory.post('/api/games/apostar/', data, format='json')
        user = User.objects.get(pk=user_id)
        force_authenticate(request, user=user)
        
        # Chama a view e captura a resposta
        response = view(request)
        
        # --- DEBUG: MOSTRA O ERRO REAL ---
        if response.status_code != 201:
            # Se falhar, queremos saber POR QUE falhou (Saldo? Validação? Rate Limit?)
            print(f"❌ Thread {index} Falhou: Status {response.status_code} | Erro: {response.data}")
            
    except Exception as e:
        print(f"💀 Thread {index} Erro Crítico: {e}")

def rodar_teste_carga():
    user, sorteio = reset_cenario()
    
    qtd_threads = 10 # 10 threads de R$ 10,00 = R$ 100,00 (Conta Exata)
    
    print(f"🚀 Iniciando Debug: {qtd_threads} threads tentando gastar R$ 10 cada.")
    print(f"💰 Saldo Inicial: R$ {user.saldo}")
    print("---------------------------------------------------")

    with ThreadPoolExecutor(max_workers=qtd_threads) as executor:
        futures = [executor.submit(tentar_apostar, user.id, sorteio.id, i) for i in range(qtd_threads)]
        for future in futures:
            future.result()

    user.refresh_from_db()
    apostas_feitas = Aposta.objects.filter(usuario=user).count()
    
    print("---------------------------------------------------")
    print(f"🏁 Fim do Teste.")
    print(f"💰 Saldo Final: R$ {user.saldo} (Esperado: R$ 0.00)")
    print(f"🎟️ Apostas Criadas: {apostas_feitas} (Esperado: 10)")
    
    if user.saldo == 0 and apostas_feitas == 10:
        print("\n🏆 SUCESSO ABSOLUTO: Fase 5 Aprovada.")
    else:
        print("\n⚠️ AINDA HÁ ERRO. Leia as mensagens acima.")

if __name__ == '__main__':
    rodar_teste_carga()