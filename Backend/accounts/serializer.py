from rest_framework import serializers
from .models import SolicitacaoPagamento, Transacao, CustomUser
from validate_docbr import CPF, CNPJ
import re
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, help_text="Senha do usuário.")
    # Change to IntegerField for cents, but display as Decimal
    saldo_cents = serializers.IntegerField(
        source='saldo', 
        read_only=True,
        help_text="Saldo em CENTAVOS. Divida por 100 para exibir em Reais."
    )
    saldo = serializers.SerializerMethodField(
        help_text="Saldo formatado em Reais (ex: '10.50'). Já convertido para exibição."
    )
    nome_completo = serializers.CharField(help_text="Nome completo do usuário.")
    cpf_cnpj = serializers.CharField(help_text="CPF ou CNPJ do usuário.")
    phone = serializers.CharField(help_text="Número de telefone do usuário.")

    class Meta:
        model = CustomUser
        fields = ('id', 'nome_completo', 'cpf_cnpj', 'phone', 'password', 'saldo', 'saldo_cents')

    def get_saldo(self, obj):
        """Convert stored cents to Decimal for display."""
        return float(obj.saldo) / 100.0

    def validate_cpf_cnpj(self, value):
        """
        Remove pontuação e valida se o CPF/CNPJ é matematicamente real.
        """
        # Sanitizacao
        clean_doc = re.sub(r'\D', '', value)
        
        if not clean_doc:
            raise serializers.ValidationError("O CPF/CNPJ é obrigatório.")

        # Validação Matemática
        if len(clean_doc) == 11:
            validator = CPF()
            if not validator.validate(clean_doc):
                raise serializers.ValidationError("CPF inválido (dígitos incorretos).")
        elif len(clean_doc) == 14:
            validator = CNPJ()
            if not validator.validate(clean_doc):
                raise serializers.ValidationError("CNPJ inválido (dígitos incorretos).")
        else:
            raise serializers.ValidationError("O documento deve ter 11 (CPF) ou 14 (CNPJ) dígitos.")
            
        return clean_doc

    def create(self, validated_data):
        cpf = validated_data['cpf_cnpj']
        
        user = CustomUser.objects.create_user(
            cpf_cnpj=cpf,
            username=cpf, 
            nome_completo=validated_data['nome_completo'],
            phone=validated_data.get('phone'),
            password=validated_data['password']
        )
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Personaliza o login para:
    1. Aceitar CPF/CNPJ com pontuação (e limpar antes de validar).
    2. Retornar dados do usuário junto com o token.
    """
    
    def validate(self, attrs):
        # Verifica qual nome de campo o sistema está usando (username ou cpf_cnpj)
        # O SimpleJWT usa o USERNAME_FIELD do seu models.py
        
        # 1. Pega o valor do login (tenta pegar 'username' ou 'cpf_cnpj')
        login_input = attrs.get('username') or attrs.get('cpf_cnpj')
        
        if login_input:
            # 2. Limpa o valor (remove pontos e traços)
            clean_value = re.sub(r'\D', '', login_input)
            
            # 3. Devolve o valor limpo para o campo correto
            if 'username' in attrs:
                attrs['username'] = clean_value
            if 'cpf_cnpj' in attrs:
                attrs['cpf_cnpj'] = clean_value
                
        # Continua a validação padrão
        data = super().validate(attrs)
        
        # Mantém seus dados extras
        data['user_id'] = self.user.id
        data['nome'] = self.user.nome_completo
        data['is_admin'] = self.user.is_superuser
        # Convert cents to decimal for display (1000 -> 10.00)
        data['saldo'] = float(self.user.saldo) / 100.0
        
        return data
    
# 1. Serializer para Redefinição de Senha
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

# 2. Serializer Completo para Backoffice (Solicitações)
class SolicitacaoPagamentoAdminSerializer(serializers.ModelSerializer):
    usuario_nome = serializers.CharField(source='usuario.nome_completo', read_only=True)
    usuario_email = serializers.CharField(source='usuario.email', read_only=True)
    usuario_cpf = serializers.CharField(source='usuario.cpf_cnpj', read_only=True)
    
    class Meta:
        model = SolicitacaoPagamento
        fields = [
            'id', 'usuario_id', 'usuario_nome', 'usuario_email', 'usuario_cpf',
            'tipo', 'valor', 'status', 'criado_em', 'data_aprovacao', 
            'analise_motivo', 'risco_score', #'comprovante_url'
        ]
    
    def to_representation(self, instance):
        """Convert stored cents to Decimal for display."""
        data = super().to_representation(instance)
        if 'valor' in data and data['valor'] is not None:
            # Convert cents to decimal (1050 -> 10.50)
            data['valor'] = float(data['valor']) / 100.0
        return data

# 3. Serializer para Ação de Aprovar/Recusar
class AnaliseSolicitacaoSerializer(serializers.Serializer):
    acao = serializers.ChoiceField(choices=['APROVAR', 'RECUSAR'])
    motivo = serializers.CharField(required=False, allow_blank=True)

# 4. Serializer de Risco (IPs)
class RiscoIPSerializer(serializers.Serializer):
    ultimo_ip = serializers.IPAddressField()
    total_contas = serializers.IntegerField()
    usuarios = serializers.ListField(child=serializers.CharField())


class DepositoSerializer(serializers.Serializer):
    valor = serializers.IntegerField(
        min_value=100,
        help_text="Valor em CENTAVOS (ex: Para R$ 10,00 envie 1000). Não envie decimais."
    )
    
    def validate_valor(self, value):
        """Validate integer cents input."""
        if value < 100:
            raise serializers.ValidationError("Valor mínimo de depósito é R$ 1,00 (100 centavos).")
        return value