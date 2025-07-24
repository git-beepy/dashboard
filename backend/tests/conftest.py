"""
Configuração base para testes do projeto Beepy
"""
import pytest
import tempfile
import os
from main_enhanced import create_app

@pytest.fixture
def app():
    """Criar instância da aplicação para testes"""
    # Configuração de teste
    test_config = {
        'TESTING': True,
        'JWT_SECRET_KEY': 'test-secret-key',
        'JWT_ACCESS_TOKEN_EXPIRES': False,  # Tokens não expiram nos testes
    }
    
    app = create_app(test_config)
    
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    """Cliente de teste para fazer requisições"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Runner para comandos CLI"""
    return app.test_cli_runner()

@pytest.fixture
def auth_headers(client):
    """Headers de autenticação para testes"""
    # Login como admin
    response = client.post('/auth/login', json={
        'email': 'admin@beepy.com',
        'password': 'admin123'
    })
    
    if response.status_code == 200:
        data = response.get_json()
        token = data.get('access_token')
        return {'Authorization': f'Bearer {token}'}
    
    return {}

@pytest.fixture
def ambassador_headers(client):
    """Headers de autenticação para embaixadora"""
    # Login como embaixadora
    response = client.post('/auth/login', json={
        'email': 'embaixadora@teste.com',
        'password': 'senha123'
    })
    
    if response.status_code == 200:
        data = response.get_json()
        token = data.get('access_token')
        return {'Authorization': f'Bearer {token}'}
    
    return {}

@pytest.fixture
def sample_user_data():
    """Dados de exemplo para criação de usuário"""
    return {
        'name': 'Teste Usuario',
        'email': 'teste@exemplo.com',
        'password': 'senha123',
        'role': 'embaixadora'
    }

@pytest.fixture
def sample_indication_data():
    """Dados de exemplo para criação de indicação"""
    return {
        'clientName': 'Cliente Teste',
        'clientEmail': 'cliente@teste.com',
        'clientPhone': '+5511999999999',
        'segment': 'tecnologia',
        'origin': 'indicacao_pessoal',
        'observations': 'Cliente interessado em nossos serviços'
    }

