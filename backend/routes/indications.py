from flask import Blueprint, request, jsonify
from models.user import User, db
from models.indication import Indication
from models.commission import Commission
from datetime import datetime, timedelta

indications_bp = Blueprint('indications', __name__)

@indications_bp.route('/', methods=['GET'])
def list_indications():
    """
    Listar todas as indicações ou filtrar por embaixadora
    """
    try:
        ambassador_id = request.args.get('ambassador_id', type=int)
        
        query = Indication.query
        
        if ambassador_id:
            query = query.filter_by(ambassador_id=ambassador_id)
        
        indications = query.order_by(Indication.created_at.desc()).all()
        
        indications_list = []
        for indication in indications:
            indication_dict = indication.to_dict()
            # Adicionar nome da embaixadora
            ambassador = User.query.get(indication.ambassador_id)
            indication_dict['ambassador_name'] = ambassador.name if ambassador else 'Desconhecido'
            indications_list.append(indication_dict)
        
        return jsonify({
            'success': True,
            'indications': indications_list
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar indicações: {str(e)}'
        }), 500

@indications_bp.route('/', methods=['POST'])
def create_indication():
    """
    Criar nova indicação
    """
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        required_fields = ['client_name', 'email', 'phone']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Campo {field} é obrigatório'
                }), 400
        
        # Usar ambassador_id do usuário logado se não fornecido
        ambassador_id = data.get('ambassador_id', 1)  # Default para teste
        
        # Verificar se embaixadora existe
        ambassador = User.query.get(ambassador_id)
        if not ambassador:
            return jsonify({
                'success': False,
                'message': 'Embaixadora não encontrada'
            }), 404
        
        # Criar nova indicação
        new_indication = Indication(
            ambassador_id=ambassador_id,
            client_name=data['client_name'].strip(),
            email=data['email'].strip(),
            phone=data['phone'].strip(),
            origin=data.get('origin', 'website').strip(),
            segment=data.get('segment', 'outros').strip(),
            notes=data.get('notes', '').strip(),
            status='agendado',
            converted=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.session.add(new_indication)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Indicação criada com sucesso',
            'indication': new_indication.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao criar indicação: {str(e)}'
        }), 500

@indications_bp.route('/<int:indication_id>', methods=['PUT'])
def update_indication():
    """
    Atualizar uma indicação (dados do cliente ou status)
    """
    try:
        indication = Indication.query.get(indication_id)
        
        if not indication:
            return jsonify({
                'success': False,
                'message': 'Indicação não encontrada'
            }), 404
        
        data = request.get_json()
        
        # Atualizar campos de dados do cliente se fornecidos
        if 'client_name' in data:
            indication.client_name = data['client_name'].strip()
        
        if 'email' in data:
            indication.email = data['email'].strip()
        
        if 'phone' in data:
            indication.phone = data['phone'].strip()
        
        if 'origin' in data:
            indication.origin = data['origin'].strip()
        
        if 'segment' in data:
            indication.segment = data['segment'].strip()
        
        if 'notes' in data:
            indication.notes = data['notes'].strip()
        
        if 'converted' in data:
            indication.converted = bool(data['converted'])
        
        # Atualizar status se fornecido
        if 'status' in data:
            new_status = data['status']
            
            if new_status not in ['agendado', 'aprovado', 'não aprovado']:
                return jsonify({
                    'success': False,
                    'message': 'Status inválido'
                }), 400
            
            old_status = indication.status
            indication.status = new_status
            
            # Se mudou para aprovado, criar comissões e definir data de aprovação
            if new_status == 'aprovado' and old_status != 'aprovado':
                indication.sale_approval_date = datetime.now()
                
                # Criar 3 parcelas de comissão
                base_value = 300.00
                for parcel_num in range(1, 4):
                    due_date = indication.sale_approval_date
                    if parcel_num == 1:
                        due_date += timedelta(days=30)
                    elif parcel_num == 2:
                        due_date += timedelta(days=60)
                    elif parcel_num == 3:
                        due_date += timedelta(days=90)
                    
                    commission = Commission(
                        indication_id=indication.id,
                        ambassador_id=indication.ambassador_id,
                        parcel_number=parcel_num,
                        amount=base_value,
                        due_date=due_date,
                        payment_status='pendente',
                        created_at=datetime.now()
                    )
                    db.session.add(commission)
            
            # Se mudou de aprovado para outro status, remover comissões
            elif old_status == 'aprovado' and new_status != 'aprovado':
                Commission.query.filter_by(indication_id=indication.id).delete()
                indication.sale_approval_date = None
        
        # Atualizar timestamp
        indication.updated_at = datetime.now()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Indicação atualizada com sucesso',
            'indication': indication.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao atualizar indicação: {str(e)}'
        }), 500

@indications_bp.route('/<int:indication_id>/status', methods=['PUT'])
def update_indication_status():
    """
    Atualizar apenas o status de uma indicação (rota separada para compatibilidade)
    """
    try:
        indication = Indication.query.get(indication_id)
        
        if not indication:
            return jsonify({
                'success': False,
                'message': 'Indicação não encontrada'
            }), 404
        
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['agendado', 'aprovado', 'não aprovado']:
            return jsonify({
                'success': False,
                'message': 'Status inválido'
            }), 400
        
        old_status = indication.status
        indication.status = new_status
        indication.updated_at = datetime.now()
        
        # Se mudou para aprovado, criar comissões e definir data de aprovação
        if new_status == 'aprovado' and old_status != 'aprovado':
            indication.sale_approval_date = datetime.now()
            
            # Criar 3 parcelas de comissão
            base_value = 300.00
            for parcel_num in range(1, 4):
                due_date = indication.sale_approval_date
                if parcel_num == 1:
                    due_date += timedelta(days=30)
                elif parcel_num == 2:
                    due_date += timedelta(days=60)
                elif parcel_num == 3:
                    due_date += timedelta(days=90)
                
                commission = Commission(
                    indication_id=indication.id,
                    ambassador_id=indication.ambassador_id,
                    parcel_number=parcel_num,
                    amount=base_value,
                    due_date=due_date,
                    payment_status='pendente',
                    created_at=datetime.now()
                )
                
                db.session.add(commission)
        
        # Se mudou de aprovado para outro status, remover comissões
        elif old_status == 'aprovado' and new_status != 'aprovado':
            Commission.query.filter_by(indication_id=indication.id).delete()
            indication.sale_approval_date = None
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Status atualizado com sucesso',
            'indication': indication.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao atualizar indicação: {str(e)}'
        }), 500

@indications_bp.route('/<int:indication_id>', methods=['GET'])
def get_indication(indication_id):
    """
    Obter detalhes de uma indicação específica
    """
    try:
        indication = Indication.query.get(indication_id)
        
        if not indication:
            return jsonify({
                'success': False,
                'message': 'Indicação não encontrada'
            }), 404
        
        indication_dict = indication.to_dict()
        
        # Adicionar nome da embaixadora
        ambassador = User.query.get(indication.ambassador_id)
        indication_dict['ambassador_name'] = ambassador.name if ambassador else 'Desconhecido'
        
        # Adicionar comissões se existirem
        commissions = Commission.query.filter_by(indication_id=indication.id).all()
        indication_dict['commissions'] = [commission.to_dict() for commission in commissions]
        
        return jsonify({
            'success': True,
            'indication': indication_dict
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao buscar indicação: {str(e)}'
        }), 500

@indications_bp.route('/<int:indication_id>', methods=['DELETE'])
def delete_indication(indication_id):
    """
    Excluir uma indicação
    """
    try:
        indication = Indication.query.get(indication_id)
        
        if not indication:
            return jsonify({
                'success': False,
                'message': 'Indicação não encontrada'
            }), 404
        
        # As comissões serão excluídas automaticamente devido ao cascade
        db.session.delete(indication)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Indicação excluída com sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao excluir indicação: {str(e)}'
        }), 500

