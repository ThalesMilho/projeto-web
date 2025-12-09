from rest_framework import serializers
from .models import CustomUser
from validate_docbr import CPF, CNPJ
import re
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    saldo = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True) # Adiciona isto

    class Meta:
        model = CustomUser
        fields = ('id', 'nome_completo', 'cpf_cnpj', 'phone', 'password', 'saldo')

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
        data_input = attrs.get('cpf_cnpj')
        if data_input:
            attrs['cpf_cnpj'] = re.sub(r'\D', '', data_input)

        data = super().validate(attrs)

        data['user'] = {
            'id': self.user.id,
            'nome': self.user.nome_completo,
            'cpf': self.user.cpf_cnpj,
            'saldo': float(self.user.saldo)
        }
        return data