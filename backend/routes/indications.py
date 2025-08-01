from flask import Blueprint, request, jsonify
from firebase_admin import firestore
from datetime import datetime, timedelta
from firestore_service import get_firestore_client
from models import user_model, indication_model, commission_model
from commission_utils import create_commission_parcels, save_commission_parcels

indications_bp = Blueprint('indications', __name__)
db = get_firestore_client()

@indications_bp.route('/', methods=['GET'])
def list_indications():
    try:
        ambassador_id = request.args.get('ambassador_id')

        indications_ref = db.collection('indications')
        query = indications_ref

        if ambassador_id:
            query = query.where('ambassadorId', '==', ambassador_id)

        docs = query.order_by('createdAt', direction=firestore.Query.DESCENDING).stream()
        indications = [doc.to_dict() | {'id': doc.id} for doc in docs]

        for ind in indications:
            user_doc = db.collection('users').document(ind.get('ambassadorId')).get()
            ind['ambassadorName'] = user_doc.to_dict().get('name') if user_doc.exists else 'Desconhecido'

        return jsonify({'success': True, 'indications': indications}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao listar indicações: {str(e)}'}), 500

@indications_bp.route('/', methods=['POST'])
def create_indication():
    try:
        data = request.get_json()

        required_fields = ['clientName', 'email', 'phone']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'Campo {field} é obrigatório'}), 400

        ambassador_id = data.get('ambassadorId', 'default_user_id')  # Substitua pelo ID do usuário logado

        user_ref = db.collection('users').document(ambassador_id).get()
        if not user_ref.exists:
            return jsonify({'success': False, 'message': 'Embaixadora não encontrada'}), 404

        now = datetime.now()
        indication_data = {
            'ambassadorId': ambassador_id,
            'clientName': data['clientName'],
            'email': data['email'],
            'phone': data['phone'],
            'origin': data.get('origin', 'website'),
            'segment': data.get('segment', 'outros'),
            'notes': data.get('notes', ''),
            'status': 'agendado',
            'converted': False,
            'createdAt': now,
            'updatedAt': now
        }

        new_ref = db.collection('indications').add(indication_data)
        indication_data['id'] = new_ref[1].id

        return jsonify({'success': True, 'message': 'Indicação criada com sucesso', 'indication': indication_data}), 201
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao criar indicação: {str(e)}'}), 500

@indications_bp.route('/<indication_id>', methods=['PUT'])
def update_indication(indication_id):
    try:
        ref = db.collection('indications').document(indication_id)
        doc = ref.get()
        if not doc.exists:
            return jsonify({'success': False, 'message': 'Indicação não encontrada'}), 404

        data = request.get_json()
        indication_data = doc.to_dict()

        updates = {k: v for k, v in data.items() if k in [
            'clientName', 'email', 'phone', 'origin', 'segment', 'notes', 'converted', 'status']}
        updates['updatedAt'] = datetime.now()

        old_status = indication_data.get('status')
        new_status = updates.get('status', old_status)

        if old_status != 'aprovado' and new_status == 'aprovado':
            updates['saleApprovalDate'] = datetime.now()

            ambassador_doc = db.collection('users').document(indication_data['ambassadorId']).get()
            ambassador_data = ambassador_doc.to_dict()
            ambassador_name = ambassador_data.get('name', '')

            parcels = create_commission_parcels(
                indication_id,
                indication_data['ambassadorId'],
                ambassador_name,
                indication_data['clientName'],
                updates['saleApprovalDate']
            )
            save_commission_parcels(parcels)

        elif old_status == 'aprovado' and new_status != 'aprovado':
            commissions_ref = db.collection('commissions').where('originalIndicationId', '==', indication_id).stream()
            for commission_doc in commissions_ref:
                db.collection('commissions').document(commission_doc.id).delete()
            updates['saleApprovalDate'] = None

        ref.update(updates)
        updated_doc = ref.get().to_dict()
        updated_doc['id'] = indication_id

        return jsonify({'success': True, 'message': 'Indicação atualizada com sucesso', 'indication': updated_doc}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao atualizar indicação: {str(e)}'}), 500

@indications_bp.route('/<indication_id>/status', methods=['PUT'])
def update_indication_status(indication_id):
    try:
        ref = db.collection('indications').document(indication_id)
        doc = ref.get()
        if not doc.exists:
            return jsonify({'success': False, 'message': 'Indicação não encontrada'}), 404

        data = request.get_json()
        new_status = data.get('status')
        if new_status not in ['agendado', 'aprovado', 'não aprovado']:
            return jsonify({'success': False, 'message': 'Status inválido'}), 400

        indication_data = doc.to_dict()
        old_status = indication_data.get('status')

        updates = {
            'status': new_status,
            'updatedAt': datetime.now()
        }

        if old_status != 'aprovado' and new_status == 'aprovado':
            updates['saleApprovalDate'] = datetime.now()

            ambassador_doc = db.collection('users').document(indication_data['ambassadorId']).get()
            ambassador_data = ambassador_doc.to_dict()
            ambassador_name = ambassador_data.get('name', '')

            parcels = create_commission_parcels(
                indication_id,
                indication_data['ambassadorId'],
                ambassador_name,
                indication_data['clientName'],
                updates['saleApprovalDate']
            )
            save_commission_parcels(parcels)

        elif old_status == 'aprovado' and new_status != 'aprovado':
            commissions_ref = db.collection('commissions').where('originalIndicationId', '==', indication_id).stream()
            for commission_doc in commissions_ref:
                db.collection('commissions').document(commission_doc.id).delete()
            updates['saleApprovalDate'] = None

        ref.update(updates)
        updated_doc = ref.get().to_dict()
        updated_doc['id'] = indication_id

        return jsonify({'success': True, 'message': 'Status atualizado com sucesso', 'indication': updated_doc}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao atualizar status: {str(e)}'}), 500

@indications_bp.route('/<indication_id>', methods=['GET'])
def get_indication(indication_id):
    try:
        doc = db.collection('indications').document(indication_id).get()
        if not doc.exists:
            return jsonify({'success': False, 'message': 'Indicação não encontrada'}), 404

        indication = doc.to_dict()
        indication['id'] = doc.id

        ambassador_doc = db.collection('users').document(indication['ambassadorId']).get()
        indication['ambassadorName'] = ambassador_doc.to_dict().get('name', 'Desconhecido') if ambassador_doc.exists else 'Desconhecido'

        commissions = db.collection('commissions').where('originalIndicationId', '==', indication_id).stream()
        indication['commissions'] = [c.to_dict() | {'id': c.id} for c in commissions]

        return jsonify({'success': True, 'indication': indication}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao buscar indicação: {str(e)}'}), 500

@indications_bp.route('/<indication_id>', methods=['DELETE'])
def delete_indication(indication_id):
    try:
        doc = db.collection('indications').document(indication_id).get()
        if not doc.exists:
            return jsonify({'success': False, 'message': 'Indicação não encontrada'}), 404

        # Apagar comissões associadas
        commissions = db.collection('commissions').where('originalIndicationId', '==', indication_id).stream()
        for c in commissions:
            db.collection('commissions').document(c.id).delete()

        db.collection('indications').document(indication_id).delete()
        return jsonify({'success': True, 'message': 'Indicação excluída com sucesso'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao excluir indicação: {str(e)}'}), 500
