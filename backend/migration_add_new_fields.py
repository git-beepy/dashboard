"""
Script de migração para adicionar novos campos ao modelo Indication
Execute este script para atualizar o banco de dados existente
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Configuração básica do Flask para migração
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///beepy.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def run_migration():
    """
    Executa a migração para adicionar os novos campos
    """
    with app.app_context():
        try:
            # Adicionar novos campos à tabela indication
            db.engine.execute("""
                ALTER TABLE indication 
                ADD COLUMN email VARCHAR(100);
            """)
            print("✓ Campo 'email' adicionado")
        except Exception as e:
            print(f"Campo 'email' já existe ou erro: {e}")
        
        try:
            db.engine.execute("""
                ALTER TABLE indication 
                ADD COLUMN phone VARCHAR(20);
            """)
            print("✓ Campo 'phone' adicionado")
        except Exception as e:
            print(f"Campo 'phone' já existe ou erro: {e}")
        
        try:
            db.engine.execute("""
                ALTER TABLE indication 
                ADD COLUMN origin VARCHAR(50) DEFAULT 'website';
            """)
            print("✓ Campo 'origin' adicionado")
        except Exception as e:
            print(f"Campo 'origin' já existe ou erro: {e}")
        
        try:
            db.engine.execute("""
                ALTER TABLE indication 
                ADD COLUMN segment VARCHAR(100) DEFAULT 'outros';
            """)
            print("✓ Campo 'segment' adicionado")
        except Exception as e:
            print(f"Campo 'segment' já existe ou erro: {e}")
        
        try:
            db.engine.execute("""
                ALTER TABLE indication 
                ADD COLUMN converted BOOLEAN DEFAULT 0;
            """)
            print("✓ Campo 'converted' adicionado")
        except Exception as e:
            print(f"Campo 'converted' já existe ou erro: {e}")
        
        try:
            db.engine.execute("""
                ALTER TABLE indication 
                ADD COLUMN notes TEXT;
            """)
            print("✓ Campo 'notes' adicionado")
        except Exception as e:
            print(f"Campo 'notes' já existe ou erro: {e}")
        
        try:
            db.engine.execute("""
                ALTER TABLE indication 
                ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP;
            """)
            print("✓ Campo 'updated_at' adicionado")
        except Exception as e:
            print(f"Campo 'updated_at' já existe ou erro: {e}")
        
        # Migrar dados existentes
        try:
            # Copiar client_contact para email (se não estiver vazio)
            db.engine.execute("""
                UPDATE indication 
                SET email = client_contact 
                WHERE client_contact IS NOT NULL AND client_contact != '' AND email IS NULL;
            """)
            print("✓ Dados migrados: client_contact -> email")
        except Exception as e:
            print(f"Erro ao migrar client_contact: {e}")
        
        try:
            # Copiar niche para segment (se não estiver vazio)
            db.engine.execute("""
                UPDATE indication 
                SET segment = niche 
                WHERE niche IS NOT NULL AND niche != '' AND segment = 'outros';
            """)
            print("✓ Dados migrados: niche -> segment")
        except Exception as e:
            print(f"Erro ao migrar niche: {e}")
        
        try:
            # Copiar observations para notes (se não estiver vazio)
            db.engine.execute("""
                UPDATE indication 
                SET notes = observations 
                WHERE observations IS NOT NULL AND observations != '' AND notes IS NULL;
            """)
            print("✓ Dados migrados: observations -> notes")
        except Exception as e:
            print(f"Erro ao migrar observations: {e}")
        
        print("\n🎉 Migração concluída com sucesso!")
        print("\nPróximos passos:")
        print("1. Teste a aplicação para verificar se tudo está funcionando")
        print("2. Após confirmar que está tudo ok, você pode remover os campos antigos:")
        print("   - client_contact")
        print("   - niche") 
        print("   - observations")

if __name__ == '__main__':
    print("🔄 Iniciando migração do banco de dados...")
    run_migration()

