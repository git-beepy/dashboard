from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from models.user import db

class Commission(db.Model):
    """
    Modelo de comissão gerada por vendas aprovadas
    """
    __tablename__ = 'commission'
    
    id = db.Column(db.Integer, primary_key=True)
    indication_id = db.Column(db.Integer, db.ForeignKey('indication.id'), nullable=False)
    ambassador_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parcel_number = db.Column(db.Integer, nullable=False)  # 1, 2 ou 3
    amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    payment_status = db.Column(db.String(20), default='pendente')  # pendente, pago
    payment_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<Commission {self.parcel_number}/3 - R${self.amount}>'
    
    def to_dict(self):
        """Converter para dicionário"""
        return {
            'id': self.id,
            'indication_id': self.indication_id,
            'ambassador_id': self.ambassador_id,
            'parcel_number': self.parcel_number,
            'amount': self.amount,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'payment_status': self.payment_status,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

