from flask import Blueprint, request, jsonify
from models.user import User, db
from models.indication import Indication
from models.commission import Commission
from datetime import datetime

commissions_bp = Blueprint('commissions', __name__)

@commissions_bp.route('/', methods=['GET'])
def list_commissions():
    """
    Listar todas as comissões ou filtrar por embaixadora
    """
    try:
        ambassador_id = request.args.get('ambassador_id', type=int)
        status = request.args.get('status')  # pendente, pago
        
        query = Commission.query
        
        if ambassador_id:
            query = query.filter_by(ambassador_id=ambassador_id)
        
        if status:
            query = query.filter_by(payment_status=status)
        
        commissions = query.order_by(Commission.due_date.asc()).all()
        
        commissions_list = []
        for commission in commissions:
            commission_dict = commission.to_dict()
            
            # Adicionar dados da embaixadora
            ambassador = User.query.get(commission.ambassador_id)
            commission_dict['ambassador_name'] = ambassador.name if ambassador else 'Desconhecido'
            
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

@commissions_bp.route('/<int:commission_id>/pay', methods=['PUT'])
def mark_commission_as_paid(commission_id):
    """
    Marcar uma comissão como paga
    """
    try:
        commission = Commission.query.get(commission_id)
        
        if not commission:
            return jsonify({
                'success': False,
                'message': 'Comissão não encontrada'
            }), 404
        
        if commission.payment_status == 'pago':
            return jsonify({
                'success': False,
                'message': 'Comissão já foi paga'
            }), 400
        
        commission.payment_status = 'pago'
        commission.payment_date = datetime.now()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Comissão marcada como paga',
            'commission': commission.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao marcar comissão como paga: {str(e)}'
        }), 500

@commissions_bp.route('/<int:commission_id>/unpay', methods=['PUT'])
def mark_commission_as_unpaid(commission_id):
    """
    Marcar uma comissão como não paga (reverter pagamento)
    """
    try:
        commission = Commission.query.get(commission_id)
        
        if not commission:
            return jsonify({
                'success': False,
                'message': 'Comissão não encontrada'
            }), 404
        
        commission.payment_status = 'pendente'
        commission.payment_date = None
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Pagamento da comissão revertido',
            'commission': commission.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao reverter pagamento: {str(e)}'
        }), 500

@commissions_bp.route('/summary', methods=['GET'])
def commissions_summary():
    """
    Resumo das comissões por embaixadora
    """
    try:
        ambassador_id = request.args.get('ambassador_id', type=int)
        
        query = Commission.query
        
        if ambassador_id:
            query = query.filter_by(ambassador_id=ambassador_id)
        
        commissions = query.all()
        
        # Calcular totais
        total_amount = sum(c.amount for c in commissions)
        paid_amount = sum(c.amount for c in commissions if c.payment_status == 'pago')
        pending_amount = total_amount - paid_amount
        
        # Agrupar por mês
        monthly_summary = {}
        for commission in commissions:
            month_key = commission.due_date.strftime('%Y-%m') if commission.due_date else 'unknown'
            
            if month_key not in monthly_summary:
                monthly_summary[month_key] = {
                    'month': month_key,
                    'total': 0,
                    'paid': 0,
                    'pending': 0
                }
            
            monthly_summary[month_key]['total'] += commission.amount
            
            if commission.payment_status == 'pago':
                monthly_summary[month_key]['paid'] += commission.amount
            else:
                monthly_summary[month_key]['pending'] += commission.amount
        
        return jsonify({
            'success': True,
            'summary': {
                'total_amount': total_amount,
                'paid_amount': paid_amount,
                'pending_amount': pending_amount,
                'total_commissions': len(commissions),
                'paid_commissions': len([c for c in commissions if c.payment_status == 'pago']),
                'pending_commissions': len([c for c in commissions if c.payment_status == 'pendente']),
                'monthly_breakdown': list(monthly_summary.values())
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao gerar resumo: {str(e)}'
        }), 500

