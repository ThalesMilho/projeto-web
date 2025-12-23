from rest_framework import serializers
from .models import Aposta, Sorteio, Bicho

# --- SERIALIZER 1: Usado para listar os sorteios abertos (GET) ---
class SorteioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sorteio
        fields = ['id', 'data', 'horario', 'get_horario_display', 'fechado']

# --- SERIALIZER 2: Usado para validar a aposta (POST) ---
class CriarApostaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aposta
        fields = ['sorteio', 'tipo_jogo', 'valor', 'palpite']

    def validate(self, data):
        """
        Validações de Regra de Negócio antes de mexer no dinheiro.
        """
        user = self.context['request'].user
        sorteio = data['sorteio']
        valor_aposta = data['valor']

        # 1. Valida se tem saldo
        if user.saldo < valor_aposta:
            raise serializers.ValidationError({"saldo": "Saldo insuficiente para esta aposta."})

        # 2. Valida se o sorteio está fechado
        if sorteio.fechado:
            raise serializers.ValidationError({"sorteio": "Este sorteio já foi encerrado."})

        return data