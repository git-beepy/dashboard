from flask import Blueprint, request, jsonify
from models.user import User, db

users_bp = Blueprint('users', __name__)

@users_bp.route('/<int:user_id>/status', methods=['PUT'])
def update_user_status(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404

        data = request.get_json()
        new_status = data.get('status')

        if new_status not in ['ativo', 'inativo']:
            return jsonify({'success': False, 'message': 'Status inválido. Use "ativo" ou "inativo"'}), 400

        user.status = new_status
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Status do usuário atualizado com sucesso',
            'user': user.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Erro ao atualizar status do usuário: {str(e)}'}), 500

@users_bp.route('/', methods=['GET'])
def list_users():
    try:
        users = User.query.all()
        users_list = [user.to_dict() for user in users]
        return jsonify({'success': True, 'users': users_list}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao listar usuários: {str(e)}'}), 500


