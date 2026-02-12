#!/usr/bin/env python3
"""
Teste completo da documentação API
"""
import urllib.request

def test_documentation():
    """Testa se a documentação está completa e funcional"""
    
    try:
        response = urllib.request.urlopen('http://127.0.0.1:8000/api/docs/', timeout=5)
        content = response.read().decode()
        
        # Check for key elements
        checks = [
            ('Swagger UI', 'swagger-ui' in content.lower()),
            ('API Documentation', 'pixlegal api' in content.lower()),
            ('Try it out', 'try it out' in content.lower()),
            ('Authentication', 'authorization' in content.lower())
        ]
        
        print('📚 VERIFICAÇÃO DA DOCUMENTAÇÃO SWAGGER')
        print('=' * 50)
        
        all_good = True
        for check_name, passed in checks:
            status = '✅' if passed else '❌'
            print(f'{status} {check_name}: {"OK" if passed else "FALTANDO"}')
            if not passed:
                all_good = False
        
        if all_good:
            print('\n🎉 DOCUMENTAÇÃO 100% FUNCIONAL!')
        else:
            print('\n⚠️  Documentação precisa de ajustes')
            
        return all_good
        
    except Exception as e:
        print(f'❌ Erro ao acessar documentação: {e}')
        return False

if __name__ == "__main__":
    test_documentation()
