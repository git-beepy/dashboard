#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.user import User, db
from src.models.indication import Indication
from src.models.commission import Commission
from src.main import app
from datetime import datetime, timedelta

def create_test_data():
    with app.app_context():
        # Limpar dados existentes
        Commission.query.delete()
        Indication.query.delete()
        User.query.delete()
        db.session.commit()
        
        # Criar usuários
        admin = User(
            email='admin@beepy.com',
            name='Admin Beepy',
            user_type='admin'
        )
        
        embaixadora1 = User(
            email='mariana@teste.com',
            name='Mariana Lopes',
            user_type='embaixadora'
        )
        
        embaixadora2 = User(
            email='julia@teste.com',
            name='Julia Santos',
            user_type='embaixadora'
        )
        
        db.session.add_all([admin, embaixadora1, embaixadora2])
        db.session.commit()
        
        # Criar indicações
        indicacoes = [
            Indication(
                ambassador_id=embaixadora1.id,
                client_name='Studio Shodwe',
                client_contact='#123-456-7890',
                niche='roupa',
                observations='Cliente interessado em roupas femininas',
                status='agendado',
                created_at=datetime.now() - timedelta(days=5)
            ),
            Indication(
                ambassador_id=embaixadora1.id,
                client_name='Borcelle',
                client_contact='$ 900,50',
                niche='clinicas',
                observations='Clínica de estética',
                status='aprovado',
                sale_approval_date=datetime.now() - timedelta(days=3),
                created_at=datetime.now() - timedelta(days=4)
            ),
            Indication(
                ambassador_id=embaixadora1.id,
                client_name='Fauget',
                client_contact='$ 1.000,50',
                niche='loja de roupa',
                observations='Loja de roupas masculinas',
                status='não aprovado',
                created_at=datetime.now() - timedelta(days=3)
            ),
            Indication(
                ambassador_id=embaixadora1.id,
                client_name='Larana, Inc.',
                client_contact='$ 900,50',
                niche='oticas',
                observations='Rede de óticas',
                status='não aprovado',
                created_at=datetime.now() - timedelta(days=2)
            ),
            Indication(
                ambassador_id=embaixadora2.id,
                client_name='Ótica Vision',
                client_contact='(11) 99999-9999',
                niche='oticas',
                observations='Ótica no centro da cidade',
                status='aprovado',
                sale_approval_date=datetime.now() - timedelta(days=1),
                created_at=datetime.now() - timedelta(days=1)
            )
        ]
        
        db.session.add_all(indicacoes)
        db.session.commit()
        
        # Criar comissões para indicações aprovadas
        for indicacao in indicacoes:
            if indicacao.status == 'aprovado':
                for i in range(1, 4):
                    due_date = indicacao.sale_approval_date + timedelta(days=(i-1) * 30)
                    commission = Commission(
                        indication_id=indicacao.id,
                        ambassador_id=indicacao.ambassador_id,
                        parcel_number=i,
                        amount=300.0,
                        due_date=due_date,
                        payment_status='pago' if i == 1 else 'pendente'
                    )
                    db.session.add(commission)
        
        db.session.commit()
        print("Dados de teste criados com sucesso!")

if __name__ == '__main__':
    create_test_data()

