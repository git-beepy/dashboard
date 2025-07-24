from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import bcrypt
from datetime import datetime
import logging
from validators import UserValidator, validate_json
from utils import admin_required

logger = logging.getLogger(__name__)

users_validated_bp = Blueprint('users_validated', __name__)

# Mock database - em produção seria substituído por Firebase/Firestore
users_db = [
    {
        'id': 1,
        'name': 'Admin Beepy',
        'email': 'admin@beepy.com',
        'password': bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        'role': 'admin',
        'active': True,
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    },
    {
        'id': 2,
        'name': 'Mariana Lopes',
        'email': 'embaixadora@teste.com',
        'password': bcrypt.hashpw('senha123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        'role': 'embaixadora',
        'active': True,
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
]

@users_validated_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_users():
    """Listar todos os usuários (apenas admin)"""
    try:
        # Remover senhas dos dados retornados
        safe_users = []
        for user in users_db:
            safe_user = user.copy()
            safe_user.pop('password', None)
            safe_users.append(safe_user)
        
        logger.info(f"Usuários listados por admin: {get_jwt_identity()}")
        return jsonify(safe_users), 200
        
    except Exception as e:
        logger.error(f"Erro ao listar usuários: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@users_validated_bp.route('/users', methods=['POST'])
@jwt_required()
@admin_required
@validate_json(UserValidator, 'create')
def create_user():
    """Criar novo usuário (apenas admin)"""
    try:
        data = request.get_json()
        
        # Verificar se email já existe
        existing_user = next((u for u in users_db if u['email'] == data['email']), None)
        if existing_user:
            return jsonify({'error': 'Email já está em uso'}), 409
        
        # Gerar hash da senha
        password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Criar novo usuário
        new_user = {
            'id': max([u['id'] for u in users_db]) + 1 if users_db else 1,
            'name': data['name'].strip(),
            'email': data['email'].lower().strip(),
            'password': password_hash,
            'role': data['role'],
            'active': True,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        users_db.append(new_user)
        
        # Retornar usuário sem senha
        safe_user = new_user.copy()
        safe_user.pop('password')
        
        logger.info(f"Usuário criado: {new_user['email']} por admin: {get_jwt_identity()}")
        return jsonify(safe_user), 201
        
    except Exception as e:
        logger.error(f"Erro ao criar usuário: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@users_validated_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Obter usuário específico"""
    try:
        current_user_email = get_jwt_identity()
        current_user = next((u for u in users_db if u['email'] == current_user_email), None)
        
        if not current_user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Admin pode ver qualquer usuário, embaixadora só pode ver a si mesma
        if current_user['role'] != 'admin' and current_user['id'] != user_id:
            return jsonify({'error': 'Acesso negado'}), 403
        
        user = next((u for u in users_db if u['id'] == user_id), None)
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Remover senha dos dados retornados
        safe_user = user.copy()
        safe_user.pop('password', None)
        
        return jsonify(safe_user), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter usuário {user_id}: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@users_validated_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@validate_json(UserValidator, 'update')
def update_user(user_id):
    """Atualizar usuário"""
    try:
        current_user_email = get_jwt_identity()
        current_user = next((u for u in users_db if u['email'] == current_user_email), None)
        
        if not current_user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Admin pode atualizar qualquer usuário, embaixadora só pode atualizar a si mesma
        if current_user['role'] != 'admin' and current_user['id'] != user_id:
            return jsonify({'error': 'Acesso negado'}), 403
        
        user = next((u for u in users_db if u['id'] == user_id), None)
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        data = request.get_json()
        
        # Verificar se email já existe (se está sendo alterado)
        if 'email' in data and data['email'] != user['email']:
            existing_user = next((u for u in users_db if u['email'] == data['email']), None)
            if existing_user:
                return jsonify({'error': 'Email já está em uso'}), 409
        
        # Atualizar campos
        if 'name' in data:
            user['name'] = data['name'].strip()
        
        if 'email' in data:
            user['email'] = data['email'].lower().strip()
        
        if 'password' in data and data['password']:
            user['password'] = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Apenas admin pode alterar role e status
        if current_user['role'] == 'admin':
            if 'role' in data:
                user['role'] = data['role']
            if 'active' in data:
                user['active'] = data['active']
        
        user['updated_at'] = datetime.now().isoformat()
        
        # Retornar usuário sem senha
        safe_user = user.copy()
        safe_user.pop('password')
        
        logger.info(f"Usuário {user_id} atualizado por: {current_user_email}")
        return jsonify(safe_user), 200
        
    except Exception as e:
        logger.error(f"Erro ao atualizar usuário {user_id}: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@users_validated_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(user_id):
    """Deletar usuário (apenas admin)"""
    try:
        user_index = next((i for i, u in enumerate(users_db) if u['id'] == user_id), None)
        if user_index is None:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        deleted_user = users_db.pop(user_index)
        
        logger.info(f"Usuário {user_id} ({deleted_user['email']}) deletado por admin: {get_jwt_identity()}")
        return jsonify({'message': 'Usuário deletado com sucesso'}), 200
        
    except Exception as e:
        logger.error(f"Erro ao deletar usuário {user_id}: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@users_validated_bp.route('/users/<int:user_id>/toggle-status', methods=['PUT'])
@jwt_required()
@admin_required
def toggle_user_status(user_id):
    """Ativar/desativar usuário (apenas admin)"""
    try:
        user = next((u for u in users_db if u['id'] == user_id), None)
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        user['active'] = not user['active']
        user['updated_at'] = datetime.now().isoformat()
        
        status = 'ativado' if user['active'] else 'desativado'
        
        logger.info(f"Usuário {user_id} {status} por admin: {get_jwt_identity()}")
        return jsonify({
            'message': f'Usuário {status} com sucesso',
            'active': user['active']
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao alterar status do usuário {user_id}: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

