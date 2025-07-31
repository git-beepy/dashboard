from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User, db
from models.indication import Indication
from models.commission import Commission
from datetime import datetime

ambassador_bp = Blueprint('ambassador', __name__)

def check_ambassador_permission():
    """Verificar se o usuário atual é embaixadora"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return user and user.role == 'embaixadora'

@ambassador_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def ambassador_dashboard():
    """Dashboard para Embaixadora"""
    try:
        if not check_ambassador_permission():
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas embaixadoras.'
            }), 403
        
        current_user_id = get_jwt_identity()
        
        # Estatísticas das indicações da embaixadora
        total_indications = Indication.query.filter_by(ambassador_id=current_user_id).count()
        approved_indications = Indication.query.filter_by(
            ambassador_id=current_user_id, status='aprovado'
        ).count()
        pending_indications = Indication.query.filter_by(
            ambassador_id=current_user_id, status='agendado'
        ).count()
        rejected_indications = Indication.query.filter_by(
            ambassador_id=current_user_id, status='não aprovado'
        ).count()
        
        # Estatísticas de comissões da embaixadora
        commissions = Commission.query.filter_by(ambassador_id=current_user_id).all()
        
        # Atualizar status de comissões em atraso
        today = datetime.now().date()
        for commission in commissions:
            if (commission.payment_status == 'pendente' and 
                commission.due_date and 
                commission.due_date.date() < today):
                commission.payment_status = 'em atraso'
        
        db.session.commit()
        
        # Calcular valores
        total_amount = sum(c.amount for c in commissions)
        paid_amount = sum(c.amount for c in commissions if c.payment_status == 'pago')
        pending_amount = sum(c.amount for c in commissions if c.payment_status == 'pendente')
        overdue_amount = sum(c.amount for c in commissions if c.payment_status == 'em atraso')
        
        # Contadores de parcelas
        total_commissions = len(commissions)
        paid_commissions = len([c for c in commissions if c.payment_status == 'pago'])
        pending_commissions = len([c for c in commissions if c.payment_status == 'pendente'])
        overdue_commissions = len([c for c in commissions if c.payment_status == 'em atraso'])
        
        # Dados para gráfico mensal
        monthly_data = {}
        
        for commission in commissions:
            if commission.due_date:
                month_key = commission.due_date.strftime('%Y-%m')
                if month_key not in monthly_data:
                    monthly_data[month_key] = {
                        'month': month_key,
                        'total': 0,
                        'paid': 0,
                        'pending': 0,
                        'overdue': 0
                    }
                
                monthly_data[month_key]['total'] += commission.amount
                if commission.payment_status == 'pago':
                    monthly_data[month_key]['paid'] += commission.amount
                elif commission.payment_status == 'pendente':
                    monthly_data[month_key]['pending'] += commission.amount
                elif commission.payment_status == 'em atraso':
                    monthly_data[month_key]['overdue'] += commission.amount
        
        return jsonify({
            'success': True,
            'dashboard': {
                'indication_stats': {
                    'total_indications': total_indications,
                    'approved_indications': approved_indications,
                    'pending_indications': pending_indications,
                    'rejected_indications': rejected_indications
                },
                'commission_stats': {
                    'total_commissions': total_commissions,
                    'paid_commissions': paid_commissions,
                    'pending_commissions': pending_commissions,
                    'overdue_commissions': overdue_commissions
                },
                'financial_stats': {
                    'total_amount': total_amount,
                    'paid_amount': paid_amount,
                    'pending_amount': pending_amount,
                    'overdue_amount': overdue_amount
                },
                'monthly_data': list(monthly_data.values())
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao carregar dashboard: {str(e)}'
        }), 500

@ambassador_bp.route('/indications', methods=['GET'])
@jwt_required()
def ambassador_list_indications():
    """Listar apenas as indicações da embaixadora logada"""
    try:
        if not check_ambassador_permission():
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas embaixadoras.'
            }), 403
        
        current_user_id = get_jwt_identity()
        
        indications = Indication.query.filter_by(
            ambassador_id=current_user_id
        ).order_by(Indication.created_at.desc()).all()
        
        indications_list = []
        for indication in indications:
            indication_dict = indication.to_dict()
            
            # Adicionar comissões da indicação
            commissions = Commission.query.filter_by(indication_id=indication.id).all()
            indication_dict['commissions'] = [c.to_dict() for c in commissions]
            
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

@ambassador_bp.route('/commissions', methods=['GET'])
@jwt_required()
def ambassador_list_commissions():
    """Listar apenas as comissões da embaixadora logada"""
    try:
        if not check_ambassador_permission():
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas embaixadoras.'
            }), 403
        
        current_user_id = get_jwt_identity()
        
        commissions = Commission.query.filter_by(
            ambassador_id=current_user_id
        ).order_by(Commission.due_date.asc()).all()
        
        # Atualizar status de comissões em atraso
        today = datetime.now().date()
        for commission in commissions:
            if (commission.payment_status == 'pendente' and 
                commission.due_date and 
                commission.due_date.date() < today):
                commission.payment_status = 'em atraso'
        
        db.session.commit()
        
        commissions_list = []
        for commission in commissions:
            commission_dict = commission.to_dict()
            
            # Adicionar dados da indicação
            indication = Indication.query.get(commission.indication_id)
            commission_dict['client_name'] = indication.client_name if indication else 'Desconhecido'
            
            commissions_list.append(commission_dict)
        
        return jsonify({
            'success': True,
            'commissions': commissions_list
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao listar comissões: {str(e)}'
        }), 500

