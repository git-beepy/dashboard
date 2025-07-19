from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.user import User, db
from datetime import datetime, timedelta
import bcrypt

auth_bp = Blueprint('auth', __name__)


def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())


@auth_bp.route('/login', methods=['POST'])
def login():
    """Rota de login com JWT"""
    try:
        # Forçar o parsing do JSON
        data = request.get_json(force=True)

        if not data:
            return jsonify({"success": False, "message": "Dados não fornecidos"}), 400

        email = data.get('email', '').strip()
        password = data.get('password', '').strip()

        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Email e senha são obrigatórios'
            }), 400

        user = User.query.filter_by(email=email).first()

        if not user or not check_password(password, user.password):
            return jsonify({
                'success': False,
                'message': 'Credenciais inválidas'
            }), 401

        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                'name': user.name,
                'email': user.email,
                'user_type': user.user_type
            },
            expires_delta=timedelta(hours=24)
        )

        return jsonify({
            'success': True,
            'access_token': access_token,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'user_type': user.user_type
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro no login: {str(e)}'
        }), 500


@auth_bp.route('/register', methods=['POST'])
def register():
    """Rota de registro com validação"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Dados não fornecidos'}), 400

        required_fields = ['name', 'email', 'user_type', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Campo {field} é obrigatório'
                }), 400

        name = data['name'].strip()
        email = data['email'].strip().lower()
        user_type = data['user_type'].strip()
        password = data['password'].strip()

        if len(password) < 8:
            return jsonify({
                'success': False,
                'message': 'Senha deve ter pelo menos 8 caracteres'
            }), 400

        if user_type not in ['embaixadora', 'admin']:
            return jsonify({
                'success': False,
                'message': 'Tipo de usuário inválido'
            }), 400

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({
                'success': False,
                'message': 'Email já cadastrado'
            }), 409

        new_user = User(
            name=name,
            email=email,
            user_type=user_type,
            password=hash_password(password),
            created_at=datetime.utcnow()
        )

        db.session.add(new_user)
        db.session.commit()

        access_token = create_access_token(
            identity=new_user.id,
            additional_claims={
                'name': new_user.name,
                'email': new_user.email,
                'user_type': new_user.user_type
            }
        )

        return jsonify({
            'success': True,
            'access_token': access_token,
            'user': {
                'id': new_user.id,
                'name': new_user.name,
                'email': new_user.email,
                'user_type': new_user.user_type
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro no registro: {str(e)}'
        }), 500


@auth_bp.route('/validate-token', methods=['GET'])
@jwt_required()
def validate_token():
    """Validação de token JWT"""
    try:
        current_user = get_jwt_identity()
        user = User.query.get(current_user)

        if not user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 404

        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'user_type': user.user_type
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Token inválido: {str(e)}'
        }), 401


@auth_bp.route('/api/auth/users', methods=['GET'])
@jwt_required()
def list_users():
    """Lista de usuários (apenas admin)"""
    try:
        current_user = get_jwt_identity()
        user = User.query.get(current_user)

        if not user or user.user_type != 'admin':
            return jsonify({
                'success': False,
                'message': 'Acesso não autorizado'
            }), 403

        users = User.query.all()
        users_list = [{
            'id': u.id,
            'name': u.name,
            'email': u.email,
            'user_type': u.user_type,
            'created_at': u.created_at.isoformat()
        } for u in users]

        return jsonify({
            'success': True,
            'users': users_list
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar usuários: {str(e)}'
        }), 500


@auth_bp.route('/api/auth/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Obter detalhes de um usuário"""
    try:
        current_user = get_jwt_identity()
        requesting_user = User.query.get(current_user)
        user = User.query.get(user_id)

        if not user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 404

        # Apenas admin ou o próprio usuário pode ver os detalhes
        if requesting_user.user_type != 'admin' and requesting_user.id != user.id:
            return jsonify({
                'success': False,
                'message': 'Acesso não autorizado'
            }), 403

        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'user_type': user.user_type,
                'created_at': user.created_at.isoformat()
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar usuário: {str(e)}'
        }), 500


@auth_bp.route('/api/auth/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Atualizar usuário"""
    try:
        current_user = get_jwt_identity()
        requesting_user = User.query.get(current_user)
        user = User.query.get(user_id)

        if not user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 404

        # Apenas admin ou o próprio usuário pode atualizar
        if requesting_user.user_type != 'admin' and requesting_user.id != user.id:
            return jsonify({
                'success': False,
                'message': 'Acesso não autorizado'
            }), 403

        data = request.get_json()

        if 'name' in data:
            user.name = data['name'].strip()

        if 'email' in data:
            new_email = data['email'].strip().lower()
            if new_email != user.email:
                existing_user = User.query.filter_by(email=new_email).first()
                if existing_user:
                    return jsonify({
                        'success': False,
                        'message': 'Email já está em uso'
                    }), 409
                user.email = new_email

        if 'user_type' in data and requesting_user.user_type == 'admin':
            if data['user_type'] in ['embaixadora', 'admin']:
                user.user_type = data['user_type']

        if 'password' in data and data['password']:
            if len(data['password']) < 8:
                return jsonify({
                    'success': False,
                    'message': 'Senha deve ter pelo menos 8 caracteres'
                }), 400
            user.password = hash_password(data['password'])

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Usuário atualizado com sucesso',
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'user_type': user.user_type
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao atualizar usuário: {str(e)}'
        }), 500


@auth_bp.route('/api/auth/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Deletar usuário (apenas admin)"""
    try:
        current_user = get_jwt_identity()
        requesting_user = User.query.get(current_user)
        user = User.query.get(user_id)

        if not user:
            return jsonify({
                'success': False,
                'message': 'Usuário não encontrado'
            }), 404

        if requesting_user.user_type != 'admin':
            return jsonify({
                'success': False,
                'message': 'Acesso não autorizado'
            }), 403

        if user.email == 'admin@beepy.com':
            return jsonify({
                'success': False,
                'message': 'Não é possível excluir o administrador principal'
            }), 403

        db.session.delete(user)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Usuário excluído com sucesso'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao excluir usuário: {str(e)}'
        }), 500

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"message": "Usuário não encontrado"}), 404
    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "user_type": user.user_type
    }), 200


