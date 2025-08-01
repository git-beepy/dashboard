from datetime import datetime, timedelta
from typing import List, Dict, Any
from models.commission import Commission
from models.indication import Indication
from models.user import User

def create_commission_parcels(indication_id: int, ambassador_id: int, ambassador_name: str, client_name: str, approval_date: datetime = None) -> List[Commission]:
    """
    Criar 3 parcelas de comissão para uma indicação aprovada
    
    Args:
        indication_id: ID da indicação original
        ambassador_id: ID da embaixadora
        ambassador_name: Nome da embaixadora
        client_name: Nome do cliente
        approval_date: Data de aprovação (padrão: agora)
    
    Returns:
        Lista de objetos Commission criados
    """
    if approval_date is None:
        approval_date = datetime.now()
    
    base_value = 300.00  # R$ 900,00 dividido em 3 parcelas
    parcels = []
    
    for i in range(3):
        due_date = approval_date
        if i == 1:  # 2ª parcela: 30 dias após a indicação
            due_date += timedelta(days=30)
        elif i == 2:  # 3ª parcela: 90 dias após a indicação
            due_date += timedelta(days=90)
        
        commission_data = {
            'originalIndicationId': indication_id,
            'ambassadorId': ambassador_id,
            'ambassadorName': ambassador_name,
            'clientName': client_name,
            'parcelNumber': i + 1,
            'value': base_value,
            'dueDate': due_date,
            'status': 'pendente',
            'createdAt': datetime.now(),
            'updatedAt': datetime.now()
        }
        
        commission = Commission(commission_data)
        parcels.append(commission)
    
    return parcels

def update_overdue_commissions() -> int:
    """
    Atualizar status de comissões pendentes que estão em atraso
    
    Returns:
        Número de comissões atualizadas
    """
    from datetime import date
    from models import db
    
    # Buscar comissões pendentes com data de vencimento passada
    overdue_commissions = Commission.query.filter(
        Commission.status == 'pendente',
        Commission.due_date < date.today()
    ).all()
    
    updated_count = 0
    for commission in overdue_commissions:
        commission.status = 'atrasado'
        commission.updated_at = datetime.now()
        updated_count += 1
    
    db.session.commit()
    return updated_count

def get_commission_summary(ambassador_id: int = None) -> Dict[str, Any]:
    """
    Obter resumo das comissões
    
    Args:
        ambassador_id: ID da embaixadora (opcional, para filtrar)
    
    Returns:
        Dicionário com resumo das comissões
    """
    query = Commission.query
    
    if ambassador_id:
        query = query.filter_by(ambassador_id=ambassador_id)
    
    commissions = query.all()
    
    # Calcular totais
    total_amount = sum(c.value for c in commissions)
    paid_amount = sum(c.value for c in commissions if c.status == 'pago')
    pending_amount = sum(c.value for c in commissions if c.status == 'pendente')
    overdue_amount = sum(c.value for c in commissions if c.status == 'atrasado')
    
    # Agrupar por mês
    monthly_summary = {}
    for commission in commissions:
        month_key = commission.due_date.strftime('%Y-%m') if commission.due_date else 'unknown'
        
        if month_key not in monthly_summary:
            monthly_summary[month_key] = {
                'month': month_key,
                'total': 0,
                'paid': 0,
                'pending': 0,
                'overdue': 0
            }
        
        monthly_summary[month_key]['total'] += commission.value
        
        if commission.status == 'pago':
            monthly_summary[month_key]['paid'] += commission.value
        elif commission.status == 'pendente':
            monthly_summary[month_key]['pending'] += commission.value
        elif commission.status == 'atrasado':
            monthly_summary[month_key]['overdue'] += commission.value
    
    return {
        'total_amount': total_amount,
        'paid_amount': paid_amount,
        'pending_amount': pending_amount,
        'overdue_amount': overdue_amount,
        'total_commissions': len(commissions),
        'paid_commissions': len([c for c in commissions if c.status == 'pago']),
        'pending_commissions': len([c for c in commissions if c.status == 'pendente']),
        'overdue_commissions': len([c for c in commissions if c.status == 'atrasado']),
        'monthly_breakdown': list(monthly_summary.values())
    }

def get_ambassador_commissions(ambassador_id: int, status: str = None, month: int = None, year: int = None) -> List[Dict[str, Any]]:
    """
    Obter comissões de uma embaixadora específica
    
    Args:
        ambassador_id: ID da embaixadora
        status: Status das comissões (opcional)
        month: Mês para filtrar (1-12, opcional)
        year: Ano para filtrar (opcional)
    
    Returns:
        Lista de comissões
    """
    query = Commission.query.filter_by(ambassador_id=ambassador_id)
    
    if status:
        query = query.filter_by(status=status)
    
    # Filtrar por mês e ano se fornecidos
    if month and year:
        from sqlalchemy import extract
        query = query.filter(
            extract('month', Commission.due_date) == month,
            extract('year', Commission.due_date) == year
        )
    elif year:
        from sqlalchemy import extract
        query = query.filter(extract('year', Commission.due_date) == year)
    
    commissions = query.order_by(Commission.due_date.asc()).all()
    
    return [commission.to_dict() for commission in commissions]

def calculate_expected_earnings(ambassador_id: int, start_date: datetime = None, end_date: datetime = None) -> Dict[str, float]:
    """
    Calcular ganhos esperados de uma embaixadora em um período
    
    Args:
        ambassador_id: ID da embaixadora
        start_date: Data de início (opcional)
        end_date: Data de fim (opcional)
    
    Returns:
        Dicionário com ganhos esperados
    """
    query = Commission.query.filter_by(ambassador_id=ambassador_id)
    
    if start_date:
        query = query.filter(Commission.due_date >= start_date)
    
    if end_date:
        query = query.filter(Commission.due_date <= end_date)
    
    commissions = query.all()
    
    total_expected = sum(c.value for c in commissions)
    total_paid = sum(c.value for c in commissions if c.status == 'pago')
    total_pending = sum(c.value for c in commissions if c.status == 'pendente')
    total_overdue = sum(c.value for c in commissions if c.status == 'atrasado')
    
    return {
        'total_expected': total_expected,
        'total_paid': total_paid,
        'total_pending': total_pending,
        'total_overdue': total_overdue,
        'payment_percentage': (total_paid / total_expected * 100) if total_expected > 0 else 0
    }

