import os
import json
import bcrypt
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from routes.users_firestore import users_bp
from google.cloud import firestore
from utils import serialize_firestore_data, safe_jsonify
from models.commission_installments import CommissionInstallment
from dotenv import load_dotenv

load_dotenv()

# Configurações
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-secret-key-change-in-production")

db = None

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
        local_creds_path = "projeto-beepy-firebase-adminsdk-fbsvc-72fd5c9b0e.json"
        if os.path.exists(local_creds_path):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = local_creds_path
            db = firestore.Client()
            print("Firebase conectado com arquivo local!")
        else:
            print("Arquivo de credenciais local não encontrado")
    except Exception as e:
        print(f"Erro no fallback Firebase: {e}")
        db = None

# Inicializar Flask
app = Flask(__name__)

# Configurações do Flask
app.config["SECRET_KEY"] = SECRET_KEY
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)

# Inicializar JWT
jwt = JWTManager(app)

# Configurar CORS para lidar com credenciais
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

# Registrar blueprints
app.register_blueprint(users_bp, url_prefix='/users')

# Inicializar modelo de parcelas de comissão
commission_installments = None
if db:
    commission_installments = CommissionInstallment(db)


# Rotas de autenticação
@app.route("/auth/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return "", 200

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
@app.route("/auth/verify", methods=["GET", "OPTIONS"])
@jwt_required()
def verify_token():
    if request.method == "OPTIONS":
        return "", 200

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
@app.route("/indications/ambassador", methods=["GET", "OPTIONS"])
@jwt_required()
def get_ambassador_indications():
    if request.method == "OPTIONS":
        return "", 200

    try:
        if not db:
            return safe_jsonify({"error": "Erro de conexão com banco de dados"}, 500)

        current_user_id = get_jwt_identity()
        user_doc = db.collection("users").document(current_user_id).get()

        if not user_doc.exists:
            return safe_jsonify({"error": "Usuário não encontrado"}, 404)

        user_data = user_doc.to_dict()

        # Retorna apenas indicações da embaixadora logada
        indications_ref = db.collection("indications").where(field_path="ambassadorId", op_string="==",
                                                             value=current_user_id)

        docs = indications_ref.stream()
        indications = []

        for doc in docs:
            indication_data = doc.to_dict()
            indication_data["id"] = doc.id
            indication_data = serialize_firestore_data(indication_data)
            indications.append(indication_data)

        return safe_jsonify({"indications": indications}, 200)

    except Exception as e:
        print(f"Erro ao buscar indicações da embaixadora: {str(e)}")
        return safe_jsonify({"error": str(e)}, 500)


@app.route("/indications", methods=["GET", "OPTIONS"])
@jwt_required()
def get_indications():
    if request.method == "OPTIONS":
        return "", 200

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


@app.route("/indications", methods=["POST", "OPTIONS"])
@jwt_required()
def create_indication():
    if request.method == "OPTIONS":
        return "", 200

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

        # Criar nova indicação
        indication_data = {
            "client_name": client_name,
            "email": client_email,
            "phone": client_phone,
            "origin": data.get("origin", "website"),
            "segment": data.get("segment", "geral"),
            "status": "agendado",
            "ambassadorId": current_user_id,  # ID da embaixadora que criou a indicação
            "createdAt": datetime.now(),
            "updatedAt": datetime.now(),
            "converted": False
        }

        doc_ref = db.collection("indications").add(indication_data)
        indication_data["id"] = doc_ref[1].id
        indication_data = serialize_firestore_data(indication_data)

        # Criar parcelas de comissão automaticamente
        user_doc = db.collection("users").document(current_user_id).get()
        if not user_doc.exists:
            print(f"Erro: Embaixador com ID {current_user_id} não encontrado ao criar indicação.")
            return safe_jsonify({"error": "Embaixador não encontrado"}, 404)

        ambassador_name = user_doc.to_dict().get("name", "Embaixador")

        # Usar o modelo de parcelas para criar as 3 parcelas automaticamente
        if commission_installments:
            try:
                installment_ids = commission_installments.create_installments_for_indication(
                    indication_id=indication_data["id"],
                    ambassador_id=current_user_id,
                    ambassador_name=ambassador_name,
                    client_name=client_name
                )
                print(f"Parcelas criadas para indicação {indication_data['id']}: {installment_ids}")
            except Exception as e:
                print(f"Erro ao criar parcelas: {str(e)}")
                # Continuar mesmo se houver erro na criação das parcelas
        else:
            print("Modelo de parcelas não inicializado")

        return safe_jsonify(indication_data, 201)
    except Exception as e:
        print(f"Erro ao criar indicação: {str(e)}")
        return safe_jsonify({"error": str(e)}, 500)


@app.route("/indications/<indication_id>", methods=["PUT", "OPTIONS"])
@jwt_required()
def update_indication(indication_id):
    if request.method == "OPTIONS":
        return "", 200

    try:
        if not db:
            return safe_jsonify({"error": "Erro de conexão com banco de dados"}, 500)

        data = request.get_json()
        print(f"Dados recebidos para atualização: {data}")

        update_data = {"updatedAt": datetime.now()}

        # Mapear campos do frontend para Firestore
        field_mapping = {
            "client_name": "client_name",
            "email": "email",
            "phone": "phone",
            "origin": "origin",
            "segment": "segment",
            "converted": "converted"
        }

        for frontend_field, firestore_field in field_mapping.items():
            if frontend_field in data:
                update_data[firestore_field] = data[frontend_field]
                print(f"Mapeando {frontend_field} -> {firestore_field}: {data[frontend_field]}")

        print(f"Dados para atualização no Firestore: {update_data}")
        db.collection("indications").document(indication_id).update(update_data)
        print(f"Indicação {indication_id} atualizada com sucesso")
        return safe_jsonify({"message": "Indicação atualizada com sucesso"}, 200)

    except Exception as e:
        print(f"Erro ao atualizar indicação: {str(e)}")
        return safe_jsonify({"error": str(e)}, 500)


@app.route("/indications/<indication_id>/status", methods=["PUT", "OPTIONS"])
@jwt_required()
def update_indication_status(indication_id):
    if request.method == "OPTIONS":
        return "", 200

    try:
        if not db:
            return safe_jsonify({"error": "Erro de conexão com banco de dados"}, 500)

        data = request.get_json()
        new_status = data.get("status")

        if new_status not in ["agendado", "aprovado", "não aprovado"]:
            return safe_jsonify({"error": "Status inválido. Use 'agendado', 'aprovado' ou 'não aprovado'"}, 400)

        # Buscar a indicação para obter dados do embaixador
        indication_doc = db.collection("indications").document(indication_id).get()
        if not indication_doc.exists:
            return safe_jsonify({"error": "Indicação não encontrada"}, 404)

        indication_data = indication_doc.to_dict()

        update_data = {"status": new_status, "updatedAt": datetime.now()}
        db.collection("indications").document(indication_id).update(update_data)

        # Se a indicação foi aprovada, criar ou atualizar comissão
        if new_status == "aprovado":
            # Buscar dados da embaixadora
            ambassador_id = indication_data.get("ambassadorId")
            ambassador_name = "Embaixadora não encontrada"

            if ambassador_id:
                ambassador_doc = db.collection("users").document(ambassador_id).get()
                if ambassador_doc.exists:
                    ambassador_data = ambassador_doc.to_dict()
                    ambassador_name = ambassador_data.get("name", "Nome não informado")

            # Verificar se já existe uma comissão para esta indicação
            existing_commission_query = db.collection("commissions").where(
                field_path="indicationId", op_string="==", value=indication_id
            ).limit(1)
            existing_commissions = list(existing_commission_query.stream())

            if existing_commissions:
                # Atualizar comissão existente
                commission_doc = existing_commissions[0]
                commission_update_data = {
                    "status": "pendente",
                    "ambassadorName": ambassador_name,
                    "clientName": indication_data.get("client_name", "Cliente não informado"),
                    "updatedAt": datetime.now()
                }
                db.collection("commissions").document(commission_doc.id).update(commission_update_data)
                print(f"Comissão atualizada para indicação aprovada: {indication_id}")
            else:
                # Criar nova comissão
                commission_data = {
                    "ambassadorId": indication_data.get("ambassadorId"),
                    "ambassadorName": ambassador_name,
                    "indicationId": indication_id,
                    "clientName": indication_data.get("client_name", "Cliente não informado"),
                    "value": data.get("commissionValue", 500.0),  # Valor padrão ou vindo do request
                    "status": "pendente",
                    "createdAt": datetime.now(),
                    "updatedAt": datetime.now()
                }

                doc_ref = db.collection("commissions").add(commission_data)
                print(f"Nova comissão criada para indicação aprovada: {indication_id} -> {doc_ref[1].id}")

        elif new_status == "não aprovado":
            # Se rejeitada, remover comissão se existir
            existing_commission_query = db.collection("commissions").where(
                field_path="indicationId", op_string="==", value=indication_id
            )
            existing_commissions = list(existing_commission_query.stream())

            for commission_doc in existing_commissions:
                db.collection("commissions").document(commission_doc.reference.id).delete()
                print(f"Comissão removida para indicação rejeitada: {indication_id}")

        return safe_jsonify({"message": "Status da indicação atualizado com sucesso"}, 200)

    except Exception as e:
        print(f"Erro ao atualizar status da indicação: {str(e)}")
        return safe_jsonify({"error": str(e)}, 500)


@app.route("/indications/<indication_id>", methods=["DELETE", "OPTIONS"])
@jwt_required()
def delete_indication(indication_id):
    if request.method == "OPTIONS":
        return "", 200

    try:
        if not db:
            return safe_jsonify({"error": "Erro de conexão com banco de dados"}, 500)

        db.collection("indications").document(indication_id).delete()
        return safe_jsonify({"message": "Indicação excluída com sucesso"}, 200)
    except Exception as e:
        print(f"Erro ao excluir indicação: {str(e)}")
        return safe_jsonify({"error": str(e)}, 500)


# Rotas de usuários (apenas admin)
@app.route("/users", methods=["GET", "OPTIONS"])
@jwt_required()
def get_users():
    if request.method == "OPTIONS":
        return "", 200

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
            # Remover senha se existir
            user_data.pop("password", None)  # Remove password se existir, senão ignora
            user_data = serialize_firestore_data(user_data)
            users.append(user_data)

        return safe_jsonify(users, 200)

    except Exception as e:
        print(f"Erro ao buscar usuários: {str(e)}")
        return safe_jsonify({"error": str(e)}, 500)


@app.route("/users", methods=["POST", "OPTIONS"])
@jwt_required()
def create_user():
    if request.method == "OPTIONS":
        return "", 200

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

        if not data:
            return safe_jsonify({"error": "Dados não fornecidos"}, 400)

        # Validar campos obrigatórios
        email = data.get("email")
        password = data.get("password")
        name = data.get("name")
        role = data.get("role")

        if not email:
            return safe_jsonify({"error": "Email é obrigatório"}, 400)

        if not password:
            return safe_jsonify({"error": "Senha é obrigatória"}, 400)

        if not name:
            return safe_jsonify({"error": "Nome é obrigatório"}, 400)

        if not role:
            return safe_jsonify({"error": "Função é obrigatória"}, 400)

        # Verificar se email já existe
        query = db.collection("users").where(field_path="email", op_string="==", value=email).limit(1)
        existing_users = list(query.stream())

        if existing_users:
            return safe_jsonify({"error": "Email já está em uso"}, 400)

        # Criar hash da senha
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        new_user_data = {
            "email": email,
            "password": hashed_password,
            "name": name,
            "role": role,
            "phone": data.get("phone", ""),
            "active": True,
            "createdAt": datetime.now(),
            "lastActiveAt": datetime.now()
        }

        doc_ref = db.collection("users").add(new_user_data)
        new_user_data["id"] = doc_ref[1].id
        del new_user_data["password"]
        new_user_data = serialize_firestore_data(new_user_data)

        print(f"Usuário criado com sucesso: {email}")
        return safe_jsonify(new_user_data, 201)

    except Exception as e:
        print(f"Erro ao criar usuário: {str(e)}")
        return safe_jsonify({"error": str(e)}, 500)


# Rotas de comissões
@app.route("/commissions", methods=["GET", "OPTIONS"])
@jwt_required()
def get_commissions():
    if request.method == "OPTIONS":
        return "", 200

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

        # Buscar todos os usuários para mapear embaixadores
        users_ref = db.collection("users")
        all_users = list(users_ref.stream())
        users_map = {}
        for user_doc in all_users:
            users_map[user_doc.id] = user_doc.to_dict()

        for doc in docs:
            commission_data = doc.to_dict()
            commission_data["id"] = doc.id

            # Adicionar dados do embaixador
            ambassador_id = commission_data.get("ambassadorId")
            if ambassador_id and ambassador_id in users_map:
                ambassador_data = users_map[ambassador_id]
                commission_data["ambassadorName"] = ambassador_data.get("name", "Nome não disponível")
                commission_data["ambassadorEmail"] = ambassador_data.get("email", "Email não disponível")
            else:
                commission_data["ambassadorName"] = "Embaixador não encontrado"
                commission_data["ambassadorEmail"] = "Email não disponível"

            # Adicionar dados da indicação se existir
            indication_id = commission_data.get("indicationId")
            if indication_id:
                try:
                    indication_doc = db.collection("indications").document(indication_id).get()
                    if indication_doc.exists:
                        indication_data = indication_doc.to_dict()
                        commission_data["indicationStatus"] = indication_data.get("status", "pendente")
                        commission_data["clientName"] = indication_data.get("client_name", "Cliente não disponível")
                        commission_data["clientEmail"] = indication_data.get("email", "Email não disponível")
                    else:
                        commission_data["indicationStatus"] = "indicação não encontrada"
                        commission_data["clientName"] = commission_data.get("clientName", "Cliente não disponível")
                except Exception as e:
                    print(f"Erro ao buscar indicação {indication_id}: {e}")
                    commission_data["indicationStatus"] = "erro ao buscar"

            commission_data = serialize_firestore_data(commission_data)
            commissions.append(commission_data)

        return safe_jsonify(commissions, 200)

    except Exception as e:
        print(f"Erro ao buscar comissões: {str(e)}")
        return safe_jsonify({"error": str(e)}, 500)


@app.route("/commissions", methods=["POST", "OPTIONS"])
@jwt_required()
def create_commission():
    if request.method == "OPTIONS":
        return "", 200

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
@app.route("/dashboard/admin", methods=["GET", "OPTIONS"])
@jwt_required()
def get_admin_dashboard():
    if request.method == "OPTIONS":
        return "", 200

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
        from datetime import timezone
        current_month = datetime.now().month
        current_year = datetime.now().year

        commissions_ref = db.collection("commissions")
        all_commissions = list(commissions_ref.stream())

        monthly_commissions = 0
        for commission_doc in all_commissions:
            commission_data = commission_doc.to_dict()
            created_at = commission_data.get("createdAt")
            if created_at:
                # Converter para datetime naive se for offset-aware
                if hasattr(created_at, 'tzinfo') and created_at.tzinfo is not None:
                    created_at = created_at.replace(tzinfo=None)
                if created_at.month == current_month and created_at.year == current_year:
                    monthly_commissions += commission_data.get("value", 0)

        # Dados para gráficos
        # 1. Indicações mês a mês (últimos 6 meses)
        indications_monthly = []
        all_indications = list(db.collection("indications").stream())

        # Contar indicações por status
        approved_indications = 0
        pending_indications = 0
        rejected_indications = 0

        for indication_doc in all_indications:
            indication_data = indication_doc.to_dict()
            status = indication_data.get("status", "pendente")
            if status == "aprovado":
                approved_indications += 1
            elif status == "não aprovado":
                rejected_indications += 1
            else:
                pending_indications += 1

        for i in range(6):
            month_date = datetime.now() - timedelta(days=30 * i)
            month_count = 0
            month_approved = 0
            for indication_doc in all_indications:
                indication_data = indication_doc.to_dict()
                created_at = indication_data.get("createdAt")
                if created_at:
                    # Converter para datetime naive se for offset-aware
                    if hasattr(created_at, 'tzinfo') and created_at.tzinfo is not None:
                        created_at = created_at.replace(tzinfo=None)
                    if created_at.month == month_date.month and created_at.year == month_date.year:
                        month_count += 1
                        if indication_data.get("status") == "aprovado":
                            month_approved += 1
            indications_monthly.append({
                "month": month_date.strftime("%b"),
                "count": month_count,
                "approved": month_approved
            })

        # 2. Leads por origem
        origins_data = {}
        for indication_doc in all_indications:
            indication_data = indication_doc.to_dict()
            origin = indication_data.get("origin", "website")
            origins_data[origin] = origins_data.get(origin, 0) + 1

        leads_origin = [{"name": k, "value": v} for k, v in origins_data.items()]

        # 3. Conversão por segmento
        segment_data = {}
        for indication_doc in all_indications:
            indication_data = indication_doc.to_dict()
            segment = indication_data.get("segment", "geral")
            status = indication_data.get("status", "pendente")

            if segment not in segment_data:
                segment_data[segment] = {"total": 0, "converted": 0}

            segment_data[segment]["total"] += 1
            if status == "aprovado":
                segment_data[segment]["converted"] += 1

        conversion_by_segment = []
        for segment, data in segment_data.items():
            conversion_rate = (data["converted"] / data["total"] * 100) if data["total"] > 0 else 0
            conversion_by_segment.append({
                "segment": segment,
                "total": data["total"],
                "converted": data["converted"],
                "rate": conversion_rate
            })

        # 4. Vendas mês a mês (comissões como proxy)
        sales_monthly = []
        for i in range(6):
            month_date = datetime.now() - timedelta(days=30 * i)
            month_sales = 0
            for commission_doc in all_commissions:
                commission_data = commission_doc.to_dict()
                created_at = commission_data.get("createdAt")
                if created_at:
                    # Converter para datetime naive se for offset-aware
                    if hasattr(created_at, 'tzinfo') and created_at.tzinfo is not None:
                        created_at = created_at.replace(tzinfo=None)
                    if created_at.month == month_date.month and created_at.year == month_date.year:
                        month_sales += commission_data.get("value", 0)
            sales_monthly.append({
                "month": month_date.strftime("%b"),
                "value": month_sales
            })

        # 5. Top embaixadoras por volume de indicação
        all_users = list(db.collection("users").stream())
        ambassador_stats = {}

        for user_doc in all_users:
            user_data = user_doc.to_dict()
            if user_data.get("role") == "embaixadora":
                user_id = user_doc.id
                user_name = user_data.get("name", "Sem nome")

                # Contar indicações desta embaixadora
                user_indications = 0
                for indication_doc in all_indications:
                    indication_data = indication_doc.to_dict()
                    if indication_data.get("ambassadorId") == user_id:
                        user_indications += 1

                if user_indications > 0:
                    ambassador_stats[user_name] = user_indications

        # Ordenar por volume e pegar top 5
        top_ambassadors = sorted(ambassador_stats.items(), key=lambda x: x[1], reverse=True)[:5]
        top_ambassadors_data = [{"name": name, "indications": count} for name, count in top_ambassadors]

        # 6. Embaixadoras ativas (últimos 60 dias)
        sixty_days_ago = datetime.now() - timedelta(days=60)
        active_ambassadors = 0
        total_ambassadors = 0

        for user_doc in all_users:
            user_data = user_doc.to_dict()
            if user_data.get("role") == "embaixadora":
                total_ambassadors += 1

                # Verificar se tem indicações nos últimos 60 dias
                has_recent_activity = False
                for indication_doc in all_indications:
                    indication_data = indication_doc.to_dict()
                    if indication_data.get("ambassadorId") == user_doc.id:
                        created_at = indication_data.get("createdAt")
                        if created_at:
                            # Converter para datetime naive se for offset-aware
                            if hasattr(created_at, 'tzinfo') and created_at.tzinfo is not None:
                                created_at = created_at.replace(tzinfo=None)
                            if created_at >= sixty_days_ago:
                                has_recent_activity = True
                                break

                if has_recent_activity:
                    active_ambassadors += 1

        indications_for_conversion = approved_indications + pending_indications
        active_percentage = (active_ambassadors / total_ambassadors * 100) if total_ambassadors > 0 else 0

        dashboard_data["stats"] = {
            "totalUsers": users_count,
            "totalIndications": indications_count,
            "totalCommissions": commissions_count,
            "monthlyCommissions": monthly_commissions,
            "activeAmbassadors": active_ambassadors,
            "activePercentage": round(active_percentage, 2),
            "approvedIndications": approved_indications,
            "pendingIndications": pending_indications,
            "rejectedIndications": rejected_indications,
            "approvalRate": round(
                (approved_indications / indications_for_conversion * 100) if indications_for_conversion > 0 else 0, 2)
        }
        dashboard_data["charts"] = {
            "indicationsMonthly": list(reversed(indications_monthly)),
            "leadsOrigin": leads_origin,
            "conversionBySegment": conversion_by_segment,
            "salesMonthly": list(reversed(sales_monthly)),
            "topAmbassadors": top_ambassadors_data
        }

        dashboard_data = serialize_firestore_data(dashboard_data)
        return safe_jsonify(dashboard_data, 200)

    except Exception as e:
        print(f"Erro no dashboard admin: {str(e)}")
        return safe_jsonify({"error": str(e)}, 500)


@app.route("/dashboard/ambassador", methods=["GET", "OPTIONS"])
@jwt_required()
def get_ambassador_dashboard():
    if request.method == "OPTIONS":
        return "", 200

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

        total_indications_count = len(indications)

        # Contar por status
        approved_indications = 0
        pending_indications = 0
        rejected_indications = 0

        for doc in indications:
            indication_data = doc.to_dict()
            status = indication_data.get("status", "agendado")
            if status == "aprovado":
                approved_indications += 1
            elif status == "não aprovado":
                rejected_indications += 1
            else:
                pending_indications += 1

        total_indications = len(indications)

        # Comissões da embaixadora
        commissions_ref = db.collection("commissions").where(field_path="ambassadorId", op_string="==",
                                                             value=current_user_id)
        commissions = list(commissions_ref.stream())

        total_commissions = sum(doc.to_dict().get("value", 0) for doc in commissions)

        # Comissões do mês atual
        current_month = datetime.now().month
        current_year = datetime.now().year
        monthly_commission = 0

        for commission_doc in commissions:
            commission_data = commission_doc.to_dict()
            created_at = commission_data.get("createdAt")
            if created_at:
                # Converter para datetime naive se for offset-aware
                if hasattr(created_at, 'tzinfo') and created_at.tzinfo is not None:
                    created_at = created_at.replace(tzinfo=None)
                if created_at.month == current_month and created_at.year == current_year:
                    monthly_commission += commission_data.get("value", 0)

        # Dados para gráficos
        # 1. Indicações mês a mês (últimos 12 meses)
        monthly_indications = []
        for i in range(12):
            month_date = datetime.now() - timedelta(days=30 * i)
            month_count = 0
            for indication_doc in indications:
                indication_data = indication_doc.to_dict()
                created_at = indication_data.get("createdAt")
                if created_at:
                    # Converter para datetime naive se for offset-aware
                    if hasattr(created_at, 'tzinfo') and created_at.tzinfo is not None:
                        created_at = created_at.replace(tzinfo=None)
                    if created_at.month == month_date.month and created_at.year == month_date.year:
                        month_count += 1
            monthly_indications.append({
                "month": month_date.strftime("%b/%Y"),
                "count": month_count
            })

        # 2. Comissões mês a mês (últimos 12 meses)
        monthly_commissions = []
        for i in range(12):
            month_date = datetime.now() - timedelta(days=30 * i)
            month_total = 0
            for commission_doc in commissions:
                commission_data = commission_doc.to_dict()
                created_at = commission_data.get("createdAt")
                if created_at:
                    # Converter para datetime naive se for offset-aware
                    if hasattr(created_at, 'tzinfo') and created_at.tzinfo is not None:
                        created_at = created_at.replace(tzinfo=None)
                    if created_at.month == month_date.month and created_at.year == month_date.year:
                        month_total += commission_data.get("value", 0)
            monthly_commissions.append({
                "month": month_date.strftime("%b/%Y"),
                "total": month_total
            })

        # 3. Indicações por segmento
        niche_stats = {}
        converted_segments = {}
        for indication_doc in indications:
            indication_data = indication_doc.to_dict()
            niche = indication_data.get("segment", "geral")
            converted = indication_data.get("converted", False)
            niche_stats[niche] = niche_stats.get(niche, 0) + 1
            if converted:
                converted_segments[niche] = converted_segments.get(niche, 0) + 1

        niche_data = []
        total_for_percentage = sum(niche_stats.values())
        for niche, count in niche_stats.items():
            converted_niche = converted_segments.get(niche, 0)
            conversion_rate = (converted_niche / count * 100) if count > 0 else 0
            percent = (count / total_for_percentage) if total_for_percentage > 0 else 0
            niche_data.append({
                "niche": niche,
                "count": count,
                "converted": converted_niche,
                "percent": percent,
                "conversion_rate": conversion_rate
            })

        # 4. Performance mensal (últimos 5 meses)
        monthly_performance = []
        for i in range(5):
            month_date = datetime.now() - timedelta(days=30 * i)
            month_indications = 0
            for indication_doc in indications:
                indication_data = indication_doc.to_dict()
                created_at = indication_data.get("createdAt")
                if created_at:
                    # Converter para datetime naive se for offset-aware
                    if hasattr(created_at, 'tzinfo') and created_at.tzinfo is not None:
                        created_at = created_at.replace(tzinfo=None)
                    if created_at.month == month_date.month and created_at.year == month_date.year:
                        month_indications += 1
            monthly_performance.append({
                "month": month_date.strftime("%b"),
                "total_indications": total_indications,
            })

        indications_for_conversion = approved_indications + pending_indications
        print(
            f"Ambassador Dashboard - Approved: {approved_indications}, Pending: {pending_indications}, Rejected: {rejected_indications}, Total Indications: {total_indications}")
        print(f"Ambassador Dashboard - Indications for Conversion: {indications_for_conversion}")
        dashboard_data["stats"] = {
            "total_indications": total_indications_display,
            "approved_sales": approved_indications,
            "conversion_rate": round(
                (approved_indications / indications_for_conversion * 100) if indications_for_conversion > 0 else 0, 2),
            "current_month_commission": monthly_commission,
            "total_commissions": total_commissions,
            "pending_indications": pending_indications,
            "rejected_indications": rejected_indications
        }

        dashboard_data["monthly_indications"] = monthly_indications
        dashboard_data["monthly_commissions"] = monthly_commissions
        dashboard_data["niche_stats"] = niche_data
        dashboard_data["monthly_performance"] = monthly_performance

        dashboard_data = serialize_firestore_data(dashboard_data)
        return safe_jsonify(dashboard_data, 200)

    except Exception as e:
        print(f"Erro no dashboard embaixadora: {str(e)}")
        return safe_jsonify({"error": str(e)}, 500)


# Rota para criar usuário admin inicial

@app.route("/")
def home():
    return safe_jsonify({
        "message": "Beepy API - Sistema de Indicações e Comissões",
        "version": "3.3",
        "status": "online",
        "cors_configured": True,
        "gunicorn_compatible": True,
        "endpoints": [
            "/auth/login",
            "/auth/verify",
            "/indications",
            "/commissions",
            "/commission-installments",
            "/users",
            "/dashboard/admin",
            "/dashboard/ambassador",
            "/setup",
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


@app.route("/commissions/<commission_id>", methods=["PUT", "OPTIONS"])
@jwt_required()
def update_commission(commission_id):
    if request.method == "OPTIONS":
        return "", 200

    try:
        if not db:
            return safe_jsonify({"error": "Erro de conexão com banco de dados"}, 500)

        data = request.get_json()
        update_data = {"updatedAt": datetime.now()}

        for field in ["status", "value", "ambassadorId", "indicationId"]:
            if field in data:
                update_data[field] = data[field]

        db.collection("commissions").document(commission_id).update(update_data)
        return safe_jsonify({"message": "Comissão atualizada com sucesso"}, 200)

    except Exception as e:
        print(f"Erro ao atualizar comissão: {str(e)}")
        return safe_jsonify({"error": str(e)}, 500)


@app.route("/commissions/<commission_id>", methods=["DELETE", "OPTIONS"])
@jwt_required()
def delete_commission(commission_id):
    if request.method == "OPTIONS":
        return "", 200

    try:
        if not db:
            return safe_jsonify({"error": "Erro de conexão com banco de dados"}, 500)

        db.collection("commissions").document(commission_id).delete()
        return safe_jsonify({"message": "Comissão excluída com sucesso"}, 200)
    except Exception as e:
        print(f"Erro ao excluir comissão: {str(e)}")
        return safe_jsonify({"error": str(e)}, 500)


# Para desenvolvimento local
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)


@app.route("/users/<user_id>", methods=["PUT", "OPTIONS"])
@jwt_required()
def update_user(user_id):
    if request.method == "OPTIONS":
        return "", 200

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

        # Verificar se o usuário a ser atualizado existe
        target_user_doc = db.collection("users").document(user_id).get()
        if not target_user_doc.exists:
            return safe_jsonify({"error": "Usuário a ser atualizado não encontrado"}, 404)

        data = request.get_json()
        if not data:
            return safe_jsonify({"error": "Dados não fornecidos"}, 400)

        update_data = {"updatedAt": datetime.now()}

        # Campos que podem ser atualizados
        for field in ["name", "email", "role", "phone", "active"]:
            if field in data:
                update_data[field] = data[field]

        # Se uma nova senha foi fornecida, fazer hash
        if "password" in data and data["password"]:
            hashed_password = bcrypt.hashpw(data["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            update_data["password"] = hashed_password

        db.collection("users").document(user_id).update(update_data)
        return safe_jsonify({"message": "Usuário atualizado com sucesso"}, 200)

    except Exception as e:
        print(f"Erro ao atualizar usuário: {str(e)}")
        return safe_jsonify({"error": str(e)}, 500)


@app.route("/users/<user_id>", methods=["DELETE", "OPTIONS"])
@jwt_required()
def delete_user(user_id):
    if request.method == "OPTIONS":
        return "", 200

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

        # Verificar se o usuário a ser excluído existe
        target_user_doc = db.collection("users").document(user_id).get()
        if not target_user_doc.exists:
            return safe_jsonify({"error": "Usuário a ser excluído não encontrado"}, 404)

        # Não permitir que um admin exclua a si mesmo
        if user_id == current_user_id:
            return safe_jsonify({"error": "Você não pode excluir seu próprio usuário"}, 400)

        db.collection("users").document(user_id).delete()
        return safe_jsonify({"message": "Usuário excluído com sucesso"}, 200)
    except Exception as e:
        print(f"Erro ao excluir usuário: {str(e)}")
        return safe_jsonify({"error": str(e)}, 500)


# Rotas para parcelas de comissão
@app.route("/commission-installments", methods=["GET", "OPTIONS"])
@jwt_required()
def get_commission_installments():
    """Busca parcelas de comissão com filtros opcionais"""
    if request.method == "OPTIONS":
        return "", 200

    try:
        if not db or not commission_installments:
            return safe_jsonify({"error": "Erro de conexão com banco de dados"}, 500)

        current_user_id = get_jwt_identity()
        user_doc = db.collection("users").document(current_user_id).get()

        if not user_doc.exists:
            return safe_jsonify({"error": "Usuário não encontrado"}, 404)

        user_data = user_doc.to_dict()

        # Obter filtros da query string
        status_filter = request.args.get("status")
        ambassador_id_filter = request.args.get("ambassador_id")
        month_filter = request.args.get("month")
        year_filter = request.args.get("year")

        filters = {}
        if status_filter:
            filters["status"] = status_filter
        if month_filter:
            filters["month"] = month_filter
        if year_filter:
            filters["year"] = year_filter

        # Se for admin, pode ver todas as parcelas ou filtrar por embaixadora
        if user_data["role"] == "admin":
            if ambassador_id_filter:
                filters["ambassador_id"] = ambassador_id_filter
            installments = commission_installments.get_all_installments(filters)
        else:
            # Se for embaixadora, só vê suas próprias parcelas
            installments = commission_installments.get_installments_by_ambassador(
                current_user_id, status_filter
            )

        # Serializar dados do Firestore
        for installment in installments:
            installment = serialize_firestore_data(installment)

        return safe_jsonify({"installments": installments}, 200)

    except Exception as e:
        print(f"Erro ao buscar parcelas: {str(e)}")
        return safe_jsonify({"error": str(e)}, 500)


@app.route("/commission-installments/<installment_id>/status", methods=["PUT", "OPTIONS"])
@jwt_required()
def update_installment_status(installment_id):
    """Atualiza o status de uma parcela"""
    if request.method == "OPTIONS":
        return "", 200

    try:
        if not db or not commission_installments:
            return safe_jsonify({"error": "Erro de conexão com banco de dados"}, 500)

        current_user_id = get_jwt_identity()
        user_doc = db.collection("users").document(current_user_id).get()

        if not user_doc.exists:
            return safe_jsonify({"error": "Usuário não encontrado"}, 404)

        user_data = user_doc.to_dict()

        # Apenas admins podem atualizar status de parcelas
        if user_data["role"] != "admin":
            return safe_jsonify({"error": "Acesso negado"}, 403)

        data = request.get_json()
        new_status = data.get("status")
        notes = data.get("notes", "")

        if new_status not in ["pendente", "pago", "atrasado"]:
            return safe_jsonify({"error": "Status inválido. Use 'pendente', 'pago' ou 'atrasado'"}, 400)

        # Atualizar status da parcela
        payment_date = datetime.now() if new_status == "pago" else None
        success = commission_installments.update_installment_status(
            installment_id, new_status, payment_date, notes
        )

        if success:
            return safe_jsonify({"message": "Status da parcela atualizado com sucesso"}, 200)
        else:
            return safe_jsonify({"error": "Erro ao atualizar status da parcela"}, 500)

    except Exception as e:
        print(f"Erro ao atualizar status da parcela: {str(e)}")
        return safe_jsonify({"error": str(e)}, 500)


@app.route("/commission-installments/summary", methods=["GET", "OPTIONS"])
@jwt_required()
def get_commission_summary():
    """Retorna resumo das comissões"""
    if request.method == "OPTIONS":
        return "", 200

    try:
        if not db or not commission_installments:
            return safe_jsonify({"error": "Erro de conexão com banco de dados"}, 500)

        current_user_id = get_jwt_identity()
        user_doc = db.collection("users").document(current_user_id).get()

        if not user_doc.exists:
            return safe_jsonify({"error": "Usuário não encontrado"}, 404)

        user_data = user_doc.to_dict()

        # Obter filtro de embaixadora se fornecido (apenas para admins)
        ambassador_id_filter = request.args.get("ambassador_id")

        if user_data["role"] == "admin":
            # Admin pode ver resumo geral ou de uma embaixadora específica
            summary = commission_installments.get_commission_summary(ambassador_id_filter)
        else:
            # Embaixadora só vê seu próprio resumo
            summary = commission_installments.get_commission_summary(current_user_id)

        return safe_jsonify(summary, 200)

    except Exception as e:
        print(f"Erro ao gerar resumo das comissões: {str(e)}")
        return safe_jsonify({"error": str(e)}, 500)


@app.route("/commission-installments/indication/<indication_id>", methods=["GET", "OPTIONS"])
@jwt_required()
def get_installments_by_indication(indication_id):
    """Busca parcelas de uma indicação específica"""
    if request.method == "OPTIONS":
        return "", 200

    try:
        if not db or not commission_installments:
            return safe_jsonify({"error": "Erro de conexão com banco de dados"}, 500)

        current_user_id = get_jwt_identity()
        user_doc = db.collection("users").document(current_user_id).get()

        if not user_doc.exists:
            return safe_jsonify({"error": "Usuário não encontrado"}, 404)

        user_data = user_doc.to_dict()

        # Verificar se a indicação existe e se o usuário tem acesso
        indication_doc = db.collection("indications").document(indication_id).get()
        if not indication_doc.exists:
            return safe_jsonify({"error": "Indicação não encontrada"}, 404)

        indication_data = indication_doc.to_dict()

        # Se não for admin, verificar se é a embaixadora da indicação
        if user_data["role"] != "admin" and indication_data.get("ambassadorId") != current_user_id:
            return safe_jsonify({"error": "Acesso negado"}, 403)

        # Buscar parcelas da indicação
        installments = commission_installments.get_installments_by_indication(indication_id)

        # Serializar dados do Firestore
        for installment in installments:
            installment = serialize_firestore_data(installment)

        return safe_jsonify({"installments": installments}, 200)

    except Exception as e:
        print(f"Erro ao buscar parcelas da indicação: {str(e)}")
        return safe_jsonify({"error": str(e)}, 500)


@app.route("/commission-installments/check-overdue", methods=["POST", "OPTIONS"])
@jwt_required()
def check_overdue_installments():
    """Verifica e marca parcelas em atraso (apenas para admins)"""
    if request.method == "OPTIONS":
        return "", 200

    try:
        if not db or not commission_installments:
            return safe_jsonify({"error": "Erro de conexão com banco de dados"}, 500)

        current_user_id = get_jwt_identity()
        user_doc = db.collection("users").document(current_user_id).get()

        if not user_doc.exists:
            return safe_jsonify({"error": "Usuário não encontrado"}, 404)

        user_data = user_doc.to_dict()

        # Apenas admins podem executar esta operação
        if user_data["role"] != "admin":
            return safe_jsonify({"error": "Acesso negado"}, 403)

        # Verificar parcelas em atraso
        overdue_installments = commission_installments.check_overdue_installments()

        # Serializar dados do Firestore
        for installment in overdue_installments:
            installment = serialize_firestore_data(installment)

        return safe_jsonify({
            "message": f"{len(overdue_installments)} parcelas marcadas como atrasadas",
            "overdue_installments": overdue_installments
        }, 200)

    except Exception as e:
        print(f"Erro ao verificar parcelas em atraso: {str(e)}")
        return safe_jsonify({"error": str(e)}, 500)


# Rota de setup para criar usuário admin inicial
@app.route("/setup", methods=["POST", "OPTIONS"])
def setup():
    if request.method == "OPTIONS":
        return "", 200

    try:
        if not db:
            return safe_jsonify({"error": "Erro de conexão com banco de dados"}, 500)

        # Verificar se já existe um admin
        users_ref = db.collection("users")
        admin_query = users_ref.where(field_path="role", op_string="==", value="admin").limit(1)
        admin_docs = list(admin_query.stream())

        if admin_docs:
            return safe_jsonify({"message": "Admin já existe no sistema"}, 200)

        # Criar usuário admin padrão
        admin_password = "admin123"
        hashed_password = bcrypt.hashpw(admin_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        admin_data = {
            "email": "admin@beepy.com",
            "password": hashed_password,
            "name": "Administrador",
            "role": "admin",
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }

        db.collection("users").add(admin_data)
        print("Usuário admin criado com sucesso!")

        return safe_jsonify({
            "message": "Usuário admin criado com sucesso",
            "email": "admin@beepy.com",
            "password": "admin123"
        }, 201)

    except Exception as e:
        print(f"Erro no setup: {str(e)}")
        return safe_jsonify({"error": str(e)}, 500)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)



@app.route("/commission-installments/<installment_id>", methods=["DELETE", "OPTIONS"])
@jwt_required()
def delete_commission_installment(installment_id):
    """Exclui uma parcela de comissão (apenas para admins)"""
    if request.method == "OPTIONS":
        return "", 200

    try:
        if not db:
            return safe_jsonify({"error": "Erro de conexão com banco de dados"}, 500)

        current_user_id = get_jwt_identity()
        user_doc = db.collection("users").document(current_user_id).get()

        if not user_doc.exists:
            return safe_jsonify({"error": "Usuário não encontrado"}, 404)

        user_data = user_doc.to_dict()

        # Apenas admins podem excluir parcelas
        if user_data["role"] != "admin":
            return safe_jsonify({"error": "Acesso negado"}, 403)

        # Verificar se a parcela existe
        installment_doc = db.collection("commission_installments").document(installment_id).get()
        if not installment_doc.exists:
            return safe_jsonify({"error": "Parcela não encontrada"}, 404)

        # Excluir a parcela
        db.collection("commission_installments").document(installment_id).delete()
        
        print(f"Parcela {installment_id} excluída com sucesso pelo admin {current_user_id}")
        return safe_jsonify({"message": "Parcela excluída com sucesso"}, 200)

    except Exception as e:
        print(f"Erro ao excluir parcela: {str(e)}")
        return safe_jsonify({"error": str(e)}, 500)

