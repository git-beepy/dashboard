#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import app, db
from models.user import User
from models.indication import Indication
from models.commission import Commission
from datetime import datetime, timedelta

def create_test_data():
    with app.app_context():
        # Limpar dados existentes (Firestore)
        # Para limpar coleções no Firestore, é necessário iterar e deletar documentos
        # Isso pode ser custoso para grandes volumes de dados. Para teste, faremos de forma simples.
        for doc in db.collection("commissions").stream():
            doc.reference.delete()
        for doc in db.collection("indications").stream():
            doc.reference.delete()
        for doc in db.collection("users").stream():
            doc.reference.delete()
        
        # Criar usuários (Firestore)
        admin_data = {
            'email': 'admin@beepy.com',
            'name': 'Admin Beepy',
            'user_type': 'admin',
            'password': 'admin123' # Senha em texto puro para facilitar o teste, em produção deve ser hash
        }
        admin_ref = db.collection("users").add(admin_data)
        admin_id = admin_ref[1].id

        embaixadora1_data = {
            'email': 'mariana@teste.com',
            'name': 'Mariana Lopes',
            'user_type': 'embaixadora',
            'password': 'password123'
        }
        embaixadora1_ref = db.collection("users").add(embaixadora1_data)
        embaixadora1_id = embaixadora1_ref[1].id
        
        embaixadora2_data = {
            'email': 'julia@teste.com',
            'name': 'Julia Santos',
            'user_type': 'embaixadora',
            'password': 'password123'
        }
        embaixadora2_ref = db.collection("users").add(embaixadora2_data)
        embaixadora2_id = embaixadora2_ref[1].id
        
        # Criar indicações (Firestore)
        indicacoes_data = [
            {
                'ambassadorId': embaixadora1_id,
                'clientName': 'Studio Shodwe',
                'clientContact': '#123-456-7890',
                'niche': 'roupa',
                'observations': 'Cliente interessado em roupas femininas',
                'status': 'agendado',
                'createdAt': datetime.now() - timedelta(days=5),
                'converted': False
            },
            {
                'ambassadorId': embaixadora1_id,
                'clientName': 'Borcelle',
                'clientContact': '$ 900,50',
                'niche': 'clinicas',
                'observations': 'Clínica de estética',
                'status': 'aprovado',
                'saleApprovalDate': datetime.now() - timedelta(days=3),
                'createdAt': datetime.now() - timedelta(days=4),
                'converted': True
            },
            {
                'ambassadorId': embaixadora1_id,
                'clientName': 'Fauget',
                'clientContact': '$ 1.000,50',
                'niche': 'loja de roupa',
                'observations': 'Loja de roupas masculinas',
                'status': 'não aprovado',
                'createdAt': datetime.now() - timedelta(days=3),
                'converted': False
            },
            {
                'ambassadorId': embaixadora1_id,
                'clientName': 'Larana, Inc.',
                'clientContact': '$ 900,50',
                'niche': 'oticas',
                'observations': 'Rede de óticas',
                'status': 'não aprovado',
                'createdAt': datetime.now() - timedelta(days=2),
                'converted': False
            },
            {
                'ambassadorId': embaixadora2_id,
                'clientName': 'Ótica Vision',
                'clientContact': '(11) 99999-9999',
                'niche': 'oticas',
                'observations': 'Ótica no centro da cidade',
                'status': 'aprovado',
                'saleApprovalDate': datetime.now() - timedelta(days=1),
                'createdAt': datetime.now() - timedelta(days=1),
                'converted': True
            }
        ]
        
        indication_ids = []
        for ind_data in indicacoes_data:
            ind_ref = db.collection("indications").add(ind_data)
            indication_ids.append((ind_ref[1].id, ind_data))
        
        # Criar comissões para indicações aprovadas (Firestore)
        for ind_id, ind_data in indication_ids:
            if ind_data['status'] == 'aprovado':
                for i in range(1, 4):
                    due_date = ind_data['saleApprovalDate'] + timedelta(days=(i-1) * 30)
                    commission_data = {
                        'indicationId': ind_id,
                        'ambassadorId': ind_data['ambassadorId'],
                        'parcelNumber': i,
                        'amount': 300.0,
                        'dueDate': due_date,
                        'paymentStatus': 'pago' if i == 1 else 'pendente'
                    }
                    db.collection("commissions").add(commission_data)
        
        print("Dados de teste criados com sucesso!")

if __name__ == '__main__':
    create_test_data()

