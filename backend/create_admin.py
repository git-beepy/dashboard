import firebase_admin
from firebase_admin import credentials, firestore
import bcrypt
from datetime import datetime

# Inicializar Firebase
cred = credentials.Certificate('projeto-beepy-firebase-adminsdk-fbsvc-45c41daaaf.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Deletar usuários admin existentes
users_ref = db.collection('users')
query = users_ref.where(field_path='role', op_string='==', value='admin')
docs = list(query.stream())

for doc in docs:
    doc.reference.delete()
    print(f"Usuário admin {doc.id} deletado")

# Criar novo usuário admin
hashed_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

admin_data = {
    'email': 'admin@beepy.com',
    'password': hashed_password,
    'role': 'admin',
    'name': 'Administrador',
    'createdAt': datetime.now(),
    'lastActiveAt': datetime.now()
}

doc_ref = db.collection('users').add(admin_data)
print(f"Usuário admin criado com ID: {doc_ref[1].id}")
print(f"Hash da senha: {hashed_password}")

