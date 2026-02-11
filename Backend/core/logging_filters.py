import logging
import re

class SensitiveDataFilter(logging.Filter):
    """
    Filtro de Logs para conformidade com LGPD.
    Intercepta qualquer log do sistema e mascara CPFs, Senhas, Cartões de Crédito, 
    E-mails e Telefones antes de exibir.
    """
    def filter(self, record):
        if not isinstance(record.msg, str):
            return True
            
        msg = record.msg
        
        # 1. Mascara CPF (Formato 11 dígitos puro ou com pontuação)
        # Regex busca: 3 digitos + ponto opcional + 3 digitos + ponto opcional + 3 digitos + traço opcional + 2 digitos
        msg = re.sub(r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b', '[CPF-OCULTO-LGPD]', msg)
        
        # 2. Mascara Cartões de Crédito (Formatos: 4111 1111 1111 1111, 4111111111111111)
        msg = re.sub(r'\b(?:\d[ -]*?){13,16}\b', '[CARTAO-OCULTO-LGPD]', msg)
        
        # 3. Mascara E-mails (preserva domínio para debugging)
        msg = re.sub(r'\b([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b', r'[EMAIL-OCULTO-LGPD]@\2', msg)
        
        # 4. Mascara Telefones brasileiros (Formatos: (11) 99999-9999, 11999999999, etc.)
        msg = re.sub(r'\(?\d{2}\)?\s?\d{4,5}-?\d{4}\b', '[TELEFONE-OCULTO-LGPD]', msg)
        
        # 5. Mascara Senhas (se aparecerem em logs de debug ou query params)
        msg = re.sub(r'(password|senha|token|secret|api_key)=.*?(&|\s|$)', r'\1=[PROTEGIDO]\2', msg, flags=re.IGNORECASE)
        
        # 6. Mascara Chaves de API longas
        msg = re.sub(r'[a-zA-Z0-9]{32,}', '[CHAVE-OCULTA-LGPD]', msg)
        
        # 7. Mascara dados bancários (agência, conta)
        msg = re.sub(r'(agencia|conta|agency|account)=\s*[0-9-]+', r'\1=[PROTEGIDO]', msg, flags=re.IGNORECASE)
        
        record.msg = msg
        return True