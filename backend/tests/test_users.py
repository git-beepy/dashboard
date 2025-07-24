"""
Testes para rotas de usuários
"""
import pytest
import json

class TestUsers:
    """Testes para rotas de usuários"""
    
    def test_get_users_as_admin(self, client, auth_headers):
        """Teste de listagem de usuários como admin"""
        response = client.get('/users', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 2  # Pelo menos admin e embaixadora
        
        # Verificar se senhas não estão sendo retornadas
        for user in data:
            assert 'password' not in user
    
    def test_get_users_as_ambassador(self, client, ambassador_headers):
        """Teste de listagem de usuários como embaixadora (deve falhar)"""
        response = client.get('/users', headers=ambassador_headers)
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'error' in data
    
    def test_get_users_without_auth(self, client):
        """Teste de listagem de usuários sem autenticação"""
        response = client.get('/users')
        
        assert response.status_code == 401
    
    def test_create_user_as_admin(self, client, auth_headers, sample_user_data):
        """Teste de criação de usuário como admin"""
        response = client.post('/users', 
                             json=sample_user_data,
                             headers=auth_headers,
                             content_type='application/json')
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['name'] == sample_user_data['name']
        assert data['email'] == sample_user_data['email']
        assert data['role'] == sample_user_data['role']
        assert 'password' not in data  # Senha não deve ser retornada
        assert 'id' in data
        assert data['active'] == True
    
    def test_create_user_as_ambassador(self, client, ambassador_headers, sample_user_data):
        """Teste de criação de usuário como embaixadora (deve falhar)"""
        response = client.post('/users',
                             json=sample_user_data,
                             headers=ambassador_headers,
                             content_type='application/json')
        
        assert response.status_code == 403
    
    def test_create_user_duplicate_email(self, client, auth_headers):
        """Teste de criação de usuário com email duplicado"""
        user_data = {
            'name': 'Usuário Duplicado',
            'email': 'admin@beepy.com',  # Email já existe
            'password': 'senha123',
            'role': 'embaixadora'
        }
        
        response = client.post('/users',
                             json=user_data,
                             headers=auth_headers,
                             content_type='application/json')
        
        assert response.status_code == 409
        data = response.get_json()
        assert 'error' in data
        assert 'já está em uso' in data['error']
    
    def test_create_user_invalid_data(self, client, auth_headers):
        """Teste de criação de usuário com dados inválidos"""
        invalid_data = {
            'name': '',  # Nome vazio
            'email': 'email_invalido',  # Email inválido
            'password': '123',  # Senha muito curta
            'role': 'role_invalida'  # Role inválida
        }
        
        response = client.post('/users',
                             json=invalid_data,
                             headers=auth_headers,
                             content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'validation_errors' in data
        assert len(data['validation_errors']) > 0
    
    def test_create_user_missing_required_fields(self, client, auth_headers):
        """Teste de criação de usuário sem campos obrigatórios"""
        incomplete_data = {
            'name': 'Usuário Incompleto'
            # Faltam email, password e role
        }
        
        response = client.post('/users',
                             json=incomplete_data,
                             headers=auth_headers,
                             content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'validation_errors' in data
    
    def test_get_user_by_id_as_admin(self, client, auth_headers):
        """Teste de obtenção de usuário por ID como admin"""
        response = client.get('/users/1', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == 1
        assert 'password' not in data
    
    def test_get_user_by_id_as_owner(self, client, ambassador_headers):
        """Teste de obtenção de próprio usuário como embaixadora"""
        response = client.get('/users/2', headers=ambassador_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == 2
        assert 'password' not in data
    
    def test_get_user_by_id_unauthorized(self, client, ambassador_headers):
        """Teste de obtenção de usuário de outro como embaixadora"""
        response = client.get('/users/1', headers=ambassador_headers)
        
        assert response.status_code == 403
    
    def test_get_user_not_found(self, client, auth_headers):
        """Teste de obtenção de usuário inexistente"""
        response = client.get('/users/999', headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_update_user_as_admin(self, client, auth_headers):
        """Teste de atualização de usuário como admin"""
        update_data = {
            'name': 'Nome Atualizado',
            'email': 'novo_email@teste.com'
        }
        
        response = client.put('/users/2',
                            json=update_data,
                            headers=auth_headers,
                            content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['name'] == update_data['name']
        assert data['email'] == update_data['email']
    
    def test_update_own_user_as_ambassador(self, client, ambassador_headers):
        """Teste de atualização de próprio usuário como embaixadora"""
        update_data = {
            'name': 'Mariana Lopes Atualizada'
        }
        
        response = client.put('/users/2',
                            json=update_data,
                            headers=ambassador_headers,
                            content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['name'] == update_data['name']
    
    def test_update_other_user_as_ambassador(self, client, ambassador_headers):
        """Teste de atualização de outro usuário como embaixadora"""
        update_data = {
            'name': 'Tentativa de Atualização'
        }
        
        response = client.put('/users/1',
                            json=update_data,
                            headers=ambassador_headers,
                            content_type='application/json')
        
        assert response.status_code == 403
    
    def test_update_user_duplicate_email(self, client, auth_headers):
        """Teste de atualização com email duplicado"""
        update_data = {
            'email': 'admin@beepy.com'  # Email já existe
        }
        
        response = client.put('/users/2',
                            json=update_data,
                            headers=auth_headers,
                            content_type='application/json')
        
        assert response.status_code == 409
    
    def test_update_user_invalid_data(self, client, auth_headers):
        """Teste de atualização com dados inválidos"""
        invalid_data = {
            'name': '',  # Nome vazio
            'email': 'email_invalido'
        }
        
        response = client.put('/users/2',
                            json=invalid_data,
                            headers=auth_headers,
                            content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'validation_errors' in data
    
    def test_delete_user_as_admin(self, client, auth_headers, sample_user_data):
        """Teste de exclusão de usuário como admin"""
        # Primeiro criar um usuário para deletar
        create_response = client.post('/users',
                                    json=sample_user_data,
                                    headers=auth_headers,
                                    content_type='application/json')
        
        assert create_response.status_code == 201
        user_id = create_response.get_json()['id']
        
        # Agora deletar o usuário
        delete_response = client.delete(f'/users/{user_id}', headers=auth_headers)
        
        assert delete_response.status_code == 200
        data = delete_response.get_json()
        assert 'message' in data
    
    def test_delete_user_as_ambassador(self, client, ambassador_headers):
        """Teste de exclusão de usuário como embaixadora (deve falhar)"""
        response = client.delete('/users/1', headers=ambassador_headers)
        
        assert response.status_code == 403
    
    def test_delete_user_not_found(self, client, auth_headers):
        """Teste de exclusão de usuário inexistente"""
        response = client.delete('/users/999', headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_toggle_user_status_as_admin(self, client, auth_headers):
        """Teste de alteração de status de usuário como admin"""
        response = client.put('/users/2/toggle-status', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        assert 'active' in data
    
    def test_toggle_user_status_as_ambassador(self, client, ambassador_headers):
        """Teste de alteração de status como embaixadora (deve falhar)"""
        response = client.put('/users/1/toggle-status', headers=ambassador_headers)
        
        assert response.status_code == 403
    
    def test_toggle_user_status_not_found(self, client, auth_headers):
        """Teste de alteração de status de usuário inexistente"""
        response = client.put('/users/999/toggle-status', headers=auth_headers)
        
        assert response.status_code == 404

