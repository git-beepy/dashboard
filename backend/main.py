import os
import json
import bcrypt
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from google.cloud import firestore
from utils import serialize_firestore_data, safe_jsonify

# Configurações
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-secret-key-change-in-production")

# Inicializar Firebase
try:
    # Tentar usar credenciais do ambiente primeiro
    if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        # Se for string JSON, criar arquivo temporário
        creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if isinstance(creds, str) and creds.startswith("{"):
            import tempfile
            import json as json_module

            # Validar se é JSON válido
            try:
                json_module.loads(creds)
                # Criar arquivo temporário
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    f.write(creds)
                    temp_file = f.name
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_file
                print("Credenciais Firebase configuradas via variável de ambiente")
            except json_module.JSONDecodeError:
                print("Erro: GOOGLE_APPLICATION_CREDENTIALS não é um JSON válido")

    db = firestore.Client()
    print("Firebase conectado com sucesso!")
except Exception as e:
    print(f"Erro ao conectar Firebase: {e}")
    # Tentar usar arquivo local como fallback
    try:
        local_creds_path = "projeto-beepy-firebase-adminsdk-fbsvc-45c41daaaf.json"
        if os.path.exists(local_creds_path):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = local_creds_path
            db = firestore.Client()
            print("Firebase conectado com arquivo local!")
        else:
            print("Arquivo de credenciais local não encontrado")
            db = None
    except Exception as e2:
        print(f"Erro ao conectar Firebase com arquivo local: {e2}")
        db = None

# Criar aplicação Flask
app = Flask(__name__)

# Configurações do Flask
app.config["SECRET_KEY"] = SECRET_KEY
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)

# Inicializar JWT
jwt = JWTManager(app)

# Configurar CORS para lidar com credenciais
CORS(app,
     supports_credentials=True,
     origins=["https://dashboard-fy7kd0d9-git-beepyjs-projects.vercel.app",
              "https://dashboard-lcgemgzdf-git-beepyjs-projects.vercel.app",
              "https://dashboard-two-murex-93kzyvrvas.vercel.app", "http://localhost:3000", "http://localhost:5173"],
     allow_headers=["Content-Type", "Authorization", "Accept"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])


# Middleware para logs de debug e tratamento de CORS específico
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = app.make_default_options_response()
        headers = response.headers

        # Obter origem da requisição
        origin = request.headers.get('Origin')
        allowed_origins = [
            "https://dashboard-two-murex-93kzyvrvas.vercel.app",
            "http://localhost:3000",
            "http://localhost:5173"
        ]

        if origin in allowed_origins:
            headers['Access-Control-Allow-Origin'] = origin
        else:
            headers['Access-Control-Allow-Origin'] = allowed_origins[0]  # Default para produção

        headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept'
        headers['Access-Control-Allow-Credentials'] = 'true'
        return response

    print(f"Request: {request.method} {request.url}")
    print(f"Origin: {request.headers.get('Origin', 'No Origin')}")
    print(f"Headers: {dict(request.headers)}")
    if request.get_json(silent=True):
        print(f"Body: {request.get_json()}")


@app.after_request
def after_request(response):
    # Obter origem da requisição
    origin = request.headers.get('Origin')
    allowed_origins = [
        "https://dashboard-two-murex-93kzyvrvas.vercel.app",
        "http://localhost:3000",
        "http://localhost:5173"
    ]

    if origin in allowed_origins:
        response.headers['Access-Control-Allow-Origin'] = origin
    else:
        response.headers['Access-Control-Allow-Origin'] = allowed_origins[0]  # Default para produção

    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response


# Rotas de autenticação
@app.route("/api/auth/login", methods=["POST"])
def login():
    try:
        # Verificar se há dados JSON
        if not request.is_json:
            return safe_jsonify({"error": "Content-Type deve ser application/json"}, 400)

        data = request.get_json()
        if not data:
            return safe_jsonify({"error": "Dados não fornecidos"}, 400)

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return safe_jsonify({"error": "Email e senha são obrigatórios"}, 400)

        print(f"Tentativa de login para: {email}")

        if not db:
            return safe_jsonify({"error": "Erro de conexão com banco de dados"}, 500)

        # Buscar usuário no Firestore
        users_ref = db.collection("users")
        query = users_ref.where(field_path="email", op_string="==", value=email).limit(1)
        docs = list(query.stream())

        if not docs:
            print(f"Usuário não encontrado: {email}")
            return safe_jsonify({"error": "Usuário não encontrado"}, 401)

        user_doc = docs[0]
        user_data = user_doc.to_dict()
        print(f"Usuário encontrado: {user_data.get('email')}")

        # Verificar senha
        stored_password = user_data.get("password", "")
        if not stored_password:
            print("Senha não encontrada no usuário")
            return safe_jsonify({"error": "Dados de usuário inválidos"}, 500)

        try:
            # Verificar se a senha está em hash bcrypt
            if bcrypt.checkpw(password.encode("utf-8"), stored_password.encode("utf-8")):
                print("Senha verificada com sucesso")

                # Criar token JWT
                access_token = create_access_token(
                    identity=user_doc.id,
                    additional_claims={
                        "email": user_data["email"],
                        "role": user_data["role"]
                    }
                )

                response_data = {
                    "access_token": access_token,
                    "user": {
                        "id": user_doc.id,
                        "email": user_data["email"],
                        "role": user_data["role"],
                        "name": user_data.get("name", "")
                    }
                }

                print(f"Login bem-sucedido para: {email}")
                return safe_jsonify(response_data, 200)
            else:
                print("Senha incorreta")
                return safe_jsonify({"error": "Senha incorreta"}, 401)

        except Exception as e:
            print(f"Erro ao verificar senha: {e}")
            # Tentar comparação direta (para senhas não hasheadas)
            if password == stored_password:
                print("Senha verificada (comparação direta)")

                access_token = create_access_token(
                    identity=user_doc.id,
                    additional_claims={
                        "email": user_data["email"],
                        "role": user_data["role"]
                    }
                )

                response_data = {
                    "access_token": access_token,
                    "user": {
                        "id": user_doc.id,
                        "email": user_data["email"],
                        "role": user_data["role"],
                        "name": user_data.get("name", "")
                    }
                }

                return safe_jsonify(response_data, 200)
            else:
                return safe_jsonify({"error": "Senha incorreta"}, 401)

    except Exception as e:
        print(f"Erro no login: {str(e)}")
        return safe_jsonify({"error": f"Erro interno: {str(e)}"}, 500)


# Rota para verificar token
@app.route("/api/auth/verify", methods=["GET"])
@jwt_required()
def verify_token():
    try:
        current_user_id = get_jwt_identity()
        if not db:
            return safe_jsonify({"error": "Erro de conexão com banco de dados"}, 500)

        user_doc = db.collection("users").document(current_user_id).get()

        if not user_doc.exists:
            return safe_jsonify({"error": "Usuário não encontrado"}, 404)

        user_data = user_doc.to_dict()
        response_data = {
            "user": {
                "id": user_doc.id,
                "email": user_data["email"],
                "role": user_data["role"],
                "name": user_data.get("name", "")
            }
        }

        return safe_jsonify(response_data, 200)

    except Exception as e:
        print(f"Erro na verificação do token: {str(e)}")
        return safe_jsonify({"error": str(e)}, 500)


# Rotas de indicações
@app.route("/api/indications", methods=["GET"])
@jwt_required()
def get_indications():
    try:
        if not db:
            return safe_jsonify({"error": "Erro de conexão com banco de dados"}, 500)

        current_user_id = get_jwt_identity()
        user_doc = db.collection("users").document(current_user_id).get()

        if not user_doc.exists:
            return safe_jsonify({"error": "Usuário não encontrado"}, 404)

        user_data = user_doc.to_dict()

        # Se for admin, retorna todas as indicações
        if user_data["role"] == "admin":
            indications_ref = db.collection("indications")
        else:
            # Se for embaixadora, retorna apenas suas indicações
            indications_ref = db.collection("indications").where(field_path="ambassadorId", op_string="==",
                                                                 value=current_user_id)

        docs = indications_ref.stream()
        indications = []

        for doc in docs:
            indication_data = doc.to_dict()
            indication_data["id"] = doc.id
            indication_data = serialize_firestore_data(indication_data)
            indications.append(indication_data)

        return safe_jsonify(indications, 200)

    except Exception as e:
        print(f"Erro ao buscar indicações: {str(e)}")
        return safe_jsonify({"error": str(e)}, 500)


@app.route("/api/indications", methods=["POST"])
@jwt_required()
def create_indication():
    try:
        if not db:
            return safe_jsonify({"error": "Erro de conexão com banco de dados"}, 500)

        current_user_id = get_jwt_identity()
        data = request.get_json()

        if not data:
            return safe_jsonify({"error": "Dados não fornecidos"}, 400)

        # Validar campos obrigatórios - aceitar ambos os formatos
        client_name = data.get("clientName") or data.get("client_name")
        client_email = data.get("clientEmail") or data.get("email")
        client_phone = data.get("clientPhone") or data.get("phone")

        if not client_name or not client_email or not client_phone:
            return safe_jsonify({"error": "Nome, email e telefone do cliente são obrigatórios"}, 400)

        indication_data = {
            "ambassadorId": current_user_id,
            "clientName": client_name,
            "clientEmail": client_email,
            "clientPhone": client_phone,
            "origin": data.get("origin", "website"),
            "segment": data.get("segment", "geral"),
            "converted": False,
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }

        doc_ref = db.collection("indications").add(indication_data)
        indication_data["id"] = doc_ref[1].id
        indication_data = serialize_firestore_data(indication_data)

        print(f"Indicação criada com sucesso: {indication_data['id']}")
        return safe_jsonify(indication_data, 201)

    except Exception as e:
        print(f"Erro ao criar indicação: {str(e)}")
        return safe_jsonify({"error": str(e)}, 500)


@app.route("/api/indications/<indication_id>", methods=["PUT"])
@jwt_required()
def update_indication(indication_id):
    try:
        if not db:
            return safe_jsonify({"error": "Erro de conexão com banco de dados"}, 500)

        data = request.get_json()
        update_data = {"updatedAt": datetime.now()}

        for field in ["converted", "clientName", "clientEmail", "clientPhone", "origin", "segment"]:
            if field in data:
                update_data[field] = data[field]

        db.collection("indications").document(indication_id).update(update_data)
        return safe_jsonify({"message": "Indicação atualizada com sucesso"}, 200)

    except Exception as e:
        print(f"Erro ao atualizar indicação: {str(e)}")
        return safe_jsonify({"error": str(e)}, 500)


@app.route("/api/indications/<indication_id>", methods=["DELETE"])
@jwt_required()
def delete_indication(indication_id):
    try:
        if not db:
            return safe_jsonify({"error": "Erro de conexão com banco de dados"}, 500)

        db.collection("indications").document(indication_id).delete()
        return safe_jsonify({"message": "Indicação excluída com sucesso"}, 200)
    except Exception as e:
        print(f"Erro ao excluir indicação: {str(e)}")
        return safe_jsonify({"error": str(e)}, 500)


# Rotas de usuários (apenas admin)
@app.route("/api/users", methods=["GET"])
@jwt_required()
def get_users():
    try:
        if not db:
            return safe_jsonify({"error": "Erro de conexão com banco de dados"}, 500)

        current_user_id = get_jwt_identity()
        user_doc = db.collection("users").document(current_user_id).get()

        if not user_doc.exists:
            return safe_jsonify({"error": "Usuário não encontrado"}, 404)

        user_data = user_doc.to_dict()
        if user_data["role"] != "admin":
            return safe_jsonify({"error": "Acesso negado"}, 403)

        users_ref = db.collection("users")
        docs = users_ref.stream()
        users = []

        for doc in docs:
            user_data = doc.to_dict()
            user_data["id"] = doc.id
            del user_data["password"]  # Não retornar senha
            user_data = serialize_firestore_data(user_data)
            users.append(user_data)

        return safe_jsonify(users, 200)

    except Exception as e:
        print(f"Erro ao buscar usuários: {str(e)}")
        return safe_jsonify({"error": str(e)}, 500)


@app.route("/api/users", methods=["POST"])
@jwt_required()
def create_user():
    try:
        if not db:
            return safe_jsonify({"error": "Erro de conexão com banco de dados"}, 500)

        current_user_id = get_jwt_identity()
        user_doc = db.collection("users").document(current_user_id).get()

        if not user_doc.exists:
            return safe_jsonify({"error": "Usuário não encontrado"}, 404)

        user_data = user_doc.to_dict()
        if user_data["role"] != "admin":
            return safe_jsonify({"error": "Acesso negado"}, 403)

        data = request.get_json()

        # Verificar se email já existe
        query = db.collection("users").where(field_path="email", op_string="==", value=data.get("email")).limit(1)
        existing_users = list(query.stream())

        if existing_users:
            return safe_jsonify({"error": "Email já está em uso"}, 400)

        # Criar hash da senha
        hashed_password = bcrypt.hashpw(data.get("password").encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        new_user_data = {
            "email": data.get("email"),
            "password": hashed_password,
            "name": data.get("name"),
            "role": data.get("role"),
            "phone": data.get("phone", ""),
            "createdAt": datetime.now(),
            "lastActiveAt": datetime.now()
        }

        doc_ref = db.collection("users").add(new_user_data)
        new_user_data["id"] = doc_ref[1].id
        del new_user_data["password"]
        new_user_data = serialize_firestore_data(new_user_data)

        return safe_jsonify(new_user_data, 201)

    except Exception as e:
        print(f"Erro ao criar usuário: {str(e)}")
        return safe_jsonify({"error": str(e)}, 500)


# Rotas de comissões
@app.route("/api/commissions", methods=["GET"])
@jwt_required()
def get_commissions():
    try:
        if not db:
            return safe_jsonify({"error": "Erro de conexão com banco de dados"}, 500)

        current_user_id = get_jwt_identity()
        user_doc = db.collection("users").document(current_user_id).get()

        if not user_doc.exists:
            return safe_jsonify({"error": "Usuário não encontrado"}, 404)

        user_data = user_doc.to_dict()

        if user_data["role"] == "admin":
            commissions_ref = db.collection("commissions")
        else:
            commissions_ref = db.collection("commissions").where(field_path="ambassadorId", op_string="==",
                                                                 value=current_user_id)

        docs = commissions_ref.stream()
        commissions = []

        for doc in docs:
            commission_data = doc.to_dict()
            commission_data["id"] = doc.id
            commission_data = serialize_firestore_data(commission_data)
            commissions.append(commission_data)

        return safe_jsonify(commissions, 200)

    except Exception as e:
        print(f"Erro ao buscar comissões: {str(e)}")
        return safe_jsonify({"error": str(e)}, 500)


@app.route("/api/commissions", methods=["POST"])
@jwt_required()
def create_commission():
    try:
        if not db:
            return safe_jsonify({"error": "Erro de conexão com banco de dados"}, 500)

        data = request.get_json()

        commission_data = {
            "ambassadorId": data.get("ambassadorId"),
            "indicationId": data.get("indicationId"),
            "value": data.get("value"),
            "status": data.get("status", "pending"),
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }

        doc_ref = db.collection("commissions").add(commission_data)
        commission_data["id"] = doc_ref[1].id
        commission_data = serialize_firestore_data(commission_data)

        return safe_jsonify(commission_data, 201)

    except Exception as e:
        print(f"Erro ao criar comissão: {str(e)}")
        return safe_jsonify({"error": str(e)}, 500)


# Rotas de dashboard
@app.route("/api/dashboard/admin", methods=["GET"])
@jwt_required()
def get_admin_dashboard():
    try:
        if not db:
            return safe_jsonify({"error": "Erro de conexão com banco de dados"}, 500)

        current_user_id = get_jwt_identity()
        user_doc = db.collection("users").document(current_user_id).get()

        if not user_doc.exists:
            return safe_jsonify({"error": "Usuário não encontrado"}, 404)

        user_data = user_doc.to_dict()
        if user_data["role"] != "admin":
            return safe_jsonify({"error": "Acesso negado"}, 403)

        dashboard_data = {}

        # Estatísticas básicas
        users_count = len(list(db.collection("users").stream()))
        indications_count = len(list(db.collection("indications").stream()))
        commissions_count = len(list(db.collection("commissions").stream()))

        # Calcular comissões do mês
        current_month = datetime.now().month
        current_year = datetime.now().year

        commissions_ref = db.collection("commissions")
        all_commissions = list(commissions_ref.stream())

        monthly_commissions = 0
        for commission_doc in all_commissions:
            commission_data = commission_doc.to_dict()
            created_at = commission_data.get("createdAt")
            if created_at and created_at.month == current_month and created_at.year == current_year:
                monthly_commissions += commission_data.get("value", 0)

        dashboard_data["stats"] = {
            "totalUsers": users_count,
            "totalIndications": indications_count,
            "totalCommissions": commissions_count,
            "monthlyCommissions": monthly_commissions,
            "activeAmbassadors": users_count - 1  # Excluir admin
        }

        dashboard_data = serialize_firestore_data(dashboard_data)
        return safe_jsonify(dashboard_data, 200)

    except Exception as e:
        print(f"Erro no dashboard admin: {str(e)}")
        return safe_jsonify({"error": str(e)}, 500)


@app.route("/api/dashboard/ambassador", methods=["GET"])
@jwt_required()
def get_ambassador_dashboard():
    try:
        if not db:
            return safe_jsonify({"error": "Erro de conexão com banco de dados"}, 500)

        current_user_id = get_jwt_identity()
        user_doc = db.collection("users").document(current_user_id).get()

        if not user_doc.exists:
            return safe_jsonify({"error": "Usuário não encontrado"}, 404)

        user_data = user_doc.to_dict()
        if user_data["role"] != "embaixadora":
            return safe_jsonify({"error": "Acesso negado"}, 403)

        dashboard_data = {}

        # Indicações da embaixadora
        indications_ref = db.collection("indications").where(field_path="ambassadorId", op_string="==",
                                                             value=current_user_id)
        indications = list(indications_ref.stream())

        total_indications = len(indications)
        converted_indications = sum(1 for doc in indications if doc.to_dict().get("converted", False))

        # Comissões da embaixadora
        commissions_ref = db.collection("commissions").where(field_path="ambassadorId", op_string="==",
                                                             value=current_user_id)
        commissions = list(commissions_ref.stream())

        total_commissions = sum(doc.to_dict().get("value", 0) for doc in commissions)

        dashboard_data["stats"] = {
            "totalIndications": total_indications,
            "convertedIndications": converted_indications,
            "conversionRate": (converted_indications / total_indications * 100) if total_indications > 0 else 0,
            "totalCommissions": total_commissions
        }

        dashboard_data = serialize_firestore_data(dashboard_data)
        return safe_jsonify(dashboard_data, 200)

    except Exception as e:
        print(f"Erro no dashboard embaixadora: {str(e)}")
        return safe_jsonify({"error": str(e)}, 500)


# Rota para criar usuário admin inicial
@app.route("/api/setup", methods=["POST"])
def setup_admin():
    try:
        if not db:
            return safe_jsonify({"error": "Erro de conexão com banco de dados"}, 500)

        # Verificar se já existe um admin
        users_ref = db.collection("users").where(field_path="role", op_string="==", value="admin").limit(1)
        docs = list(users_ref.stream())

        if docs:
            return safe_jsonify({"message": "Admin já existe"}, 200)

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

        db.collection("users").add(admin_data)
        print("Usuário admin criado com sucesso!")
        return safe_jsonify({"message": "Usuário admin criado com sucesso"}, 201)

    except Exception as e:
        print(f"Erro ao criar admin: {str(e)}")
        return safe_jsonify({"error": str(e)}, 500)


@app.route("/")
def home():
    return safe_jsonify({
        "message": "Beepy API - Sistema de Indicações e Comissões",
        "version": "3.2",
        "status": "online",
        "cors_configured": True,
        "gunicorn_compatible": True,
        "endpoints": [
            "/api/auth/login",
            "/api/auth/verify",
            "/api/indications",
            "/api/commissions",
            "/api/users",
            "/api/dashboard/admin",
            "/api/dashboard/ambassador",
            "/api/setup",
            "/health"
        ]
    })


@app.route("/health")
def health():
    return safe_jsonify({
        "status": "healthy",
        "service": "beepy-api",
        "firebase_connected": db is not None,
        "cors_configured": True,
        "gunicorn_compatible": True
    })


# Para desenvolvimento local
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)



