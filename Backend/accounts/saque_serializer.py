from rest_framework import serializers

class SolicitacaoSaqueSerializer(serializers.Serializer):
    valor = serializers.IntegerField(
        min_value=1000,
        help_text="Valor do saque em CENTAVOS (ex: 5000 = R$ 50,00). Mínimo: R$ 10,00 (1000 centavos)."
    )
    chave_pix = serializers.CharField(
        max_length=140,
        help_text="Chave PIX para saque (CPF, CNPJ, Email ou Telefone)"
    )
    
    def validate_valor(self, value):
        """Validate withdrawal amount in cents."""
        if value < 1000:
            raise serializers.ValidationError("Valor mínimo de saque é R$ 10,00 (1000 centavos).")
        return value
