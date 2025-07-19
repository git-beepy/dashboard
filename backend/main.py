import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import bcrypt
from utils import CustomJSONEncoder, safe_jsonify, serialize_firestore_data

# Inicializar Firebase
try:
    if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        # Tentar carregar das variáveis de ambiente primeiro
        cred_json = json.loads(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))
        cred = credentials.Certificate(cred_json)
    else:
        # Fallback para arquivo local
        cred = credentials.Certificate("projeto-beepy-firebase-adminsdk-fbsvc-45c41daaaf.json")
    
    firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print(f"Erro ao inicializar Firebase: {e}")
    # Fallback para arquivo local se houver erro
    try:
        cred = credentials.Certificate("projeto-beepy-firebase-adminsdk-fbsvc-45c41daaaf.json")
        firebase_admin.initialize_app(cred)
        db = firestore.client()
    except Exception as e2:
        print(f"Erro crítico ao inicializar Firebase: {e2}")
        raise


def create_app():
    flask_app = Flask(__name__)

    flask_app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "beepy-secret-key-2024")
    flask_app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "beepy-jwt-secret-key-2024")
    flask_app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)

    jwt = JWTManager(flask_app)
    
    # Configurar CORS mais permissivo
    CORS(flask_app, 
         supports_credentials=True, 
         origins="*",
         allow_headers=["Content-Type", "Authorization", "Accept"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

    # Middleware para logs de debug e tratamento de CORS
    @flask_app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = flask_app.make_default_options_response()
            headers = response.headers
            headers['Access-Control-Allow-Origin'] = '*'
            headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept'
            return response
        
        print(f"Request: {request.method} {request.url}")
        print(f"Headers: {dict(request.headers)}")
        if request.get_json(silent=True):
            print(f"Body: {request.get_json()}")

    @flask_app.after_request
    def after_request(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, Accept'
        return response

    @flask_app.route("/api/auth/login", methods=["POST"])
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
    @flask_app.route("/api/auth/verify", methods=["GET"])
    @jwt_required()
    def verify_token():
        try:
            current_user_id = get_jwt_identity()
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
            return safe_jsonify({"error": "Token inválido"}, 401)

    # Rotas de indicações
    @flask_app.route("/api/indications", methods=["GET"])
    @jwt_required()
    def get_indications():
        try:
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
                indications_ref = db.collection("indications").where(field_path="ambassadorId", op_string="==", value=current_user_id)

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

    @flask_app.route("/api/indications", methods=["POST"])
    @jwt_required()
    def create_indication():
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json()

            indication_data = {
                "ambassadorId": current_user_id,
                "clientName": data.get("clientName"),
                "clientEmail": data.get("clientEmail"),
                "clientPhone": data.get("clientPhone"),
                "origin": data.get("origin", "website"),
                "segment": data.get("segment", "geral"),
                "converted": False,
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            }

            doc_ref = db.collection("indications").add(indication_data)
            indication_data["id"] = doc_ref[1].id
            indication_data = serialize_firestore_data(indication_data)

            return safe_jsonify(indication_data, 201)

        except Exception as e:
            print(f"Erro ao criar indicação: {str(e)}")
            return safe_jsonify({"error": str(e)}, 500)

    @flask_app.route("/api/indications/<indication_id>", methods=["PUT"])
    @jwt_required()
    def update_indication(indication_id):
        try:
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

    @flask_app.route("/api/indications/<indication_id>", methods=["DELETE"])
    @jwt_required()
    def delete_indication(indication_id):
        try:
            db.collection("indications").document(indication_id).delete()
            return safe_jsonify({"message": "Indicação excluída com sucesso"}, 200)
        except Exception as e:
            print(f"Erro ao excluir indicação: {str(e)}")
            return safe_jsonify({"error": str(e)}, 500)

    # Rotas de usuários (apenas admin)
    @flask_app.route("/api/users", methods=["GET"])
    @jwt_required()
    def get_users():
        try:
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
                if "password" in user_data:
                    del user_data["password"]
                user_data = serialize_firestore_data(user_data)
                users.append(user_data)

            return safe_jsonify(users, 200)

        except Exception as e:
            print(f"Erro ao buscar usuários: {str(e)}")
            return safe_jsonify({"error": str(e)}, 500)

    @flask_app.route("/api/users", methods=["POST"])
    @jwt_required()
    def create_user():
        try:
            current_user_id = get_jwt_identity()
            user_doc = db.collection("users").document(current_user_id).get()
            
            if not user_doc.exists:
                return safe_jsonify({"error": "Usuário não encontrado"}, 404)

            user_data = user_doc.to_dict()
            if user_data["role"] != "admin":
                return safe_jsonify({"error": "Acesso negado"}, 403)

            data = request.get_json()

            required_fields = ["email", "password", "name", "role"]
            for field in required_fields:
                if not data.get(field):
                    return safe_jsonify({"error": f"{field} é obrigatório"}, 400)

            # Verificar se email já existe
            users_ref = db.collection("users")
            query = users_ref.where(field_path="email", op_string="==", value=data.get("email")).limit(1)
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
    @flask_app.route("/api/commissions", methods=["GET"])
    @jwt_required()
    def get_commissions():
        try:
            current_user_id = get_jwt_identity()
            user_doc = db.collection("users").document(current_user_id).get()
            
            if not user_doc.exists:
                return safe_jsonify({"error": "Usuário não encontrado"}, 404)

            user_data = user_doc.to_dict()

            if user_data["role"] == "admin":
                commissions_ref = db.collection("commissions")
            else:
                commissions_ref = db.collection("commissions").where(field_path="ambassadorId", op_string="==", value=current_user_id)

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

    @flask_app.route("/api/commissions", methods=["POST"])
    @jwt_required()
    def create_commission():
        try:
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
    @flask_app.route("/api/dashboard/admin", methods=["GET"])
    @jwt_required()
    def get_admin_dashboard():
        try:
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

            dashboard_data["stats"] = {
                "totalUsers": users_count,
                "totalIndications": indications_count,
                "totalCommissions": commissions_count
            }

            dashboard_data = serialize_firestore_data(dashboard_data)
            return safe_jsonify(dashboard_data, 200)

        except Exception as e:
            print(f"Erro no dashboard admin: {str(e)}")
            return safe_jsonify({"error": str(e)}, 500)

    @flask_app.route("/api/dashboard/embaixadora", methods=["GET"])
    @jwt_required()
    def get_ambassador_dashboard():
        try:
            current_user_id = get_jwt_identity()
            user_doc = db.collection("users").document(current_user_id).get()
            
            if not user_doc.exists:
                return safe_jsonify({"error": "Usuário não encontrado"}, 404)

            user_data = user_doc.to_dict()
            if user_data["role"] != "embaixadora":
                return safe_jsonify({"error": "Acesso negado"}, 403)

            dashboard_data = {}

            # Indicações da embaixadora
            indications_ref = db.collection("indications").where(field_path="ambassadorId", op_string="==", value=current_user_id)
            indications = list(indications_ref.stream())
            
            total_indications = len(indications)
            converted_indications = sum(1 for doc in indications if doc.to_dict().get("converted", False))

            dashboard_data["stats"] = {
                "totalIndications": total_indications,
                "convertedIndications": converted_indications,
                "conversionRate": (converted_indications / total_indications * 100) if total_indications > 0 else 0
            }

            dashboard_data = serialize_firestore_data(dashboard_data)
            return safe_jsonify(dashboard_data, 200)

        except Exception as e:
            print(f"Erro no dashboard embaixadora: {str(e)}")
            return safe_jsonify({"error": str(e)}, 500)

    # Rota para criar usuário admin inicial
    @flask_app.route("/api/setup", methods=["POST"])
    def setup_admin():
        try:
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
            return safe_jsonify({"message": "Usuário admin criado com sucesso"}, 201)

        except Exception as e:
            print(f"Erro ao criar admin: {str(e)}")
            return safe_jsonify({"error": str(e)}, 500)

    @flask_app.route("/")
    def home():
        return safe_jsonify({
            "message": "Beepy API - Sistema de Indicações e Comissões",
            "version": "3.0",
            "status": "online"
        })

    @flask_app.route("/health")
    def health():
        return safe_jsonify({"status": "healthy", "service": "beepy-api"})

    return flask_app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)

