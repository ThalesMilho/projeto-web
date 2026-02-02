from decimal import Decimal
from datetime import datetime
from rest_framework import serializers
from .models import Aposta, Sorteio, ParametrosDoJogo, Jogo, Modalidade, Colocacao
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes

# --- SERIALIZER 1: Listar sorteios (GET) ---
class SorteioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sorteio
        fields = ['id', 'data', 'horario', 'get_horario_display', 'fechado', 'premio_1']

# --- SERIALIZER 2: Validar e Criar aposta (POST) ---
# Em Backend/games/serializer.py

class CriarApostaSerializer(serializers.ModelSerializer):
    # Recebemos IDs ao invés de strings mágicas
    jogo_id = serializers.PrimaryKeyRelatedField(queryset=Jogo.objects.filter(ativo=True), source='jogo')
    modalidade_id = serializers.PrimaryKeyRelatedField(queryset=Modalidade.objects.all(), source='modalidade')
    colocacao_id = serializers.PrimaryKeyRelatedField(queryset=Colocacao.objects.all(), required=False, source='colocacao', allow_null=True)
    
    # Palpites agora é uma lista/JSON
    palpites = serializers.JSONField()
    
    class Meta:
        model = Aposta
        # Atualizado para refletir novos nomes de campos do diagrama
        fields = [
            'sorteio', 
            'jogo_id', 
            'modalidade_id', 
            'colocacao_id', 
            'valor_aposta', # Mudou de 'valor'
            'palpites', 
            # 'status' geralmente é read-only na criação
        ]

    def validate(self, data):
        # Validação de integridade entre Jogo/Modalidade/Colocação
        # Agora Colocação também depende do Jogo/Modalidade no diagrama
        if data.get('colocacao'):
            if data['colocacao'].jogo != data['jogo']:
                raise serializers.ValidationError("A colocação não pertence a este jogo.")

        # ... manter validações de palpites ...

        # 2. Validação do JSON de palpites (evita schema lixo no banco)
        palpites = data['palpites']
        if not isinstance(palpites, list):
            raise serializers.ValidationError({"palpites": "O campo deve ser uma lista (array). Ex: ['1234']"})
        
        if len(palpites) == 0:
            raise serializers.ValidationError({"palpites": "A lista de palpites não pode estar vazia."})

        # Ajuste: buscar qtd usando o nome correto do campo
        qtd_exigida = data['modalidade'].quantidade_palpites # Mudou de quantidade_numeros

        # Validação por tipo de jogo (Bicho vs Loto/Loterias)
        jogo_tipo = getattr(data.get('jogo'), 'tipo', None)

        for p in palpites:
            # Se a modalidade exige múltiplos números por palpite, cada item deve ser array/tuple
            if qtd_exigida and qtd_exigida > 1:
                if not (isinstance(p, (list, tuple)) and len(p) == qtd_exigida):
                    raise serializers.ValidationError({
                        "palpites": f"Cada palpite deve ser uma lista de {qtd_exigida} números."})
                for sub in p:
                    if not str(sub).isdigit():
                        raise serializers.ValidationError(f"Palpite inválido: {sub}. Apenas números permitidos.")
            else:
                # itens simples: devem ser strings/digits com tamanho razoável
                if isinstance(p, (list, tuple)):
                    raise serializers.ValidationError({"palpites": "Formato inválido: esperado item simples, recebeu lista."})
                if not str(p).isdigit():
                    raise serializers.ValidationError(f"Palpite inválido: {p}. Apenas números.")
                # Regras adicionais por tipo de jogo (ex.: Bicho aceita 1-4 dígitos)
                if jogo_tipo == 'bicho':
                    if not (1 <= len(str(p)) <= 4):
                        raise serializers.ValidationError({"palpites": "No Jogo do Bicho, palpites devem ter 1 a 4 dígitos."})
                elif jogo_tipo in ('loto', 'loterias'):
                    # Para loterias, forçar 2 dígitos (dezenas) ou números entre 1-99
                    if not (1 <= len(str(p)) <= 2):
                        raise serializers.ValidationError({"palpites": "Em loterias, palpites devem ter 1 ou 2 dígitos (dezenas)."})
        # Para jogos simples (1 palpite = 1 aposta), verificamos o formato de cada item
        # Para jogos compostos (1 palpite = array de 3 números), a lógica valida o tamanho do array
        
        # Exemplo simples: valida se é numérico
        for p in palpites:
            if not str(p).isdigit():
                raise serializers.ValidationError(f"Palpite inválido: {p}. Apenas números.")

        return data

    def create(self, validated_data):
        # Ao criar, preenchemos o data_sorteio baseado no objeto sorteio
        sorteio = validated_data.get('sorteio')
        validated_data['data_sorteio'] = datetime.combine(sorteio.data, datetime.min.time()) # Exemplo
        return super().create(validated_data)

# --- SERIALIZER 3: NOVO - Para ver os detalhes e se ganhou (GET) ---
class ApostaDetalheSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    nome_sorteio = serializers.CharField(source='sorteio.__str__', read_only=True)
    
    # Exibir nomes legíveis ao invés de IDs
    nome_jogo = serializers.CharField(source='jogo.nome', read_only=True)
    nome_modalidade = serializers.CharField(source='modalidade.nome', read_only=True)
    nome_colocacao = serializers.CharField(source='colocacao.nome', read_only=True, allow_null=True)

    class Meta:
        model = Aposta
        # [ATENÇÃO] Removidos 'tipo_jogo' e 'palpite'. Adicionados novos campos.
        fields = [
            'id', 'nome_sorteio', 'nome_jogo', 'nome_modalidade', 'nome_colocacao', 
            'palpites', 'valor', 'status', 'valor_premio', 'criado_em'
        ]

    @extend_schema_field(OpenApiTypes.STR)
    def get_status(self, obj):
        if not obj.sorteio.fechado:
            return "Aguardando Sorteio ⏳"
        return "Ganhou!!!" if obj.ganhou else "Não foi dessa vez"