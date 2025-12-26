import logging
import re

class SensitiveDataFilter(logging.Filter):
    """
    Filtro de Logs para conformidade com LGPD.
    Intercepta qualquer log do sistema e mascara CPFs e Senhas antes de exibir.
    """
    def filter(self, record):
        if not isinstance(record.msg, str):
            return True
            
        msg = record.msg
        
        # 1. Mascara CPF (Formato 11 dígitos puro ou com pontuação)
        # Regex busca: 3 digitos + ponto opcional + 3 digitos + ponto opcional + 3 digitos + traço opcional + 2 digitos
        msg = re.sub(r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b', '[CPF-OCULTO-LGPD]', msg)
        
        # 2. Mascara Senhas (se aparecerem em logs de debug ou query params)
        msg = re.sub(r'(password|senha|token)=.*?(&|\s|$)', r'\1=[PROTEGIDO]\2', msg, flags=re.IGNORECASE)
        
        record.msg = msg
        return True