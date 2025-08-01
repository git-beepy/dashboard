from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User, db
from models.indication import Indication
from models.commission import Commission
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)


def check_admin_permission():
    """Verificar se o usuário atual é admin"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return user and user.role == 'admin'


@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def admin_dashboard():
    """Dashboard completo para Admin"""
    try:
        if not check_admin_permission():
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores.'
            }), 403

        # Estatísticas gerais
        total_indications = Indication.query.count()
        approved_indications = Indication.query.filter_by(status='aprovado').count()
        pending_indications = Indication.query.filter_by(status='agendado').count()
        rejected_indications = Indication.query.filter_by(status='não aprovado').count()

        # Estatísticas de comissões
        total_commissions = Commission.query.count()
        paid_commissions = Commission.query.filter_by(payment_status='pago').count()
        pending_commissions = Commission.query.filter_by(payment_status='pendente').count()
        overdue_commissions = Commission.query.filter_by(payment_status='em atraso').count()

        # Valores financeiros
        total_amount = db.session.query(db.func.sum(Commission.amount)).scalar() or 0
        paid_amount = db.session.query(db.func.sum(Commission.amount)).filter(
            Commission.payment_status == 'pago'
        ).scalar() or 0
        pending_amount = db.session.query(db.func.sum(Commission.amount)).filter(
            Commission.payment_status == 'pendente'
        ).scalar() or 0
        overdue_amount = db.session.query(db.func.sum(Commission.amount)).filter(
            Commission.payment_status == 'em atraso'
        ).scalar() or 0

        # Estatísticas por embaixadora
        ambassadors_stats = []
        ambassadors = User.query.filter_by(role='embaixadora').all()

        for ambassador in ambassadors:
            ambassador_indications = Indication.query.filter_by(ambassador_id=ambassador.id).count()
            ambassador_approved = Indication.query.filter_by(
                ambassador_id=ambassador.id, status='aprovado'
            ).count()
            ambassador_commissions = Commission.query.filter_by(ambassador_id=ambassador.id)
            ambassador_total = sum(c.amount for c in ambassador_commissions)
            ambassador_paid = sum(c.amount for c in ambassador_commissions if c.payment_status == 'pago')
            ambassador_pending = sum(c.amount for c in ambassador_commissions if c.payment_status == 'pendente')
            ambassador_overdue = sum(c.amount for c in ambassador_commissions if c.payment_status == 'em atraso')

            ambassadors_stats.append({
                'id': ambassador.id,
                'name': ambassador.name,
                'email': ambassador.email,
                'total_indications': ambassador_indications,
                'approved_indications': ambassador_approved,
                'total_amount': ambassador_total,
                'paid_amount': ambassador_paid,
                'pending_amount': ambassador_pending,
                'overdue_amount': ambassador_overdue
            })

        # Dados para gráfico mensal
        monthly_data = {}
        commissions = Commission.query.all()

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
                'general_stats': {
                    'total_indications': total_indications,
                    'approved_indications': approved_indications,
                    'pending_indications': pending_indications,
                    'rejected_indications': rejected_indications,
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
                'ambassadors_stats': ambassadors_stats,
                'monthly_data': list(monthly_data.values())
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao carregar dashboard: {str(e)}'
        }), 500


@admin_bp.route('/indications', methods=['GET'])
@jwt_required()
def admin_list_indications():
    """Listar todas as indicações (Admin)"""
    try:
        if not check_admin_permission():
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores.'
            }), 403

        # Filtros opcionais
        ambassador_id = request.args.get('ambassador_id', type=int)
        status = request.args.get('status')

        query = Indication.query

        if ambassador_id:
            query = query.filter_by(ambassador_id=ambassador_id)

        if status:
            query = query.filter_by(status=status)

        indications = query.order_by(Indication.created_at.desc()).all()

        indications_list = []
        for indication in indications:
            indication_dict = indication.to_dict()
            # Adicionar nome da embaixadora
            ambassador = User.query.get(indication.ambassador_id)
            indication_dict['ambassador_name'] = ambassador.name if ambassador else 'Desconhecido'

            # Adicionar comissões
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


@admin_bp.route('/commissions', methods=['GET'])
@jwt_required()
def admin_list_commissions():
    """Listar todas as comissões com controle de status (Admin)"""
    try:
        if not check_admin_permission():
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores.'
            }), 403

        # Filtros opcionais
        ambassador_id = request.args.get('ambassador_id', type=int)
        status = request.args.get('status')

        query = Commission.query

        if ambassador_id:
            query = query.filter_by(ambassador_id=ambassador_id)

        if status:
            query = query.filter_by(payment_status=status)

        commissions = query.order_by(Commission.due_date.asc()).all()

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


@admin_bp.route('/commissions/<int:commission_id>/status', methods=['PUT'])
@jwt_required()
def admin_update_commission_status(commission_id):
    """Atualizar status de uma comissão (Admin)"""
    try:
        if not check_admin_permission():
            return jsonify({
                'success': False,
                'message': 'Acesso negado. Apenas administradores.'
            }), 403

        commission = Commission.query.get(commission_id)

        if not commission:
            return jsonify({
                'success': False,
                'message': 'Comissão não encontrada'
            }), 404

        data = request.get_json()
        new_status = data.get('status')

        if new_status not in ['pendente', 'pago', 'em atraso']:
            return jsonify({
                'success': False,
                'message': 'Status inválido'
            }), 400

        commission.payment_status = new_status

        if new_status == 'pago':
            commission.payment_date = datetime.now()
        else:
            commission.payment_date = None

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Status da comissão atualizado com sucesso',
            'commission': commission.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao atualizar status: {str(e)}'
        }), 500
