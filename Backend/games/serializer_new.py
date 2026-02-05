import logging
from decimal import Decimal
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from .models import Aposta, Sorteio, Jogo, Modalidade, Colocacao

logger = logging.getLogger(__name__)

# --- SERIALIZER 1: Listar sorteios (GET) ---
class SorteioSerializer(serializers.ModelSerializer):
    """
    Utilizado para listar os sorteios disponíveis no Frontend.
    """
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Sorteio
        fields = ['id', 'data', 'horario', 'fechado', 'status_display', 'premio_1', 'resultado']

    def get_status_display(self, obj):
        return "Fechado" if obj.fechado else "Aberto"

# --- SERIALIZER 2: CRIAÇÃO DE APOSTAS (Com Adapter Pattern & Documentação) ---
class CriarApostaSerializer(serializers.ModelSerializer):
    """
    Serializer robusto para criar apostas.
    Funciona como um 'Adaptador': Aceita dados legados do frontend antigo ('tipo_jogo', 'palpite')
    e os converte automaticamente para o novo esquema do banco ('modalidade', 'jogo', 'palpites').
    """
    
    # --- Campos Legados (Compatibilidade com Frontend) ---
    # write_only=True garante que não poluam a resposta, apenas a entrada
    tipo_jogo = serializers.CharField(
        required=False, 
        allow_null=True, 
        write_only=True,
        help_text="Código Legado (ex: 'M', 'G'). Será traduzido para Modalidade."
    )
    palpite = serializers.CharField(
        required=False, 
        allow_null=True, 
        write_only=True,
        help_text="String Legada (ex: '1234'). Será convertida para lista JSON."
    )
    
    # --- Campos Normalizados (Integridade do Banco de Dados) ---
    # Aceita IDs se o frontend enviar, mas resolve via lógica se não enviar
    jogo = serializers.PrimaryKeyRelatedField(
        queryset=Jogo.objects.filter(ativo=True), 
        required=False,
        allow_null=True
    )
    modalidade = serializers.PrimaryKeyRelatedField(
        queryset=Modalidade.objects.all(), 
        required=False,
        allow_null=True
    )
    colocacao = serializers.PrimaryKeyRelatedField(
        queryset=Colocacao.objects.all(),
        required=False,
        allow_null=True
    )
    sorteio = serializers.PrimaryKeyRelatedField(
        queryset=Sorteio.objects.all()
    )
    
    class Meta:
        model = Aposta
        fields = [
            'id',
            'valor', 
            'palpites', 
            'sorteio',         
            'tipo_jogo',       # Input Legado
            'palpite',         # Input Legado
            'jogo',            # Output Normalizado
            'modalidade',      # Output Normalizado
            'colocacao',       
            'comissao_gerada',
            'criado_em',
            'status'
        ]
        read_only_fields = ['id', 'criado_em', 'status', 'comissao_gerada', 'ganhou', 'valor_premio']
        extra_kwargs = {
            'palpites': {'required': False}, # Gerado dinamicamente no validate
            'valor': {'required': True, 'min_value': Decimal('0.01')}
        }

    def _normalize_palpites(self, legacy_palpite, current_palpites):
        """
        Helper: Garante que 'palpites' seja sempre uma lista de strings limpa.
        """
        if current_palpites:
            # Se já veio no formato novo (lista), apenas limpa espaços e converte para string
            if isinstance(current_palpites, list):
                return [str(p).strip() for p in current_palpites if str(p).strip()]
            return []

        if legacy_palpite:
            # Trata string única ("1234") ou separada por vírgula ("12, 15")
            safe_str = str(legacy_palpite)
            if ',' in safe_str:
                return [p.strip() for p in safe_str.split(',') if p.strip()]
            return [safe_str.strip()]
        
        return []

    def _resolve_modalidade(self, tipo_code):
        """
        Helper Crítico: Mapeia o código 'M'/'G' do frontend antigo para o objeto Modalidade real no banco.
        """
        if not tipo_code:
            return None

        clean_code = str(tipo_code).upper().strip()
        
        # MAPA DE TRADUÇÃO (Adicione variações conforme necessário)
        LEGACY_CODE_MAP = {
            'M': 'Milhar',
            'C': 'Centena',
            'D': 'Dezena',
            'G': 'Grupo',
            'MC': 'Milhar e Centena', 
            'MM': 'Milhar e Centena', 
            'MINV': 'Milhar Invertida',
            'CINV': 'Centena Invertida',
            'DG': 'Duque de Grupo',
            'TG': 'Terno de Grupo',
            'QG': 'Quadra de Grupo',
            'DD': 'Duque de Dezena',
            'TD': 'Terno de Dezena',
            'PV': 'Passe Vai',
            'PVV': 'Passe Vai Vem',
            'TS': 'Terno Seco',
        }

        # 1. Tenta pegar o nome mapeado, ou usa o próprio código
        search_term = LEGACY_CODE_MAP.get(clean_code, clean_code)

        # 2. Busca no Banco (Prioridade: Nome Exato > Nome Contém)
        modalidade = Modalidade.objects.filter(nome__iexact=search_term).first()
        
        if not modalidade:
            modalidade = Modalidade.objects.filter(nome__icontains=search_term).first()

        return modalidade

    def validate(self, attrs):
        """
        VALIDAÇÃO CENTRAL: Transforma dados legados e garante integridade antes de salvar.
        """
        
        # 1. Normalizar Palpites (Transforma string 'palpite' em lista 'palpites')
        legacy_palpite = attrs.get('palpite')
        current_palpites = attrs.get('palpites')
        
        attrs['palpites'] = self._normalize_palpites(legacy_palpite, current_palpites)
        
        if not attrs['palpites']:
             raise serializers.ValidationError({"palpites": _("O palpite é obrigatório.")})

        # 2. Resolver Modalidade e Jogo (Se não enviados via ID)
        # Prioriza o ID se enviado, senão tenta resolver pelo tipo_jogo legado
        if not attrs.get('modalidade'): 
            tipo_jogo = attrs.get('tipo_jogo')
            if tipo_jogo:
                modalidade = self._resolve_modalidade(tipo_jogo)
                
                if not modalidade:
                     logger.error(f"Adapter Falhou: Código '{tipo_jogo}' não mapeado.")
                     raise serializers.ValidationError({
                         "tipo_jogo": _(f"Modalidade inválida ou não encontrada para o código '{tipo_jogo}'.")
                     })
                
                # INJEÇÃO: Salva os objetos resolvidos nos dados validados
                attrs['modalidade'] = modalidade
                # Resolve automaticamente o Jogo pai da modalidade
                attrs['jogo'] = modalidade.jogo 
        
        # 3. Verificações de Integridade Final
        if not attrs.get('modalidade'):
             raise serializers.ValidationError(_("Erro de Validação: A modalidade do jogo não foi identificada."))
        
        if not attrs.get('jogo'):
             # Fallback de segurança: Tenta pegar do pai da modalidade
             if attrs.get('modalidade'):
                 attrs['jogo'] = attrs['modalidade'].jogo
             else:
                 raise serializers.ValidationError(_("Erro de Validação: O Jogo pai não foi identificado."))

        # 4. Validar Colocação (se enviada e se temos jogo)
        if attrs.get('colocacao') and attrs.get('jogo'):
            if attrs['colocacao'].jogo_id != attrs['jogo'].id:
                raise serializers.ValidationError({"colocacao": _("Esta colocação não pertence ao jogo selecionado.")})

        # 5. Validar Sorteio
        sorteio = attrs.get('sorteio')
        if sorteio and sorteio.fechado:
            raise serializers.ValidationError({"sorteio": _("Este sorteio já está fechado.")})

        return attrs

# --- SERIALIZER 3: DETALHES PARA O USUÁRIO (GET) ---
class ApostaDetalheSerializer(serializers.ModelSerializer):
    """
    Serializer Somente-Leitura para exibir detalhes da aposta no histórico.
    """
    # Campos de leitura amigáveis (Flattening)
    nome_sorteio = serializers.CharField(source='sorteio.__str__', read_only=True)
    nome_jogo = serializers.CharField(source='jogo.nome', read_only=True)
    nome_modalidade = serializers.CharField(source='modalidade.nome', read_only=True)
    nome_colocacao = serializers.CharField(source='colocacao.nome', read_only=True, allow_null=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Aposta
        fields = [
            'id', 
            'nome_sorteio', # Mantido para compatibilidade com sua view atual
            'sorteio',      # ID do sorteio também é útil
            'nome_jogo', 'jogo',
            'nome_modalidade', 'modalidade',
            'nome_colocacao', 'colocacao',
            'valor', 
            'palpites', 
            'status', 'status_display', 
            'ganhou', 
            'valor_premio', 
            'criado_em'
        ]
