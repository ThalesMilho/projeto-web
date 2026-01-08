from rest_framework import serializers
from .models import Aposta, Sorteio, Bicho, ParametrosDoJogo # <--- Adicionei ParametrosDoJogo

# --- SERIALIZER 1: Listar sorteios (GET) ---
class SorteioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sorteio
        fields = ['id', 'data', 'horario', 'get_horario_display', 'fechado', 'premio_1']

# --- SERIALIZER 2: Validar e Criar aposta (POST) ---
class CriarApostaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aposta
        fields = ['sorteio', 'tipo_jogo', 'valor', 'palpite']

    def validate(self, data):
        sorteio = data['sorteio']
        tipo_jogo = data['tipo_jogo']
        palpite = data['palpite']
        
        # Valida Configuração Global
        config = ParametrosDoJogo.load()
        if not config.ativa_apostas:
            raise serializers.ValidationError("O sistema de apostas está temporariamente suspenso pelo administrador.")
            
        # Valida Sorteio
        if sorteio.fechado:
            raise serializers.ValidationError({"sorteio": "Este sorteio já foi encerrado."})

        # --- NOVA VALIDAÇÃO: FORMATO LOTERIA ---
        if tipo_jogo in ['QU', 'SE', 'LO']:
            try:
                # Remove espaços, divide por vírgula e limpa vazios
                numeros = [n.strip() for n in palpite.replace('-', ',').split(',') if n.strip()]
                
                if len(numeros) == 0:
                    raise ValueError
                
                # Testa se são todos números
                for n in numeros:
                    int(n)
            except Exception:
                raise serializers.ValidationError({
                    "palpite": "Formato inválido. Use números separados por vírgula. Ex: 01,02,03..."
                })

        return data
    
    def create(self, validated_data):
        # Injeta o usuário logado automaticamente
        usuario = self.context['request'].user
        return Aposta.objects.create(usuario=usuario, **validated_data)

# --- SERIALIZER 3: NOVO - Para ver os detalhes e se ganhou (GET) ---
class ApostaDetalheSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    nome_sorteio = serializers.CharField(source='sorteio.__str__', read_only=True)

    class Meta:
        model = Aposta
        fields = ['id', 'nome_sorteio', 'tipo_jogo', 'palpite', 'valor', 'status', 'valor_premio', 'criado_em']

    def get_status(self, obj):
        if not obj.sorteio.fechado:
            return "Aguardando Sorteio ⏳"
        return "Ganhou! 🤑" if obj.ganhou else "Não foi dessa vez 😢"