from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt

db = SQLAlchemy()


class User(db.Model):
    """
    Modelo de usuário do sistema
    Representa tanto embaixadoras quanto administradores
    """
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=True)  # Hash da senha
    user_type = db.Column(db.String(20), nullable=False)  # 'embaixadora' ou 'admin'
    created_at = db.Column(db.DateTime, default=datetime.now)

    # Relacionamentos
    indications = db.relationship(
        'Indication', backref='ambassador', lazy=True,
        foreign_keys='Indication.ambassador_id'
    )

    commissions = db.relationship(
        'Commission', backref='ambassador_user', lazy=True,
        foreign_keys='Commission.ambassador_id'
    )

    def __repr__(self):
        return f'<User {self.name} ({self.user_type})>'

    def to_dict(self):
        """Converter para dicionário (sem senha)"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'user_type': self.user_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def create_admin_user(cls):
        """
        Cria um usuário admin padrão se ele ainda não existir.
        email: admin@beepy.com
        senha: admin (hash bcrypt)
        """
        try:
            admin = cls.query.filter_by(email='admin@beepy.com').first()
            if not admin:
                hashed_password = bcrypt.hashpw('admin'.encode(), bcrypt.gensalt()).decode()
                admin = cls(
                    name='Admin Beepy',
                    email='admin@beepy.com',
                    password=hashed_password,
                    user_type='admin',
                    created_at=datetime.now()
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ Admin criado com sucesso")
            else:
                print("ℹ️ Admin já existe")
            return admin
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erro ao criar admin: {e}")
            return None