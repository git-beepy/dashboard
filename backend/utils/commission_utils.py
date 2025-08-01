from datetime import datetime, timedelta
from typing import List, Dict, Any
from firebase_admin import firestore
from models.commission import Commission


def create_commission_parcels(indication_id: str, ambassador_id: str, ambassador_name: str, client_name: str,
                              approval_date: datetime = None) -> List[Dict[str, Any]]:
    """
    Criar e retornar 3 parcelas de comissão (sem salvar ainda)
    """
    if approval_date is None:
        approval_date = datetime.now()

    base_value = 300.00
    commissions = []

    for i in range(3):
        due_date = approval_date + timedelta(days=30 * (i + 1))

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

        commissions.append(commission_data)

    return commissions


def save_commission_parcels(commissions: List[Dict[str, Any]]) -> None:
    """
    Salva uma lista de parcelas de comissão no Firestore usando batch
    """
    db = firestore.client()
    batch = db.batch()

    for commission_data in commissions:
        doc_ref = db.collection('commissions').document()
        batch.set(doc_ref, commission_data)

    batch.commit()


def update_overdue_commissions() -> int:
    """
    Atualiza comissões vencidas no Firestore (status: 'atrasado')
    """
    db = firestore.client()
    today = datetime.today()

    pending_commissions = db.collection('commissions') \
        .where('status', '==', 'pendente') \
        .where('dueDate', '<', today).stream()

    batch = db.batch()
    count = 0

    for doc in pending_commissions:
        batch.update(doc.reference, {
            'status': 'atrasado',
            'updatedAt': datetime.now()
        })
        count += 1

    if count > 0:
        batch.commit()

    return count


def get_commission_summary(ambassador_id: str = None) -> Dict[str, Any]:
    """
    Obter resumo das comissões de uma embaixadora (Firestore)
    """
    db = firestore.client()
    query = db.collection('commissions')
    if ambassador_id:
        query = query.where('ambassadorId', '==', ambassador_id)

    commissions = [Commission(doc.to_dict()) for doc in query.stream()]

    total = sum(c.value for c in commissions)
    paid = sum(c.value for c in commissions if c.status == 'pago')
    pending = sum(c.value for c in commissions if c.status == 'pendente')
    overdue = sum(c.value for c in commissions if c.status == 'atrasado')

    monthly = {}
    for c in commissions:
        if not c.due_date:
            continue
        key = c.due_date.strftime('%Y-%m')
        if key not in monthly:
            monthly[key] = {'month': key, 'total': 0, 'paid': 0, 'pending': 0, 'overdue': 0}

        monthly[key]['total'] += c.value
        if c.status == 'pago':
            monthly[key]['paid'] += c.value
        elif c.status == 'pendente':
            monthly[key]['pending'] += c.value
        elif c.status == 'atrasado':
            monthly[key]['overdue'] += c.value

    return {
        'total_amount': total,
        'paid_amount': paid,
        'pending_amount': pending,
        'overdue_amount': overdue,
        'total_commissions': len(commissions),
        'paid_commissions': len([c for c in commissions if c.status == 'pago']),
        'pending_commissions': len([c for c in commissions if c.status == 'pendente']),
        'overdue_commissions': len([c for c in commissions if c.status == 'atrasado']),
        'monthly_breakdown': list(monthly.values())
    }


def get_ambassador_commissions(ambassador_id: str, status: str = None, month: int = None, year: int = None) -> List[Dict[str, Any]]:
    """
    Obter comissões de uma embaixadora com filtros opcionais
    """
    db = firestore.client()
    query = db.collection('commissions').where('ambassadorId', '==', ambassador_id)
    if status:
        query = query.where('status', '==', status)

    results = []
    for doc in query.stream():
        data = doc.to_dict()
        commission = Commission(data)
        if commission.due_date:
            if month and year:
                if commission.due_date.month != month or commission.due_date.year != year:
                    continue
            elif year and commission.due_date.year != year:
                continue
        results.append(commission.to_dict())

    return sorted(results, key=lambda x: x.get('dueDate'))


def calculate_expected_earnings(ambassador_id: str, start_date: datetime = None, end_date: datetime = None) -> Dict[str, float]:
    """
    Calcular ganhos esperados de uma embaixadora
    """
    db = firestore.client()
    query = db.collection('commissions').where('ambassadorId', '==', ambassador_id)

    commissions = [Commission(doc.to_dict()) for doc in query.stream()]
    if start_date:
        commissions = [c for c in commissions if c.due_date and c.due_date >= start_date]
    if end_date:
        commissions = [c for c in commissions if c.due_date and c.due_date <= end_date]

    total = sum(c.value for c in commissions)
    paid = sum(c.value for c in commissions if c.status == 'pago')
    pending = sum(c.value for c in commissions if c.status == 'pendente')
    overdue = sum(c.value for c in commissions if c.status == 'atrasado')

    return {
        'total_expected': total,
        'total_paid': paid,
        'total_pending': pending,
        'total_overdue': overdue,
        'payment_percentage': (paid / total * 100) if total > 0 else 0
    }
