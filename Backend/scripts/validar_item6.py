import os
import django
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
import json
import random
from django.db import connection, IntegrityError

# Configuração do ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from games.models import Aposta, Sorteio
from accounts.models import CustomUser, MetricasDiarias
from django.core.management import call_command

def criar_cenario_teste():
    print("🛠️  Criando cenário de teste para ONTEM...")
    
    # Data de ontem (pois o script processa D-1)
    ontem = timezone.now() - timedelta(days=1)
    ontem_date = ontem.date()
    
    # 1. CRIAR SORTEIO FICTÍCIO (Com Fallback para Erro de Schema)
    try:
        sorteio_dummy, created = Sorteio.objects.get_or_create(
            data=ontem_date,
            horario='PTM',
            defaults={
                'fechado': True,
                'premio_1': '1234',
                'premio_2': '5678',
                'premio_3': '9012',
                'premio_4': '3456',
                'premio_5': '7890',
            }
        )
        msg = "criado" if created else "existente"
        print(f"   -> Sorteio {msg} via ORM.")
        
    except IntegrityError as e:
        print(f"⚠️  Aviso: O Banco de dados exige campos extras no Sorteio ({e}).")
        print("   -> Tentando contornar via SQL Direto...")
        
        # Se falhar, tentamos inserir via SQL Bruto preenchendo os campos 'invisíveis'
        # Assumindo que os campos faltantes são os de snapshot (acertos e tabelas)
        with connection.cursor() as cursor:
            # Verifica se já existe para não duplicar no erro
            cursor.execute("SELECT id FROM games_sorteio WHERE data = %s AND horario = %s", [ontem_date, 'PTM'])
            row = cursor.fetchone()
            
            if not row:
                cursor.execute("""
                    INSERT INTO games_sorteio 
                    (data, horario, fechado, premio_1, premio_2, premio_3, premio_4, premio_5, 
                     quininha_acertos_necessarios, seninha_acertos_necessarios, lotinha_acertos_necessarios,
                     tabela_quininha, tabela_seninha, tabela_lotinha)
                    VALUES 
                    (%s, %s, %s, '1234', '5678', '9012', '3456', '7890',
                     5, 6, 5, '{}', '{}', '{}')
                """, [ontem_date, 'PTM', True])
                print("   -> Sorteio inserido via SQL Bruto com sucesso!")
        
        # Recupera o objeto agora que existe
        sorteio_dummy = Sorteio.objects.get(data=ontem_date, horario='PTM')

    # 2. USUÁRIO DE TESTE
    user, _ = CustomUser.objects.get_or_create(username="teste_metricas", email="teste@metricas.com")
    
    # Limpar apostas antigas desse usuário na data de ontem
    Aposta.objects.filter(usuario=user, criado_em__date=ontem_date).delete()

    # --- SIMULAÇÃO DE APOSTAS ---
    
    # Aposta 1: Jogo do Bicho (Grupo) - PERDEU
    aposta1 = Aposta.objects.create(
        usuario=user,
        sorteio=sorteio_dummy, 
        tipo_jogo="G", # Grupo
        palpite="16",   
        valor=Decimal("100.00"),
        ganhou=False,
        valor_premio=Decimal("0.00")
    )
    Aposta.objects.filter(id=aposta1.id).update(criado_em=ontem)

    # Aposta 2: Milhar - GANHOU
    aposta2 = Aposta.objects.create(
        usuario=user,
        sorteio=sorteio_dummy,
        tipo_jogo="M", # Milhar
        palpite="1234",
        valor=Decimal("50.00"),
        ganhou=True,
        valor_premio=Decimal("10.00") 
    )
    Aposta.objects.filter(id=aposta2.id).update(criado_em=ontem)
    
    # Aposta 3: Milhar - PERDEU
    aposta3 = Aposta.objects.create(
        usuario=user,
        sorteio=sorteio_dummy,
        tipo_jogo="M", # Milhar
        palpite="5678",
        valor=Decimal("20.00"),
        ganhou=False,
        valor_premio=Decimal("0.00")
    )
    Aposta.objects.filter(id=aposta3.id).update(criado_em=ontem)

    print("✅ Apostas retroativas criadas com sucesso!")

def verificar_resultado():
    print("\n🚀 Executando processamento de métricas...")
    call_command('processar_metricas')
    
    ontem_date = timezone.localdate() - timedelta(days=1)
    try:
        metrica = MetricasDiarias.objects.get(data=ontem_date)
        json_dados = metrica.performance_modalidades
        
        print("\n📊 RESULTADO DO JSON (Item 6 - Lucratividade):")
        print("-" * 50)
        print(json.dumps(json_dados, indent=4))
        print("-" * 50)
        
        # Verificação rápida
        grupo_stats = json_dados.get('G', {}) 
        milhar_stats = json_dados.get('M', {}) 
        
        print(f"GRUPO (G) -> Apostado: 100 | Lucro Banca: {grupo_stats.get('lucro_banca')} (Esperado: 100.0)")
        print(f"MILHAR (M) -> Apostado: 70  | Lucro Banca: {milhar_stats.get('lucro_banca')} (Esperado: 60.0)")
        
    except MetricasDiarias.DoesNotExist:
        print("❌ Erro: Nenhuma métrica foi gerada para ontem.")

if __name__ == "__main__":
    try:
        criar_cenario_teste()
        verificar_resultado()
    except Exception as e:
        print(f"\n❌ Erro crítico: {e}")