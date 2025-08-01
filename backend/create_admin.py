#!/usr/bin/env python3
"""
Script para criar usuário administrador inicial
"""

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import bcrypt


def create_admin_user():
    try:
        # Inicializar Firebase
        if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
            cred_json = json.loads(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))
            cred = credentials.Certificate(cred_json)
        else:
            cred = credentials.Certificate("projeto-beepy-firebase-adminsdk-fbsvc-45c41daaaf.json")
        
        firebase_admin.initialize_app(cred)
        db = firestore.client()

        # Verificar se já existe um admin
        users_ref = db.collection("users").where(field_path="role", op_string="==", value="admin").limit(1)
        docs = list(users_ref.stream())

        if docs:
            print("Usuário admin já existe!")
            return

        # Criar usuário admin
        hashed_password = bcrypt.hashpw("admin123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        admin_data = {
            "email": "admin@beepy.com",
            "password": hashed_password,
            "role": "admin",
            "name": "Administrador",
            "createdAt": datetime.now(),
            "lastActiveAt": datetime.now()
        }

        doc_ref = db.collection("users").add(admin_data)
        print(f"Usuário admin criado com sucesso! ID: {doc_ref[1].id}")
        print("Email: admin@beepy.com")
        print("Senha: admin123")

    except Exception as e:
        print(f"Erro ao criar admin: {e}")


if __name__ == "__main__":
    create_admin_user()

