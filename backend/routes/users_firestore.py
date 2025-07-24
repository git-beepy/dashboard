from flask import Blueprint, request, jsonify
from datetime import datetime
import bcrypt

users_bp = Blueprint('users', __name__)

def get_db():
    """Importa o db do main.py"""
    from main import db
    return db

@users_bp.route('/<user_id>/status', methods=['PUT', 'OPTIONS'])
def update_user_status(user_id):
    if request.method == "OPTIONS":
        return "", 200
        
    try:
        db = get_db()
        if not db:
            return jsonify({'success': False, 'message': 'Erro de conexão com banco de dados'}), 500

        # Verificar se o usuário existe
        user_doc = db.collection("users").document(user_id).get()
        if not user_doc.exists:
            return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404

        data = request.get_json()
        new_status = data.get('status')

        if new_status not in ['ativo', 'inativo']:
            return jsonify({'success': False, 'message': 'Status inválido. Use "ativo" ou "inativo"'}), 400

        # Atualizar o status do usuário
        update_data = {
            'status': new_status,
            'updatedAt': datetime.now()
        }
        
        db.collection("users").document(user_id).update(update_data)

        # Buscar dados atualizados do usuário
        updated_user_doc = db.collection("users").document(user_id).get()
        user_data = updated_user_doc.to_dict()
        user_data['id'] = updated_user_doc.id
        # Remover senha se existir
        user_data.pop('password', None)

        return jsonify({
            'success': True,
            'message': 'Status do usuário atualizado com sucesso',
            'user': user_data
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao atualizar status do usuário: {str(e)}'}), 500

@users_bp.route('/', methods=['GET', 'OPTIONS'])
def list_users():
    if request.method == "OPTIONS":
        return "", 200
        
    try:
        db = get_db()
        if not db:
            return jsonify({'success': False, 'message': 'Erro de conexão com banco de dados'}), 500

        users_ref = db.collection("users")
        docs = users_ref.stream()
        users = []

        for doc in docs:
            user_data = doc.to_dict()
            user_data["id"] = doc.id
            # Remover senha se existir
            user_data.pop("password", None)
            users.append(user_data)

        return jsonify({'success': True, 'users': users}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao listar usuários: {str(e)}'}), 500

