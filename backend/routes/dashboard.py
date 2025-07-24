from flask import Blueprint, request, jsonify
from models.user import User, db
from models.indication import Indication
from models.commission import Commission
from datetime import datetime, timedelta
from sqlalchemy import func, extract

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/ambassador', methods=['GET'])
def current_ambassador_dashboard():
    """
    Dashboard para a embaixadora logada
    """
    from flask_jwt_extended import get_jwt_identity
    
    try:
        # Obter ID do usuário logado
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return jsonify({
                'success': False,
                'message': 'Token inválido'
            }), 401
        
        # Redirecionar para o dashboard específico da embaixadora
        return ambassador_dashboard(current_user_id)
        
    except Exception as e:
        print(f"Erro no dashboard embaixadora atual: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro ao gerar dashboard: {str(e)}'
        }), 500

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
        total_indications = Indication.query.filter_by(ambassadorId=ambassador_id).count()
        approved_sales = Indication.query.filter_by(ambassadorId=ambassador_id, status='aprovado').count()
        
        # Comissões
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        current_month_commissions = Commission.query.filter(
            Commission.ambassadorId == ambassador_id,
            extract('month', Commission.createdAt) == current_month,
            extract('year', Commission.createdAt) == current_year
        ).all()
        
        current_month_commission_amount = sum(c.value for c in current_month_commissions)
        
        # Taxa de conversão
        conversion_rate = (approved_sales / total_indications * 100) if total_indications > 0 else 0
        
        # Comissões por mês (últimos 12 meses)
        monthly_commissions = []
        months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        
        for i in range(12):
            date = datetime.now() - timedelta(days=30 * (11 - i))
            month_commissions = Commission.query.filter(
                Commission.ambassadorId == ambassador_id,
                extract('month', Commission.createdAt) == date.month,
                extract('year', Commission.createdAt) == date.year
            ).all()
            
            monthly_commissions.append({
                'month': months[date.month - 1],
                'comissao': sum(c.value for c in month_commissions)
            })
        
        # Indicações por segmento
        segment_stats = db.session.query(
            Indication.segment,
            func.count(Indication.id).label('count')
        ).filter_by(ambassadorId=ambassador_id).group_by(Indication.segment).all()
        
        total_segment_indications = sum(count for _, count in segment_stats)
        segment_list = []
        colors = ['#EF4444', '#3B82F6', '#8B5CF6', '#F59E0B']
        
        for i, (segment, count) in enumerate(segment_stats):
            percentage = (count / total_segment_indications * 100) if total_segment_indications > 0 else 0
            segment_list.append({
                'name': (segment or 'Não informado').upper(),
                'value': round(percentage, 1),
                'color': colors[i % len(colors)]
            })
        
        return jsonify({
            'totalIndications': total_indications,
            'totalSales': approved_sales,
            'monthlyCommission': current_month_commission_amount,
            'conversionRate': round(conversion_rate, 1),
            'commissionsData': monthly_commissions,
            'segmentData': segment_list
        }), 200
        
    except Exception as e:
        print(f"Erro no dashboard embaixadora: {str(e)}")
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
        total_ambassadors = User.query.filter_by(role='embaixadora').count()
        
        # Embaixadoras ativas (últimos 60 dias)
        sixty_days_ago = datetime.now() - timedelta(days=60)
        active_ambassadors = db.session.query(User.id).join(Indication, User.id == Indication.ambassadorId)\
            .filter(Indication.createdAt >= sixty_days_ago)\
            .filter(User.role == 'embaixadora')\
            .distinct().count()
        
        # Comissões do mês atual
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        current_month_commissions = Commission.query.filter(
            extract('month', Commission.createdAt) == current_month,
            extract('year', Commission.createdAt) == current_year
        ).all()
        
        monthly_commissions = sum(c.value for c in current_month_commissions)
        
        # Taxa de conversão geral
        conversion_rate = (total_sales / total_indications * 100) if total_indications > 0 else 0
        
        # Porcentagem de embaixadoras ativas
        active_percentage = (active_ambassadors / total_ambassadors * 100) if total_ambassadors > 0 else 0
        
        # Indicações por mês (últimos 12 meses)
        monthly_indications = []
        months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        
        for i in range(12):
            date = datetime.now() - timedelta(days=30 * (11 - i))
            month_indications = Indication.query.filter(
                extract('month', Indication.createdAt) == date.month,
                extract('year', Indication.createdAt) == date.year
            ).count()
            
            monthly_indications.append({
                'month': months[date.month - 1],
                'count': month_indications
            })
        
        # Leads por origem
        leads_origin = db.session.query(
            Indication.origin,
            func.count(Indication.id).label('count')
        ).group_by(Indication.origin).all()
        
        leads_list = [{'name': origin or 'Não informado', 'value': count} for origin, count in leads_origin]
        
        # Conversão por segmento
        segment_conversion = db.session.query(
            Indication.segment,
            func.count(Indication.id).label('total'),
            func.sum(func.case([(Indication.status == 'aprovado', 1)], else_=0)).label('converted')
        ).group_by(Indication.segment).all()
        
        segment_list = []
        for segment, total, converted in segment_conversion:
            rate = (converted / total * 100) if total > 0 else 0
            segment_list.append({
                'segment': segment or 'Não informado',
                'total': total,
                'converted': converted or 0,
                'rate': round(rate, 1)
            })
        
        # Vendas por mês (últimos 12 meses)
        monthly_sales = []
        for i in range(12):
            date = datetime.now() - timedelta(days=30 * (11 - i))
            month_sales_count = Indication.query.filter(
                Indication.status == 'aprovado',
                extract('month', Indication.createdAt) == date.month,
                extract('year', Indication.createdAt) == date.year
            ).count()
            
            # Simular valor de vendas (R$ 1000 por venda aprovada)
            month_sales_value = month_sales_count * 1000
            
            monthly_sales.append({
                'month': months[date.month - 1],
                'value': month_sales_value
            })
        
        # Top embaixadoras por volume de indicações
        top_ambassadors = db.session.query(
            User.name,
            func.count(Indication.id).label('total_indications')
        ).join(Indication, User.id == Indication.ambassadorId)\
         .group_by(User.id, User.name)\
         .order_by(func.count(Indication.id).desc())\
         .limit(10).all()
        
        top_ambassadors_list = [
            {'name': name, 'indications': total}
            for name, total in top_ambassadors
        ]
        
        return jsonify({
            'stats': {
                'totalIndications': total_indications,
                'monthlyCommissions': monthly_commissions,
                'activePercentage': round(active_percentage, 1),
                'activeAmbassadors': active_ambassadors
            },
            'charts': {
                'indicationsMonthly': monthly_indications,
                'leadsOrigin': leads_list,
                'conversionBySegment': segment_list,
                'salesMonthly': monthly_sales,
                'topAmbassadors': top_ambassadors_list
            }
        }), 200
        
    except Exception as e:
        print(f"Erro no dashboard admin: {str(e)}")
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

