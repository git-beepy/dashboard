from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from models.user import db

class Indication(db.Model):
    """
    Modelo de indicação feita por embaixadoras - Versão atualizada
    """
    __tablename__ = 'indication'
    
    id = db.Column(db.Integer, primary_key=True)
    ambassador_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    client_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    origin = db.Column(db.String(50), nullable=False, default='website')
    segment = db.Column(db.String(100), nullable=False, default='outros')
    status = db.Column(db.String(20), default='agendado')  # agendado, aprovado, não aprovado
    converted = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    sale_approval_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Campos antigos para compatibilidade (podem ser removidos após migração)
    client_contact = db.Column(db.String(100))  # Mapeado para email
    niche = db.Column(db.String(50))  # Mapeado para segment
    observations = db.Column(db.Text)  # Mapeado para notes
    
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
            'email': self.email,
            'phone': self.phone,
            'origin': self.origin,
            'segment': self.segment,
            'status': self.status,
            'converted': self.converted,
            'notes': self.notes,
            'sale_approval_date': self.sale_approval_date.isoformat() if self.sale_approval_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            # Campos de compatibilidade
            'client_contact': self.email,  # Para compatibilidade
            'niche': self.segment,  # Para compatibilidade
            'observations': self.notes  # Para compatibilidade
        }

