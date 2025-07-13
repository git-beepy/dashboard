from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from models.user import db

class Indication(db.Model):
    """
    Modelo de indicação feita por embaixadoras
    """
    __tablename__ = 'indication'
    
    id = db.Column(db.Integer, primary_key=True)
    ambassador_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    client_name = db.Column(db.String(100), nullable=False)
    client_contact = db.Column(db.String(100), nullable=False)
    niche = db.Column(db.String(50), nullable=False)
    observations = db.Column(db.Text)
    status = db.Column(db.String(20), default='agendado')  # agendado, aprovado, não aprovado
    sale_approval_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relacionamentos
    commissions = db.relationship('Commission', backref='indication', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Indication {self.client_name} by {self.ambassador_id}>'
    
    def to_dict(self):
        """Converter para dicionário"""
        return {
            'id': self.id,
            'ambassador_id': self.ambassador_id,
            'client_name': self.client_name,
            'client_contact': self.client_contact,
            'niche': self.niche,
            'observations': self.observations,
            'status': self.status,
            'sale_approval_date': self.sale_approval_date.isoformat() if self.sale_approval_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

