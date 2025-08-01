from datetime import datetime, timedelta
from typing import List, Dict, Any
from firebase_admin import firestore
from models.commission import Commission
from models.indication import Indication
from models.user import User


def create_commission_parcels(indication_id: str, ambassador_id: str, ambassador_name: str, client_name: str,
                              approval_date: datetime = None) -> List[Commission]:
    """
    Criar e salvar 3 parcelas de comissão para uma indicação aprovada (Firestore)

    Args:
        indication_id: ID da indicação
        ambassador_id: ID da embaixadora
        ambassador_name: Nome da embaixadora
        client_name: Nome do cliente
        approval_date: Data de aprovação (opcional)

    Returns:
        Lista de objetos Commission criados
    """
    if approval_date is None:
        approval_date = datetime.now()

    base_value = 300.00
    commissions = []

    for i in range(3):
        due_date = approval_date + timedelta(days=30 * (i + 1))

        commission = Commission({
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
        })

        commissions.append(commission)

    # Salvar no Firestore usando batch
    db = firestore.client()
    batch = db.batch()

    for commission in commissions:
        doc_ref = db.collection('commissions').document()
        batch.set(doc_ref, commission.to_dict())

    batch.commit()

    return commissions


def update_overdue_commissions() -> int:
    """
    Atualiza comissões vencidas no Firestore (status: 'atrasado')

    Returns:
        Número de comissões atualizadas
    """
    db = firestore.client()
    today = datetime.today()

    # Buscar comissões pendentes com dueDate anterior a hoje
    pending_commissions = db.collection('commissions') \
        .where('status', '==', 'pendente') \
        .where('dueDate', '<', today).stream()

    updated_count = 0
    batch = db.batch()

    for doc in pending_commissions:
        batch.update(doc.reference, {
            'status': 'atrasado',
            'updatedAt': datetime.now()
        })
        updated_count += 1

    if updated_count > 0:
        batch.commit()

    return updated_count


def get_commission_summary(ambassador_id: str = None) -> Dict[str, Any]:
    """
    Obter resumo das comissões de uma embaixadora (Firestore)

    Args:
        ambassador_id: ID da embaixadora (opcional)

    Returns:
        Dicionário com resumo das comissões
    """
    db = firestore.client()

    query = db.collection('commissions')
    if ambassador_id:
        query = query.where('ambassadorId', '==', ambassador_id)

    commissions = [Commission(doc.to_dict()) for doc in query.stream()]

    total_amount = sum(c.value for c in commissions)
    paid_amount = sum(c.value for c in commissions if c.status == 'pago')
    pending_amount = sum(c.value for c in commissions if c.status == 'pendente')
    overdue_amount = sum(c.value for c in commissions if c.status == 'atrasado')

    monthly_summary = {}
    for commission in commissions:
        if not commission.due_date:
            continue
        month_key = commission.due_date.strftime('%Y-%m')

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


def get_ambassador_commissions(ambassador_id: str, status: str = None,
                               month: int = None, year: int = None) -> List[Dict[str, Any]]:
    """
    Obter comissões de uma embaixadora específica no Firestore

    Args:
        ambassador_id: ID da embaixadora
        status: Status das comissões (opcional)
        month: Mês para filtrar (1–12, opcional)
        year: Ano para filtrar (opcional)

    Returns:
        Lista de comissões
    """
    db = firestore.client()

    query = db.collection('commissions').where('ambassadorId', '==', ambassador_id)

    if status:
        query = query.where('status', '==', status)

    results = []
    for doc in query.stream():
        commission = Commission(doc.to_dict())

        if commission.due_date:
            if month and year:
                if commission.due_date.month != month or commission.due_date.year != year:
                    continue
            elif year and commission.due_date.year != year:
                continue

        results.append(commission.to_dict())

    return sorted(results, key=lambda x: x.get('dueDate'))


def calculate_expected_earnings(ambassador_id: str, start_date: datetime = None,
                                end_date: datetime = None) -> Dict[str, float]:
    """
    Calcular ganhos esperados de uma embaixadora no Firestore

    Args:
        ambassador_id: ID da embaixadora
        start_date: Data inicial (opcional)
        end_date: Data final (opcional)

    Returns:
        Dicionário com totais
    """
    db = firestore.client()
    query = db.collection('commissions').where('ambassadorId', '==', ambassador_id)

    commissions = [Commission(doc.to_dict()) for doc in query.stream()]

    if start_date:
        commissions = [c for c in commissions if c.due_date and c.due_date >= start_date]
    if end_date:
        commissions = [c for c in commissions if c.due_date and c.due_date <= end_date]

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
