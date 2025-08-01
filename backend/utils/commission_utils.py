from datetime import datetime, timedelta
from typing import List
from models import Commission

def create_commission_parcels(indication_id: str, ambassador_id: str, ambassador_name: str, client_name: str, approval_date: datetime = None) -> List[Commission]:
    """
    Cria 3 parcelas de comissão para uma indicação aprovada.
    """
    if approval_date is None:
        approval_date = datetime.now()

    base_value = 300.00  # Valor da comissão dividido em 3 parcelas
    parcels = []

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

        commission = Commission(commission_data)
        parcels.append(commission)

    # Retornar lista de dicionários para persistência
    return [p.to_dict() for p in parcels]
