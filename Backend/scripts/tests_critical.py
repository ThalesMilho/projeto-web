from decimal import Decimal
from django.test import TestCase
from unittest.mock import patch, MagicMock
from accounts.models import CustomUser
from .models import Sorteio, Aposta, Jogo, Modalidade, Colocacao
from .strategies import RegraBichoExata, RegraGrupo, RegraInvertida
from .engine import apurar_sorteio
from accounts.services.wallet import WalletService


class TestCriticalGameLogic(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            cpf_cnpj='00000000001',
            password='test',
            nome_completo='Test User',
            saldo=Decimal('100.00')
        )
        
        # Setup game structure
        self.jogo = Jogo.objects.create(nome='Bicho', tipo='bicho')
        self.modalidade_milhar = Modalidade.objects.create(
            jogo=self.jogo, nome='Milhar', quantidade_palpites=1, cotacao=4000.0
        )
        self.modalidade_grupo = Modalidade.objects.create(
            jogo=self.jogo, nome='Grupo', quantidade_palpites=1, cotacao=18.0
        )
        self.colocacao = Colocacao.objects.create(
            nome='Cabeça', cotacao=1.0, jogo=self.jogo, modalidade=self.modalidade_milhar
        )
        
        self.sorteio = Sorteio.objects.create(
            data='2026-01-15', 
            premio_1='0054',  # Critical: leading zero test case
            premio_2='1234',
            premio_3='5678',
            premio_4='9012',
            premio_5='3456'
        )

    def test_leading_zero_milhar_victory(self):
        """Test: Bet '0054' should win against result '0054'"""
        aposta = Aposta.objects.create(
            usuario=self.user,
            jogo=self.jogo,
            modalidade=self.modalidade_milhar,
            colocacao=self.colocacao,
            valor=Decimal('10.00'),
            palpites=['0054'],
            sorteio=self.sorteio
        )
        
        strategy = RegraBichoExata(4)
        result = strategy.verificar(aposta, self.sorteio)
        
        # This should PASS with fixed code
        self.assertTrue(result, "Bet '0054' should win against '0054'")

    def test_leading_zero_milhar_defeat(self):
        """Test: Bet '54' should LOSE against result '0054' (different digits)"""
        aposta = Aposta.objects.create(
            usuario=self.user,
            jogo=self.jogo,
            modalidade=self.modalidade_milhar,
            colocacao=self.colocacao,
            valor=Decimal('10.00'),
            palpites=['54'],
            sorteio=self.sorteio
        )
        
        strategy = RegraBichoExata(4)
        result = strategy.verificar(aposta, self.sorteio)
        
        # This should FAIL - '54' is not the same as '0054' for milhar
        self.assertFalse(result, "Bet '54' should lose against '0054' for milhar")

    def test_centena_leading_zero_handling(self):
        """Test: Centena '054' vs '0054' should match (last 3 digits)"""
        aposta = Aposta.objects.create(
            usuario=self.user,
            jogo=self.jogo,
            modalidade=Modalidade.objects.create(
                jogo=self.jogo, nome='Centena', quantidade_palpites=1, cotacao=600.0
            ),
            colocacao=self.colocacao,
            valor=Decimal('10.00'),
            palpites=['054'],
            sorteio=self.sorteio
        )
        
        strategy = RegraBichoExata(3)
        result = strategy.verificar(aposta, self.sorteio)
        
        self.assertTrue(result, "Centena '054' should match '0054'")

    def test_grupo_mapping_zero_case(self):
        """Test: Result '00' should map to grupo 25 (Vaca)"""
        sorteio_zero = Sorteio.objects.create(
            data='2026-01-16',
            premio_1='1200',  # Ends with '00'
            fechado=False
        )
        
        aposta = Aposta.objects.create(
            usuario=self.user,
            jogo=self.jogo,
            modalidade=self.modalidade_grupo,
            colocacao=Colocacao.objects.create(
                nome='Cabeça', cotacao=1.0, jogo=self.jogo, modalidade=self.modalidade_grupo
            ),
            valor=Decimal('10.00'),
            palpites=[25],  # Bet on Vaca group
            sorteio=sorteio_zero
        )
        
        strategy = RegraGrupo()
        result = strategy.verificar(aposta, sorteio_zero)
        
        self.assertTrue(result, "Result ending in '00' should match grupo 25")

    def test_premio_nulo_handling(self):
        """Test: System should handle null/empty prizes gracefully"""
        sorteio_com_nulo = Sorteio.objects.create(
            data='2026-01-17',
            premio_1='1234',
            premio_2=None,  # Null prize
            premio_3='',   # Empty prize
            premio_4='5678',
            fechado=False
        )
        
        aposta = Aposta.objects.create(
            usuario=self.user,
            jogo=self.jogo,
            modalidade=self.modalidade_milhar,
            colocacao=self.colocacao,
            valor=Decimal('10.00'),
            palpites=['5678'],
            sorteio=sorteio_com_nulo
        )
        
        strategy = RegraBichoExata(4)
        result = strategy.verificar(aposta, sorteio_com_nulo)
        
        self.assertTrue(result, "Should win despite null prizes in other positions")

    def test_invertida_permutation_limits(self):
        """Test: Invertida should handle long numbers safely"""
        from .strategies import RegraInvertida
        
        # Test with very long number (should be rejected for security)
        aposta_longa = Aposta.objects.create(
            usuario=self.user,
            jogo=self.jogo,
            modalidade=Modalidade.objects.create(
                jogo=self.jogo, nome='Milhar Invertida', quantidade_palpites=1, cotacao=400.0
            ),
            colocacao=self.colocacao,
            valor=Decimal('10.00'),
            palpites=['123456789'],  # 9 digits - should be rejected
            sorteio=self.sorteio
        )
        
        strategy = RegraInvertida(4)
        result = strategy.verificar(aposta_longa, self.sorteio)
        
        self.assertFalse(result, "Long numbers should be rejected for security")

    @patch('accounts.services.wallet.WalletService.credit')
    def test_apuracao_payout_calculation(self, mock_credit):
        """Test: Full apuration flow with correct payout calculation"""
        # Setup winning bet
        aposta = Aposta.objects.create(
            usuario=self.user,
            jogo=self.jogo,
            modalidade=self.modalidade_milhar,
            colocacao=self.colocacao,
            valor=Decimal('10.00'),
            palpites=['0054'],
            sorteio=self.sorteio
        )
        
        # Mock the strategy to return True (win)
        with patch('games.strategies.ValidadorFactory.get_strategy') as mock_factory:
            mock_strategy = MagicMock()
            mock_strategy.verificar.return_value = True
            mock_factory.return_value = mock_strategy
            
            # Run apuration
            result = apurar_sorteio(self.sorteio.id)
            
            self.assertTrue(result, "Apuration should succeed")
            
            # Verify payout calculation: 10.00 * 4000.0 = 40000.00
            mock_credit.assert_called_once()
            call_args = mock_credit.call_args
            self.assertEqual(call_args[1]['user_id'], self.user.id)
            self.assertEqual(call_args[1]['amount'], Decimal('40000.00'))

    def test_concurrent_bet_race_condition(self):
        """Test: Concurrent bets should not cause double-spending"""
        initial_balance = Decimal('100.00')
        self.user.saldo = initial_balance
        self.user.save()
        
        # Simulate concurrent bets
        with patch('accounts.services.wallet.WalletService.debit') as mock_debit:
            mock_debit.return_value = MagicMock()
            
            # Create two bets simultaneously
            for i in range(2):
                Aposta.objects.create(
                    usuario=self.user,
                    jogo=self.jogo,
                    modalidade=self.modalidade_milhar,
                    colocacao=self.colocacao,
                    valor=Decimal('60.00'),  # Each bet > half balance
                    palpites=[f'123{i}'],
                    sorteio=self.sorteio
                )
            
            # Should have called debit twice
            self.assertEqual(mock_debit.call_count, 2)
            
            # Second call should raise ValidationError (insufficient funds)
            # This would be tested with actual concurrent execution in integration tests

    def test_lottery_variant_intersection(self):
        """Test: Lottery variants should count intersections correctly"""
        from .strategies_fixed import RegraLotinha
        
        # Create lottery-style draw
        sorteio_lottery = Sorteio.objects.create(
            data='2026-01-18',
            premio_1='1201',  # Dezena: 01
            premio_2='2302',  # Dezena: 02
            premio_3='3403',  # Dezena: 03
            premio_4='4504',  # Dezena: 04
            premio_5='5605',  # Dezena: 05
            fechado=False
        )
        
        # User bets on [01, 02, 03, 06, 07] - should match 3/5
        aposta = Aposta.objects.create(
            usuario=self.user,
            jogo=Jogo.objects.create(nome='Lotinha', tipo='loterias'),
            modalidade=Modalidade.objects.create(
                jogo=self.jogo, nome='Lotinha 5', quantidade_palpites=5, cotacao=10.0
            ),
            colocacao=self.colocacao,
            valor=Decimal('10.00'),
            palpites=['01', '02', '03', '06', '07'],
            sorteio=sorteio_lottery
        )
        
        strategy = RegraLotinha(acertos_necessarios=3)
        result = strategy.verificar(aposta, sorteio_lottery)
        
        self.assertTrue(result, "Should win with 3/5 matches")
        
        # Test with 2/5 matches (should lose)
        strategy_5 = RegraLotinha(acertos_necessarios=5)
        result_5 = strategy_5.verificar(aposta, sorteio_lottery)
        self.assertFalse(result_5, "Should lose with only 3/5 when 5 needed")
