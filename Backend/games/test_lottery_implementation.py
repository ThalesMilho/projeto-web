"""
Comprehensive test suite for the new lottery variants implementation.
Tests the RegraLoteria class, ValidadorFactory, and serializer integration.
"""

from decimal import Decimal
from django.test import TestCase
from unittest.mock import patch, MagicMock
from accounts.models import CustomUser
from .models import Sorteio, Aposta, Jogo, Modalidade, Colocacao, ParametrosDoJogo
from .strategies import RegraLoteria, ValidadorFactory
from .utils import extract_numbers_from_string
from .serializer import CriarApostaSerializer


class TestRegraLoteria(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            cpf_cnpj='00000000001',
            password='test',
            nome_completo='Test User',
            saldo=Decimal('100.00')
        )
        
        # Create lottery-style draw
        self.sorteio = Sorteio.objects.create(
            data='2026-01-15',
            premio_1='1201',  # Dezena: 01
            premio_2='2302',  # Dezena: 02
            premio_3='3403',  # Dezena: 03
            premio_4='4504',  # Dezena: 04
            premio_5='5605',  # Dezena: 05
        )

    def test_extract_numbers_from_string_various_formats(self):
        """Test the utility function with different input formats"""
        # Test comma-separated
        self.assertEqual(extract_numbers_from_string("01, 02, 05"), [1, 2, 5])
        
        # Test hyphen-separated
        self.assertEqual(extract_numbers_from_string("1-2-3"), [1, 2, 3])
        
        # Test space-separated
        self.assertEqual(extract_numbers_from_string("1 2 3"), [1, 2, 3])
        
        # Test mixed separators
        self.assertEqual(extract_numbers_from_string("01, 02-03 04"), [1, 2, 3, 4])
        
        # Test single number with leading zero
        self.assertEqual(extract_numbers_from_string("05"), [5])
        
        # Test empty/invalid inputs
        self.assertEqual(extract_numbers_from_string(""), [])
        self.assertEqual(extract_numbers_from_string(None), [])
        self.assertEqual(extract_numbers_from_string("abc"), [])
        
        # Test numbers outside range (should be filtered)
        self.assertEqual(extract_numbers_from_string("150"), [])

    def test_regra_loteria_exact_match(self):
        """Test exact match scenario"""
        aposta = Aposta.objects.create(
            usuario=self.user,
            jogo=Jogo.objects.create(nome='Lotinha', tipo='loterias'),
            modalidade=Modalidade.objects.create(
                jogo=Jogo.objects.create(nome='Test', tipo='loterias'), 
                nome='Lotinha 5', 
                quantidade_palpites=5, 
                cotacao=10.0
            ),
            valor=Decimal('10.00'),
            palpites=['01', '02', '03', '04', '05'],
            sorteio=self.sorteio
        )
        
        strategy = RegraLoteria(5)  # Need 5 matches to win
        result = strategy.verificar(aposta, self.sorteio)
        
        self.assertTrue(result, "Should win with exact 5/5 matches")

    def test_regra_loteria_partial_match(self):
        """Test partial match scenario"""
        aposta = Aposta.objects.create(
            usuario=self.user,
            jogo=Jogo.objects.create(nome='Quininha', tipo='loterias'),
            modalidade=Modalidade.objects.create(
                jogo=Jogo.objects.create(nome='Test', tipo='loterias'), 
                nome='Quininha 4', 
                quantidade_palpites=4, 
                cotacao=15.0
            ),
            valor=Decimal('10.00'),
            palpites=['01', '02', '03', '06'],  # Only 3 matches
            sorteio=self.sorteio
        )
        
        strategy = RegraLoteria(4)  # Need 4 matches to win
        result = strategy.verificar(aposta, self.sorteio)
        
        self.assertFalse(result, "Should lose with only 3/4 matches")

    def test_regra_loteria_list_input_format(self):
        """Test with list input format (JSON)"""
        aposta = Aposta.objects.create(
            usuario=self.user,
            jogo=Jogo.objects.create(nome='Seninha', tipo='loterias'),
            modalidade=Modalidade.objects.create(
                jogo=Jogo.objects.create(nome='Test', tipo='loterias'), 
                nome='Seninha 6', 
                quantidade_palpites=6, 
                cotacao=20.0
            ),
            valor=Decimal('10.00'),
            palpites=[1, 2, 3, 4, 5, 6],  # List of ints
            sorteio=self.sorteio
        )
        
        strategy = RegraLoteria(6)  # Need 6 matches to win
        result = strategy.verificar(aposta, self.sorteio)
        
        self.assertTrue(result, "Should win with 6/6 matches using int list")

    def test_regra_loteria_string_input_format(self):
        """Test with string input format (legacy)"""
        aposta = Aposta.objects.create(
            usuario=self.user,
            jogo=Jogo.objects.create(nome='Lotinha', tipo='loterias'),
            modalidade=Modalidade.objects.create(
                jogo=Jogo.objects.create(nome='Test', tipo='loterias'), 
                nome='Lotinha 3', 
                quantidade_palpites=3, 
                cotacao=8.0
            ),
            valor=Decimal('10.00'),
            palpites="01, 02, 03",  # String format
            sorteio=self.sorteio
        )
        
        strategy = RegraLoteria(3)  # Need 3 matches to win
        result = strategy.verificar(aposta, self.sorteio)
        
        self.assertTrue(result, "Should win with string format input")

    def test_regra_loteria_no_match(self):
        """Test complete miss scenario"""
        aposta = Aposta.objects.create(
            usuario=self.user,
            jogo=Jogo.objects.create(nome='Lotinha', tipo='loterias'),
            modalidade=Modalidade.objects.create(
                jogo=Jogo.objects.create(nome='Test', tipo='loterias'), 
                nome='Lotinha 2', 
                quantidade_palpites=2, 
                cotacao=5.0
            ),
            valor=Decimal('10.00'),
            palpites=['11', '12'],  # No matches
            sorteio=self.sorteio
        )
        
        strategy = RegraLoteria(2)  # Need 2 matches to win
        result = strategy.verificar(aposta, self.sorteio)
        
        self.assertFalse(result, "Should lose with 0/2 matches")

    def test_regra_loteria_error_handling(self):
        """Test error handling with invalid inputs"""
        # Test with None palpite
        aposta_invalid = Aposta.objects.create(
            usuario=self.user,
            jogo=Jogo.objects.create(nome='Test', tipo='loterias'),
            modalidade=Modalidade.objects.create(
                jogo=Jogo.objects.create(nome='Test', tipo='loterias'), 
                nome='Test', 
                quantidade_palpites=1, 
                cotacao=1.0
            ),
            valor=Decimal('10.00'),
            palpites=None,
            sorteio=self.sorteio
        )
        
        strategy = RegraLoteria(1)
        result = strategy.verificar(aposta_invalid, self.sorteio)
        
        self.assertFalse(result, "Should handle None palpite gracefully")

    def test_validador_factory_lottery_variants(self):
        """Test ValidadorFactory integration"""
        # Test Lotinha
        modalidade_lotinha = Modalidade.objects.create(
            jogo=Jogo.objects.create(nome='Test', tipo='loterias'),
            nome='Lotinha',
            cotacao=10.0
        )
        strategy = ValidadorFactory.get_strategy(modalidade_lotinha)
        self.assertIsInstance(strategy, RegraLoteria)
        self.assertEqual(strategy.quantidade_acertos_necessarios, 15)  # Default

        # Test Quininha
        modalidade_quininha = Modalidade.objects.create(
            jogo=Jogo.objects.create(nome='Test', tipo='loterias'),
            nome='Quininha',
            cotacao=15.0
        )
        strategy = ValidadorFactory.get_strategy(modalidade_quininha)
        self.assertIsInstance(strategy, RegraLoteria)
        self.assertEqual(strategy.quantidade_acertos_necessarios, 5)  # Default

        # Test Seninha
        modalidade_seninha = Modalidade.objects.create(
            jogo=Jogo.objects.create(nome='Test', tipo='loterias'),
            nome='Seninha',
            cotacao=20.0
        )
        strategy = ValidadorFactory.get_strategy(modalidade_seninha)
        self.assertIsInstance(strategy, RegraLoteria)
        self.assertEqual(strategy.quantidade_acertos_necessarios, 6)  # Default

    def test_validador_factory_with_config_parameters(self):
        """Test ValidadorFactory with database configuration"""
        # Setup config
        config = ParametrosDoJogo.load()
        config.lotinha_acertos_necessarios = 20
        config.quininha_acertos_necessarios = 4
        config.seninha_acertos_necessarios = 7
        config.save()
        
        # Test Lotinha with custom config
        modalidade_lotinha = Modalidade.objects.create(
            jogo=Jogo.objects.create(nome='Test', tipo='loterias'),
            nome='Lotinha Custom',
            cotacao=10.0
        )
        strategy = ValidadorFactory.get_strategy(modalidade_lotinha)
        self.assertIsInstance(strategy, RegraLoteria)
        self.assertEqual(strategy.quantidade_acertos_necessarios, 20)  # From config

    def test_serializer_lottery_mapping(self):
        """Test serializer mapping for lottery variants"""
        # Test Lotinha mapping
        modalidade = Modalidade.objects.create(
            jogo=Jogo.objects.create(nome='Test', tipo='loterias'),
            nome='Lotinha',
            cotacao=10.0
        )
        
        serializer = CriarApostaSerializer()
        resolved = serializer._resolve_modalidade('L')
        self.assertEqual(resolved, modalidade)

        # Test Quininha mapping
        modalidade_quininha = Modalidade.objects.create(
            jogo=Jogo.objects.create(nome='Test', tipo='loterias'),
            nome='Quininha',
            cotacao=15.0
        )
        resolved = serializer._resolve_modalidade('Q')
        self.assertEqual(resolved, modalidade_quininha)

        # Test Seninha mapping
        modalidade_seninha = Modalidade.objects.create(
            jogo=Jogo.objects.create(nome='Test', tipo='loterias'),
            nome='Seninha',
            cotacao=20.0
        )
        resolved = serializer._resolve_modalidade('S')
        self.assertEqual(resolved, modalidade_seninha)


class TestLotteryPerformance(TestCase):
    """Performance tests for the lottery implementation"""
    
    def setUp(self):
        # Create a large draw for performance testing
        self.sorteio = Sorteio.objects.create(
            data='2026-01-15',
            premio_1='1201', premio_2='2302', premio_3='3403', premio_4='4504', premio_5='5605',
        )
        
        self.user = CustomUser.objects.create_user(
            cpf_cnpj='00000000001',
            password='test',
            nome_completo='Test User',
            saldo=Decimal('1000.00')
        )

    def test_performance_large_bet_sets(self):
        """Test performance with large bet sets"""
        import time
        
        # Create a bet with many numbers
        large_palpites = [str(i).zfill(2) for i in range(1, 51)]  # 50 numbers
        
        aposta = Aposta.objects.create(
            usuario=self.user,
            jogo=Jogo.objects.create(nome='Test', tipo='loterias'),
            modalidade=Modalidade.objects.create(
                jogo=Jogo.objects.create(nome='Test', tipo='loterias'), 
                nome='Large Bet', 
                quantidade_palpites=50, 
                cotacao=100.0
            ),
            valor=Decimal('50.00'),
            palpites=large_palpites,
            sorteio=self.sorteio
        )
        
        strategy = RegraLoteria(5)
        
        # Measure execution time
        start_time = time.time()
        result = strategy.verificar(aposta, self.sorteio)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Should complete quickly even with large sets
        self.assertLess(execution_time, 0.1, "Large bet processing should be fast")
        self.assertTrue(result, "Should win with 5+ matches in large set")

    def test_performance_set_operations(self):
        """Test that set operations are indeed being used"""
        # This is more of a design verification test
        strategy = RegraLoteria(5)
        
        # Verify the method uses set operations (by checking the implementation)
        # This is a simple check - in real scenarios you might want more sophisticated testing
        import inspect
        source = inspect.getsource(strategy.verificar)
        
        self.assertIn('intersection', source, "Should use set intersection for performance")
        self.assertIn('set()', source, "Should use set data structure")
