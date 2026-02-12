#!/usr/bin/env python3
"""
Teste de CORS para verificar se frontend consegue acessar
"""
import urllib.request
import json

def test_cors():
    print("🔍 TESTE DE CORS - FRONTEND CONSEGUE ACESSAR?")
    print("=" * 60)
    
    # Simular requisição de frontend (localhost:3000)
    frontend_origin = "http://localhost:3000"
    
    # Testar endpoint público (sem autenticação)
    try:
        req = urllib.request.Request(
            'http://127.0.0.1:8000/api/games/bichos/',
            headers={
                'Origin': frontend_origin,
                'Content-Type': 'application/json'
            }
        )
        
        response = urllib.request.urlopen(req, timeout=5)
        
        # Verificar headers CORS
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
        }
        
        print("📋 RESPOSTA DO SERVIDOR:")
        print(f"   Status: {response.status}")
        print(f"   Content-Type: {response.headers.get('Content-Type')}")
        
        print("\n🔒 HEADERS CORS RECEBIDOS:")
        for header, value in cors_headers.items():
            status = "✅" if value else "❌"
            print(f"   {status} {header}: {value or 'NÃO ENVIADO'}")
        
        # Verificar se frontend consegue acessar
        allow_origin = cors_headers['Access-Control-Allow-Origin']
        
        if allow_origin == frontend_origin:
            print(f"\n✅ SUCESSO! Frontend {frontend_origin} PODE acessar!")
        elif allow_origin == "*":
            print(f"\n⚠️  ATENÇÃO! CORS permite qualquer origem (*)")
            print("   Isso funciona mas não é recomendado para produção!")
        elif not allow_origin:
            print(f"\n❌ BLOQUEADO! Frontend {frontend_origin} NÃO PODE acessar!")
            print("   CORS não configurado para permitir esta origem!")
        else:
            print(f"\n❌ BLOQUEADO! Frontend {frontend_origin} NÃO PODE acessar!")
            print(f"   CORS permite apenas: {allow_origin}")
            
    except urllib.error.HTTPError as e:
        print(f"❌ Erro HTTP: {e.code} - {e.reason}")
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")

def test_preflight():
    """Testar requisição OPTIONS (preflight)"""
    print("\n🚀 TESTE DE PREFLIGHT (OPTIONS)")
    print("-" * 40)
    
    try:
        req = urllib.request.Request(
            'http://127.0.0.1:8000/api/accounts/login/',
            method='OPTIONS',
            headers={
                'Origin': 'http://localhost:3000',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type, Authorization'
            }
        )
        
        response = urllib.request.urlopen(req, timeout=5)
        
        print(f"   Status: {response.status}")
        
        # Verificar headers de preflight
        allow_methods = response.headers.get('Access-Control-Allow-Methods')
        allow_headers = response.headers.get('Access-Control-Allow-Headers')
        
        if allow_methods and 'POST' in allow_methods:
            print("✅ Métodos permitidos: POST")
        else:
            print(f"❌ Métodos permitidos: {allow_methods}")
            
        if allow_headers and 'Content-Type' in allow_headers:
            print("✅ Headers permitidos: Content-Type")
        else:
            print(f"❌ Headers permitidos: {allow_headers}")
            
    except Exception as e:
        print(f"❌ Erro no preflight: {e}")

if __name__ == "__main__":
    test_cors()
    test_preflight()
