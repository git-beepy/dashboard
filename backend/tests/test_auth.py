"""
Testes para autenticação
"""
import pytest
import json

class TestAuth:
    """Testes para rotas de autenticação"""
    
    def test_login_success_admin(self, client):
        """Teste de login bem-sucedido para admin"""
        response = client.post('/auth/login', 
                             json={'email': 'admin@beepy.com', 'password': 'admin123'},
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert data['user']['email'] == 'admin@beepy.com'
        assert data['user']['role'] == 'admin'
    
    def test_login_success_ambassador(self, client):
        """Teste de login bem-sucedido para embaixadora"""
        response = client.post('/auth/login',
                             json={'email': 'embaixadora@teste.com', 'password': 'senha123'},
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert data['user']['email'] == 'embaixadora@teste.com'
        assert data['user']['role'] == 'embaixadora'
    
    def test_login_invalid_email(self, client):
        """Teste de login com email inválido"""
        response = client.post('/auth/login',
                             json={'email': 'inexistente@teste.com', 'password': 'senha123'},
                             content_type='application/json')
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
    
    def test_login_invalid_password(self, client):
        """Teste de login com senha inválida"""
        response = client.post('/auth/login',
                             json={'email': 'admin@beepy.com', 'password': 'senha_errada'},
                             content_type='application/json')
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
    
    def test_login_missing_email(self, client):
        """Teste de login sem email"""
        response = client.post('/auth/login',
                             json={'password': 'senha123'},
                             content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_login_missing_password(self, client):
        """Teste de login sem senha"""
        response = client.post('/auth/login',
                             json={'email': 'admin@beepy.com'},
                             content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_login_empty_json(self, client):
        """Teste de login com JSON vazio"""
        response = client.post('/auth/login',
                             json={},
                             content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_login_no_json(self, client):
        """Teste de login sem JSON"""
        response = client.post('/auth/login')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_verify_token_valid(self, client, auth_headers):
        """Teste de verificação de token válido"""
        response = client.get('/auth/verify', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'user' in data
        assert data['user']['email'] == 'admin@beepy.com'
    
    def test_verify_token_invalid(self, client):
        """Teste de verificação de token inválido"""
        headers = {'Authorization': 'Bearer token_invalido'}
        response = client.get('/auth/verify', headers=headers)
        
        assert response.status_code == 422  # JWT decode error
    
    def test_verify_token_missing(self, client):
        """Teste de verificação sem token"""
        response = client.get('/auth/verify')
        
        assert response.status_code == 401  # Missing Authorization Header
    
    def test_protected_route_with_valid_token(self, client, auth_headers):
        """Teste de rota protegida com token válido"""
        response = client.get('/users', headers=auth_headers)
        
        # Deve retornar 200 ou 404, não 401 (não autorizado)
        assert response.status_code != 401
    
    def test_protected_route_without_token(self, client):
        """Teste de rota protegida sem token"""
        response = client.get('/users')
        
        assert response.status_code == 401
    
    def test_admin_only_route_with_admin_token(self, client, auth_headers):
        """Teste de rota apenas admin com token de admin"""
        response = client.get('/users', headers=auth_headers)
        
        # Admin deve ter acesso
        assert response.status_code != 403
    
    def test_admin_only_route_with_ambassador_token(self, client, ambassador_headers):
        """Teste de rota apenas admin com token de embaixadora"""
        response = client.get('/users', headers=ambassador_headers)
        
        # Embaixadora não deve ter acesso
        assert response.status_code == 403
    
    def test_case_insensitive_email_login(self, client):
        """Teste de login com email em maiúsculas"""
        response = client.post('/auth/login',
                             json={'email': 'ADMIN@BEEPY.COM', 'password': 'admin123'},
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
    
    def test_login_with_whitespace_email(self, client):
        """Teste de login com espaços no email"""
        response = client.post('/auth/login',
                             json={'email': '  admin@beepy.com  ', 'password': 'admin123'},
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data

