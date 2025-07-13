from flask import Blueprint, request, jsonify
from models.user import User, db
from models.indication import Indication
from models.commission import Commission
from datetime import datetime, timedelta
from sqlalchemy import func, extract

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/ambassador/<int:ambassador_id>', methods=['GET'])
def ambassador_dashboard(ambassador_id):
    """
    Dashboard específico para uma embaixadora
    """
    try:
        # Verificar se embaixadora existe
        ambassador = User.query.get(ambassador_id)
        if not ambassador:
            return jsonify({
                'success': False,
                'message': 'Embaixadora não encontrada'
            }), 404
        
        # Estatísticas básicas
        total_indications = Indication.query.filter_by(ambassador_id=ambassador_id).count()
        approved_sales = Indication.query.filter_by(ambassador_id=ambassador_id, status='aprovado').count()
        
        # Comissões
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        current_month_commissions = Commission.query.filter(
            Commission.ambassador_id == ambassador_id,
            extract('month', Commission.due_date) == current_month,
            extract('year', Commission.due_date) == current_year
        ).all()
        
        current_month_commission_amount = sum(c.amount for c in current_month_commissions)
        
        # Taxa de conversão
        conversion_rate = (approved_sales / total_indications * 100) if total_indications > 0 else 0
        
        # Comissões por mês (últimos 12 meses)
        monthly_commissions = []
        for i in range(12):
            date = datetime.now() - timedelta(days=30 * i)
            month_commissions = Commission.query.filter(
                Commission.ambassador_id == ambassador_id,
                extract('month', Commission.due_date) == date.month,
                extract('year', Commission.due_date) == date.year
            ).all()
            
            monthly_commissions.append({
                'month': date.strftime('%Y-%m'),
                'total': sum(c.amount for c in month_commissions)
            })
        
        monthly_commissions.reverse()
        
        # Indicações por nicho
        niche_stats = db.session.query(
            Indication.niche,
            func.count(Indication.id).label('count')
        ).filter_by(ambassador_id=ambassador_id).group_by(Indication.niche).all()
        
        niche_list = [{'niche': niche, 'count': count} for niche, count in niche_stats]
        
        return jsonify({
            'success': True,
            'dashboard': {
                'ambassador': ambassador.to_dict(),
                'stats': {
                    'total_indications': total_indications,
                    'approved_sales': approved_sales,
                    'current_month_commission': current_month_commission_amount,
                    'conversion_rate': round(conversion_rate, 1)
                },
                'monthly_commissions': monthly_commissions,
                'niche_stats': niche_list
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao gerar dashboard: {str(e)}'
        }), 500

@dashboard_bp.route('/admin', methods=['GET'])
def admin_dashboard():
    """
    Dashboard geral para administradores
    """
    try:
        # Estatísticas gerais
        total_indications = Indication.query.count()
        total_sales = Indication.query.filter_by(status='aprovado').count()
        total_ambassadors = User.query.filter_by(user_type='embaixadora').count()
        
        # Comissões a pagar no mês atual
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        current_month_commissions = Commission.query.filter(
            extract('month', Commission.due_date) == current_month,
            extract('year', Commission.due_date) == current_year,
            Commission.payment_status == 'pendente'
        ).all()
        
        commissions_to_pay = sum(c.amount for c in current_month_commissions)
        
        # Taxa de conversão geral
        conversion_rate = (total_sales / total_indications * 100) if total_indications > 0 else 0
        
        # Indicações por mês (últimos 12 meses)
        monthly_indications = []
        for i in range(12):
            date = datetime.now() - timedelta(days=30 * i)
            month_indications = Indication.query.filter(
                extract('month', Indication.created_at) == date.month,
                extract('year', Indication.created_at) == date.year
            ).count()
            
            monthly_indications.append({
                'month': date.strftime('%Y-%m'),
                'count': month_indications
            })
        
        monthly_indications.reverse()
        
        # Vendas por mês (últimos 12 meses)
        monthly_sales = []
        for i in range(12):
            date = datetime.now() - timedelta(days=30 * i)
            month_sales = Indication.query.filter(
                Indication.status == 'aprovado',
                extract('month', Indication.sale_approval_date) == date.month,
                extract('year', Indication.sale_approval_date) == date.year
            ).count()
            
            monthly_sales.append({
                'month': date.strftime('%Y-%m'),
                'count': month_sales
            })
        
        monthly_sales.reverse()
        
        # Conversão por segmento
        niche_conversion = db.session.query(
            Indication.niche,
            func.count(Indication.id).label('total'),
            func.sum(func.case([(Indication.status == 'aprovado', 1)], else_=0)).label('approved')
        ).group_by(Indication.niche).all()
        
        niche_list = []
        for niche, total, approved in niche_conversion:
            conversion = (approved / total * 100) if total > 0 else 0
            niche_list.append({
                'niche': niche,
                'total': total,
                'approved': approved or 0,
                'conversion_rate': round(conversion, 1)
            })
        
        # Top embaixadoras por volume de indicações
        top_ambassadors = db.session.query(
            User.name,
            func.count(Indication.id).label('total_indications')
        ).join(Indication, User.id == Indication.ambassador_id)\
         .group_by(User.id, User.name)\
         .order_by(func.count(Indication.id).desc())\
         .limit(5).all()
        
        top_ambassadors_list = [
            {'name': name, 'total_indications': total}
            for name, total in top_ambassadors
        ]
        
        return jsonify({
            'success': True,
            'dashboard': {
                'stats': {
                    'total_indications': total_indications,
                    'total_sales': total_sales,
                    'total_ambassadors': total_ambassadors,
                    'commissions_to_pay': commissions_to_pay,
                    'conversion_rate': round(conversion_rate, 1)
                },
                'monthly_indications': monthly_indications,
                'monthly_sales': monthly_sales,
                'niche_conversion': niche_list,
                'top_ambassadors': top_ambassadors_list
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao gerar dashboard admin: {str(e)}'
        }), 500

@dashboard_bp.route('/stats', methods=['GET'])
def general_stats():
    """
    Estatísticas gerais do sistema
    """
    try:
        # Contadores básicos
        total_users = User.query.count()
        total_ambassadors = User.query.filter_by(user_type='embaixadora').count()
        total_admins = User.query.filter_by(user_type='admin').count()
        total_indications = Indication.query.count()
        total_commissions = Commission.query.count()
        
        # Valores financeiros
        total_commission_value = db.session.query(func.sum(Commission.amount)).scalar() or 0
        paid_commission_value = db.session.query(func.sum(Commission.amount)).filter_by(payment_status='pago').scalar() or 0
        pending_commission_value = total_commission_value - paid_commission_value
        
        return jsonify({
            'success': True,
            'stats': {
                'users': {
                    'total': total_users,
                    'ambassadors': total_ambassadors,
                    'admins': total_admins
                },
                'indications': {
                    'total': total_indications,
                    'approved': Indication.query.filter_by(status='aprovado').count(),
                    'pending': Indication.query.filter_by(status='agendado').count(),
                    'rejected': Indication.query.filter_by(status='não aprovado').count()
                },
                'commissions': {
                    'total_count': total_commissions,
                    'total_value': total_commission_value,
                    'paid_value': paid_commission_value,
                    'pending_value': pending_commission_value,
                    'paid_count': Commission.query.filter_by(payment_status='pago').count(),
                    'pending_count': Commission.query.filter_by(payment_status='pendente').count()
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao gerar estatísticas: {str(e)}'
        }), 500

