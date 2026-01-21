from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from accounts.models import CustomUser, Transacao
from .models import Sorteio, Aposta, ParametrosDoJogo
from .views import ApostaViewSet


class TestApostaComissao(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        # Garantir sistema ativo
        config = ParametrosDoJogo.load()
        config.ativa_apostas = True
        config.save()

        # Sorteio aberto
        self.sorteio = Sorteio.objects.create(data='2026-01-15', horario='PT', fechado=False)

        # Usuários
        self.jogador = CustomUser.objects.create_user(cpf_cnpj='00000000001', password='test', nome_completo='Jogador', saldo=Decimal('100.00'))
        self.cambista = CustomUser.objects.create_user(cpf_cnpj='00000000002', password='test', nome_completo='Cambista', saldo=Decimal('100.00'), tipo_usuario='CAMBISTA', comissao_percentual=Decimal('15.00'))

    def test_arredondamento_comissao_dizima(self):
        """R$10 x 33.33% = 3.333 -> quantize -> 3.33 (ROUND_DOWN)"""
        # Ajusta percentuais para o cenário
        self.cambista.comissao_percentual = Decimal('33.33')
        self.cambista.save()

        data = {'sorteio': self.sorteio.pk, 'tipo_jogo': 'G', 'valor': '10.00', 'palpite': '16'}
        request = self.factory.post('/', data, format='json')
        force_authenticate(request, user=self.cambista)

        view = ApostaViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, 201)

        aposta = Aposta.objects.latest('criado_em')
        # Comissão esperada: 10 * 0.3333 = 3.333 -> 3.33
        self.assertEqual(aposta.comissao_gerada, Decimal('3.33'))

    def test_cambista_comissao_15_porcento(self):
        data = {'sorteio': self.sorteio.pk, 'tipo_jogo': 'G', 'valor': '100.00', 'palpite': '16'}
        request = self.factory.post('/', data, format='json')
        force_authenticate(request, user=self.cambista)

        view = ApostaViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, 201)

        aposta = Aposta.objects.latest('criado_em')
        # 15% de 100 = 15.00
        self.assertEqual(aposta.comissao_gerada, Decimal('15.00'))

    def test_jogador_sem_comissao(self):
        data = {'sorteio': self.sorteio.pk, 'tipo_jogo': 'G', 'valor': '50.00', 'palpite': '16'}
        request = self.factory.post('/', data, format='json')
        force_authenticate(request, user=self.jogador)

        view = ApostaViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, 201)

        aposta = Aposta.objects.latest('criado_em')
        self.assertEqual(aposta.comissao_gerada, Decimal('0.00'))

    def test_saldo_insuficiente(self):
        # Jogador com saldo baixo
        self.jogador.saldo = Decimal('1.00')
        self.jogador.save()

        data = {'sorteio': self.sorteio.pk, 'tipo_jogo': 'G', 'valor': '50.00', 'palpite': '16'}
        request = self.factory.post('/', data, format='json')
        force_authenticate(request, user=self.jogador)

        view = ApostaViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, 400)

    def test_sorteio_fechado(self):
        self.sorteio.fechado = True
        self.sorteio.save()

        data = {'sorteio': self.sorteio.pk, 'tipo_jogo': 'G', 'valor': '10.00', 'palpite': '16'}
        request = self.factory.post('/', data, format='json')
        force_authenticate(request, user=self.cambista)

        view = ApostaViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, 400)

    def test_antispam_duplicated_bet(self):
        data = {'sorteio': self.sorteio.pk, 'tipo_jogo': 'G', 'valor': '10.00', 'palpite': '16'}
        request1 = self.factory.post('/', data, format='json')
        force_authenticate(request1, user=self.jogador)
        view = ApostaViewSet.as_view({'post': 'create'})
        resp1 = view(request1)
        self.assertEqual(resp1.status_code, 201)

        # Immediate duplicate should be blocked (within 5s)
        request2 = self.factory.post('/', data, format='json')
        force_authenticate(request2, user=self.jogador)
        resp2 = view(request2)
        self.assertEqual(resp2.status_code, 400)

    def test_kill_switch_system_off(self):
        config = ParametrosDoJogo.load()
        config.ativa_apostas = False
        config.save()

        data = {'sorteio': self.sorteio.pk, 'tipo_jogo': 'G', 'valor': '10.00', 'palpite': '16'}
        request = self.factory.post('/', data, format='json')
        force_authenticate(request, user=self.cambista)

        view = ApostaViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, 503)

    def test_cambista_zero_percent_edgecase(self):
        self.cambista.comissao_percentual = Decimal('0.00')
        self.cambista.save()

        data = {'sorteio': self.sorteio.pk, 'tipo_jogo': 'G', 'valor': '100.00', 'palpite': '16'}
        request = self.factory.post('/', data, format='json')
        force_authenticate(request, user=self.cambista)

        view = ApostaViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, 201)

        aposta = Aposta.objects.latest('criado_em')
        self.assertEqual(aposta.comissao_gerada, Decimal('0.00'))

    def test_multiples_apostas_acumulando(self):
        # Cambista com 10% comissão, saldo inicial 200
        self.cambista.saldo = Decimal('200.00')
        self.cambista.comissao_percentual = Decimal('10.00')
        self.cambista.save()

        view = ApostaViewSet.as_view({'post': 'create'})

        data1 = {'sorteio': self.sorteio.pk, 'tipo_jogo': 'G', 'valor': '50.00', 'palpite': '16'}
        req1 = self.factory.post('/', data1, format='json')
        force_authenticate(req1, user=self.cambista)
        r1 = view(req1)
        self.assertEqual(r1.status_code, 201)

        data2 = {'sorteio': self.sorteio.pk, 'tipo_jogo': 'G', 'valor': '30.00', 'palpite': '17'}
        req2 = self.factory.post('/', data2, format='json')
        force_authenticate(req2, user=self.cambista)
        r2 = view(req2)
        self.assertEqual(r2.status_code, 201)

        # Saldo esperado: 200 -50 +5 -30 +3 = 128.00
        self.cambista.refresh_from_db()
        self.assertEqual(self.cambista.saldo, Decimal('128.00'))

    def test_transacoes_sequenciais(self):
        # Verifica criação de transações e consistência de snapshot
        self.cambista.saldo = Decimal('100.00')
        self.cambista.comissao_percentual = Decimal('10.00')
        self.cambista.save()

        view = ApostaViewSet.as_view({'post': 'create'})
        data = {'sorteio': self.sorteio.pk, 'tipo_jogo': 'G', 'valor': '20.00', 'palpite': '16'}
        req = self.factory.post('/', data, format='json')
        force_authenticate(req, user=self.cambista)
        resp = view(req)
        self.assertEqual(resp.status_code, 201)

        # Últimas transações devem conter COMISSAO e APOSTA
        txs = Transacao.objects.filter(usuario=self.cambista).order_by('data')
        self.assertTrue(txs.count() >= 2)
        last_aposta = txs.filter(tipo='APOSTA').last()
        self.assertIsNotNone(last_aposta)
        # saldo_posterior - saldo_anterior == -valor_aposta (already applied commissions separately)
        self.assertEqual(last_aposta.valor, Decimal('20.00'))
