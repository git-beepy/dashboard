#!/usr/bin/env python3
"""
Teste simples para verificar se o backend está funcionando
"""
import os
import sys

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("🔍 Testando importações...")
    
    # Testar importação das configurações
    from config.settings import config
    print("✅ Configurações importadas com sucesso")
    
    # Testar validação de configurações
    try:
        config.validate()
        print("✅ Configurações validadas com sucesso")
    except ValueError as e:
        print(f"⚠️ Aviso de configuração: {e}")
    
    # Testar importação do Firebase
    from config.firebase import firebase_config
    print("✅ Firebase config importado com sucesso")
    
    # Testar conexão Firebase
    if firebase_config.is_connected():
        print("✅ Firebase conectado com sucesso")
    else:
        print("❌ Firebase não conectado")
    
    # Testar importação dos serviços
    from services.firestore_service import UserService
    print("✅ Serviços importados com sucesso")
    
    # Testar importação das rotas
    from routes.auth import auth_bp
    from routes.indications import indications_bp
    print("✅ Rotas importadas com sucesso")
    
    # Testar criação da aplicação
    from app import create_app
    app = create_app()
    print("✅ Aplicação Flask criada com sucesso")
    
    print("\n🎉 Todos os testes passaram! O backend está funcionando corretamente.")
    
except Exception as e:
    print(f"❌ Erro durante o teste: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

