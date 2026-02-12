"""
Simple working test for lottery implementation.
"""

from decimal import Decimal
from django.test import TestCase
from accounts.models import CustomUser
from .models import Sorteio, Aposta, Jogo, Modalidade
from .strategies import RegraLoteria, ValidadorFactory
from .utils import extract_numbers_from_string


class TestLotterySimple(TestCase):
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

    def test_extract_numbers_from_string_basic(self):
        """Test the utility function basic functionality"""
        self.assertEqual(extract_numbers_from_string("01, 02, 05"), [1, 2, 5])
        self.assertEqual(extract_numbers_from_string("1-2-3"), [1, 2, 3])
        self.assertEqual(extract_numbers_from_string("05"), [5])

    def test_regra_loteria_basic_functionality(self):
        """Test RegraLoteria basic functionality"""
        jogo = Jogo.objects.create(nome='Test', tipo='loterias')
        modalidade = Modalidade.objects.create(
            jogo=jogo, 
            nome='Test Loteria', 
            quantidade_palpites=5, 
            cotacao=10.0
        )
        
        aposta = Aposta.objects.create(
            usuario=self.user,
            jogo=jogo,
            modalidade=modalidade,
            valor=Decimal('10.00'),
            palpites=['01', '02', '03', '04', '05'],
            sorteio=self.sorteio,
            tipo_jogo='L'  # Add legacy field to avoid constraint
        )
        
        strategy = RegraLoteria(5)
        result = strategy.verificar(aposta, self.sorteio)
        
        self.assertTrue(result, "Should win with 5/5 matches")

    def test_regra_loteria_losing_scenario(self):
        """Test RegraLoteria losing scenario"""
        jogo = Jogo.objects.create(nome='Test', tipo='loterias')
        modalidade = Modalidade.objects.create(
            jogo=jogo, 
            nome='Test Loteria Lose', 
            quantidade_palpites=3, 
            cotacao=8.0
        )
        
        aposta = Aposta.objects.create(
            usuario=self.user,
            jogo=jogo,
            modalidade=modalidade,
            valor=Decimal('10.00'),
            palpites=['11', '12', '13'],  # No matches
            sorteio=self.sorteio,
            tipo_jogo='L'  # Add legacy field to avoid constraint
        )
        
        strategy = RegraLoteria(3)
        result = strategy.verificar(aposta, self.sorteio)
        
        self.assertFalse(result, "Should lose with 0/3 matches")

    def test_validador_factory_basic(self):
        """Test ValidadorFactory basic integration"""
        jogo = Jogo.objects.create(nome='Test', tipo='loterias')
        
        # Test Lotinia
        modalidade_lotinha = Modalidade.objects.create(
            jogo=jogo,
            nome='Lotinha Test',
            cotacao=10.0
        )
        strategy = ValidadorFactory.get_strategy(modalidade_lotinha)
        self.assertIsInstance(strategy, RegraLoteria)
        
        # Test Quininha
        modalidade_quininha = Modalidade.objects.create(
            jogo=jogo,
            nome='Quininha Test',
            cotacao=15.0
        )
        strategy = ValidadorFactory.get_strategy(modalidade_quininha)
        self.assertIsInstance(strategy, RegraLoteria)
        
        # Test Seninha
        modalidade_seninha = Modalidade.objects.create(
            jogo=jogo,
            nome='Seninha Test',
            cotacao=20.0
        )
        strategy = ValidadorFactory.get_strategy(modalidade_seninha)
        self.assertIsInstance(strategy, RegraLoteria)
