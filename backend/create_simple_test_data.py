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