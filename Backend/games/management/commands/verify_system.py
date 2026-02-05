import sys
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction

# Imports do Domínio
from games.models import Jogo, Modalidade, Sorteio, Aposta
from accounts.models import Transacao
from games.serializer import CriarApostaSerializer
from games.engine import apurar_sorteio
from accounts.services.wallet import WalletService

class Command(BaseCommand):
    help = 'Executa teste de integridade End-to-End (Adapter -> Wallet -> Engine)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('=== INICIANDO VERIFICACAO DE SISTEMA (BACKEND) ==='))
        
        try:
            # Atomicidade: Se qualquer passo falhar, nada é salvo no banco (Rollback).
            # Isso mantem seu banco de desenvolvimento limpo em caso de erro.
            with transaction.atomic():
                
                # 1. SETUP
                user, jogo, modalidade, sorteio = self._setup_environment()
                
                # 2. TESTE DO ADAPTER & DEBITO
                aposta = self._test_bet_creation_flow(user, sorteio, jogo, modalidade)
                
                # 3. TESTE DE PERSISTENCIA
                self._test_persistence_integrity(aposta, jogo, modalidade)
                
                # 4. TESTE DO MOTOR DE PAGAMENTO
                self._test_payout_engine(user, aposta, sorteio)
                
                # Se chegou aqui, sucesso total.
                self.stdout.write(self.style.SUCCESS('\n>>> SUCESSO: O SISTEMA ESTA INTEGRO E PRONTO PARA PRODUCAO.'))
                
                # Opcional: Se quiser que os dados de teste sumam depois do sucesso, descomente a linha abaixo:
                # raise Exception("Rollback Intencional (Limpeza de Teste)")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n[FALHA CRITICA]: {str(e)}'))
            # Descomente para ver o stacktrace completo se precisar debugar
            # import traceback
            # traceback.print_exc()
            sys.exit(1)

    def _setup_environment(self):
        self.stdout.write("\n[1] Configurando Ambiente de Teste...")
        User = get_user_model()
        
        # Cria ou Pega Usuário
        user, _ = User.objects.get_or_create(username='qa_tester', defaults={'email': 'qa@teste.com'})
        # Reseta o saldo para garantir previsibilidade matemática
        user.saldo = Decimal('1000.00')
        user.save()
        self.stdout.write(f" - Usuario: {user.username} | Saldo Inicial: R$ {user.saldo}")

        # Configura Jogo e Modalidade (Vital para o Adapter funcionar)
        jogo, _ = Jogo.objects.get_or_create(nome='Bicho', defaults={'ativo': True, 'tipo': 'bicho'})
        
        # O Adapter busca por 'Milhar' quando recebe 'M'. Tem que existir exato.
        modalidade, _ = Modalidade.objects.get_or_create(
            jogo=jogo, 
            nome='Milhar', 
            defaults={'cotacao': 4000.00, 'quantidade_palpites': 1}
        )
        
        # Configura Sorteio Aberto
        sorteio, _ = Sorteio.objects.get_or_create(
            data=timezone.now().date(),
            defaults={'fechado': False}
        )
        sorteio.fechado = False
        sorteio.resultado = None # Limpa resultado anterior
        sorteio.save()
        
        return user, jogo, modalidade, sorteio

    def _test_bet_creation_flow(self, user, sorteio, jogo, modalidade):
        self.stdout.write("\n[2] Testando Fluxo de Criacao (Adapter + Wallet)...")
        
        # Payload LEGADO (Simulando o Frontend atual)
        payload = {
            'tipo_jogo': 'M',        # O Adapter deve traduzir isso para modalidade_id
            'palpite': '1234',       # O Adapter deve transformar em ['1234']
            'valor': 10.00,
            'sorteio': sorteio.id
        }
        
        # 2.1 Validação e Adaptação (Serializer)
        serializer = CriarApostaSerializer(data=payload)
        if not serializer.is_valid():
            raise Exception(f"Erro de Validacao no Serializer: {serializer.errors}")

        validated = serializer.validated_data
        
        # Verificação do Adapter (Tradução)
        if validated.get('modalidade') != modalidade:
            raise Exception(f"Falha no Adapter: Recebeu 'M' mas nao resolveu para a Modalidade 'Milhar'. Resolveu para: {validated.get('modalidade')}")
        
        if validated.get('palpites') != ['1234']:
            raise Exception(f"Falha na Normalizacao de Palpites: Esperado ['1234'], Recebido {validated.get('palpites')}")

        self.stdout.write(" - Adapter OK: Traduziu dados legados corretamente.")

        # 2.2 Cobrança (WalletService) - Simulando a View
        # Aqui estava o erro do teste anterior. O dinheiro tem que sair AGORA.
        WalletService.debit(user.id, validated['valor'], 'APOSTA', 'Teste Automatizado')
        
        # Verifica Saldo Imediato
        user.refresh_from_db()
        expected_balance = Decimal('1000.00') - Decimal('10.00')
        if user.saldo != expected_balance:
            raise Exception(f"Falha na Carteira: Saldo esperado {expected_balance}, Atual {user.saldo}")
        self.stdout.write(" - Wallet OK: Debito realizado com sucesso.")

        # 2.3 Persistência (Save)
        aposta = serializer.save(usuario=user)
        self.stdout.write(f" - Aposta Criada: ID {aposta.id}")
        
        return aposta

    def _test_persistence_integrity(self, aposta, jogo, modalidade):
        self.stdout.write("\n[3] Verificando Integridade no Banco de Dados...")
        aposta.refresh_from_db()
        
        # Verifica se as chaves estrangeiras foram salvas corretamente
        if aposta.jogo != jogo:
            raise Exception("Integridade de Dados Falhou: Campo 'jogo' incorreto.")
        if aposta.modalidade != modalidade:
            raise Exception("Integridade de Dados Falhou: Campo 'modalidade' incorreto.")
        
        # Verifica se existe o registro financeiro (Auditabilidade)
        tx = Transacao.objects.filter(usuario=aposta.usuario, tipo='APOSTA', valor=aposta.valor).last()
        if not tx:
            raise Exception("Auditabilidade Falhou: Dinheiro saiu, mas nao ha registro de Transacao 'APOSTA'.")
            
        self.stdout.write(" - Persistencia OK: Dados normalizados e Transacao registrada.")

    def _test_payout_engine(self, user, aposta, sorteio):
        self.stdout.write("\n[4] Testando Motor de Premiacao (Win Scenario)...")
        
        # --- 4.1 DATA SETUP (The Fix) ---
        # Define winning numbers. The first one '1234' matches our test bet.
        winning_numbers = ['1234', '5555', '6666', '7777', '8888']
        
        # Sync New Schema (JSON)
        sorteio.resultado = winning_numbers
        
        # Sync Legacy Schema (Columns) - Critical for Strategy Compatibility
        # We explicitly map first 5 prizes to legacy columns
        sorteio.premio_1 = winning_numbers[0]
        sorteio.premio_2 = winning_numbers[1]
        sorteio.premio_3 = winning_numbers[2]
        sorteio.premio_4 = winning_numbers[3]
        sorteio.premio_5 = winning_numbers[4]
        
        sorteio.save()
        self.stdout.write(f" - Sorteio Result Synced: JSON={len(sorteio.resultado)} items | Legacy premio_1={sorteio.premio_1}")

        # --- 4.2 EXECUTION ---
        self.stdout.write(" - Executing apurar_sorteio()...")
        apurar_sorteio(sorteio.id)
        
        # --- 4.3 ASSERTIONS ---
        aposta.refresh_from_db()
        
        # A. Win Status Check
        if not aposta.ganhou:
            self.stdout.write(self.style.ERROR(f"DEBUG DATA: Bet Palpites: {aposta.palpites}"))
            self.stdout.write(self.style.ERROR(f"DEBUG DATA: Sorteio Premio 1: {sorteio.premio_1}"))
            raise Exception("Engine Logic Failure: The bet matched 'premio_1' but was not marked as WON.")
        
        # B. Prize Calculation Check (Precision)
        # Expected: 10.00 * 4000.00 = 40,000.00
        expected_prize = Decimal(str(aposta.valor)) * Decimal(str(aposta.modalidade.cotacao))
        if abs(aposta.valor_premio - expected_prize) > Decimal('0.01'):
             raise Exception(f"Math Failure: Calculated {aposta.valor_premio}, Expected {expected_prize}")

        # C. Wallet Credit Check
        user.refresh_from_db()
        # Initial 1000 - 10 (Bet) + 40000 (Prize) = 40990
        expected_balance = Decimal('990.00') + expected_prize
        
        if user.saldo != expected_balance:
            raise Exception(f"Wallet Failure: Final Balance is {user.saldo}, Expected {expected_balance}")
            
        # D. Audit Trail Check
        tx_premio = Transacao.objects.filter(usuario=user, tipo='PREMIO', valor=expected_prize).last()
        if not tx_premio:
             raise Exception("Audit Failure: Prize credited but no 'PREMIO' transaction record found.")

        self.stdout.write(self.style.SUCCESS(f" - Engine OK: Bet Won. Prize R$ {aposta.valor_premio} credited."))
        self.stdout.write(self.style.SUCCESS(f" - Final User Balance: R$ {user.saldo}"))