#!/usr/bin/env python3
import sqlite3
from datetime import datetime, timedelta
import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def create_test_data():
    # Conectar ao banco SQLite
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    # Criar tabelas se não existirem
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            user_type TEXT NOT NULL,
            password TEXT NOT NULL,
            status TEXT DEFAULT 'ativo',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS indications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ambassador_id INTEGER NOT NULL,
            client_name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            origin TEXT,
            segment TEXT,
            status TEXT DEFAULT 'pendente',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ambassador_id) REFERENCES user (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS commissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ambassador_id INTEGER NOT NULL,
            indication_id INTEGER,
            value REAL NOT NULL,
            status TEXT DEFAULT 'pendente',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ambassador_id) REFERENCES user (id),
            FOREIGN KEY (indication_id) REFERENCES indications (id)
        )
    ''')
    
    # Limpar dados existentes
    cursor.execute('DELETE FROM commissions')
    cursor.execute('DELETE FROM indications')
    cursor.execute('DELETE FROM user')
    
    # Criar usuários com bcrypt
    admin_password = hash_password('admin123')
    embaixadora_password = hash_password('embaixadora123')
    
    cursor.execute('''
        INSERT INTO user (email, name, user_type, password) VALUES
        ('admin@beepy.com', 'Admin Beepy', 'admin', ?),
        ('pietraribeiro@gmail.com', 'Pietra Ribeiro', 'embaixadora', ?),
        ('mariana@teste.com', 'Mariana Lopes', 'embaixadora', ?),
        ('julia@teste.com', 'Julia Santos', 'embaixadora', ?)
    ''', (admin_password, embaixadora_password, embaixadora_password, embaixadora_password))
    
    # Obter IDs dos usuários
    cursor.execute("SELECT id FROM user WHERE email = 'pietraribeiro@gmail.com'")
    pietra_id = cursor.fetchone()[0]
    
    cursor.execute("SELECT id FROM user WHERE email = 'mariana@teste.com'")
    mariana_id = cursor.fetchone()[0]
    
    # Criar indicações para Pietra (usuário logado)
    indicacoes_pietra = [
        (pietra_id, 'Studio Shodwe', 'studio@shodwe.com', '(11) 99999-1111', 'instagram', 'roupa', 'aprovado'),
        (pietra_id, 'Borcelle Clínica', 'contato@borcelle.com', '(11) 99999-2222', 'website', 'clinicas', 'aprovado'),
        (pietra_id, 'Fauget Store', 'vendas@fauget.com', '(11) 99999-3333', 'facebook', 'loja de roupa', 'pendente'),
        (pietra_id, 'Larana Óticas', 'info@larana.com', '(11) 99999-4444', 'indicacao', 'oticas', 'aprovado'),
        (pietra_id, 'Moda Bella', 'contato@modabella.com', '(11) 99999-5555', 'instagram', 'roupa', 'pendente'),
        (pietra_id, 'Clínica Estética Plus', 'atendimento@esteticaplus.com', '(11) 99999-6666', 'website', 'clinicas', 'aprovado'),
    ]
    
    # Criar indicações para Mariana
    indicacoes_mariana = [
        (mariana_id, 'Ótica Vision', 'contato@vision.com', '(11) 99999-7777', 'instagram', 'oticas', 'aprovado'),
        (mariana_id, 'Boutique Chic', 'vendas@boutiquechic.com', '(11) 99999-8888', 'facebook', 'roupa', 'pendente'),
    ]
    
    # Inserir indicações
    for indicacao in indicacoes_pietra + indicacoes_mariana:
        cursor.execute('''
            INSERT INTO indications (ambassador_id, client_name, email, phone, origin, segment, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', indicacao + (datetime.now() - timedelta(days=30),))
    
    # Criar comissões para indicações aprovadas
    cursor.execute("SELECT id, ambassador_id FROM indications WHERE status = 'aprovado'")
    approved_indications = cursor.fetchall()
    
    for indication_id, ambassador_id in approved_indications:
        # Criar 3 parcelas de comissão
        for i in range(3):
            value = 300.0 + (i * 50)  # Valores variados
            created_date = datetime.now() - timedelta(days=20 - (i * 5))
            cursor.execute('''
                INSERT INTO commissions (ambassador_id, indication_id, value, status, created_at)
                VALUES (?, ?, ?, 'pago', ?)
            ''', (ambassador_id, indication_id, value, created_date))
    
    # Criar algumas comissões pendentes
    for ambassador_id in [pietra_id, mariana_id]:
        for i in range(2):
            value = 250.0 + (i * 100)
            created_date = datetime.now() - timedelta(days=10 - (i * 3))
            cursor.execute('''
                INSERT INTO commissions (ambassador_id, value, status, created_at)
                VALUES (?, ?, 'pendente', ?)
            ''', (ambassador_id, value, created_date))
    
    conn.commit()
    conn.close()
    print("Dados de teste criados com sucesso no SQLite!")

if __name__ == '__main__':
    create_test_data()

