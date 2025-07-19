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


@app.route("/indications/<indication_id>", methods=["PUT", "OPTIONS"])
@jwt_required()
def update_indication(indication_id):
    if request.method == "OPTIONS":
        return "", 200
        
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

        for doc in docs:
            commission_data = doc.to_dict()
            commission_data["id"] = doc.id
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

        # Dados para gráficos
        # 1. Indicações mês a mês (últimos 6 meses)
        indications_monthly = []
        all_indications = list(db.collection("indications").stream())
        
        for i in range(6):
            month_date = datetime.now() - timedelta(days=30*i)
            month_count = 0
            for indication_doc in all_indications:
                indication_data = indication_doc.to_dict()
                created_at = indication_data.get("createdAt")
                if created_at and created_at.month == month_date.month and created_at.year == month_date.year:
                    month_count += 1
            indications_monthly.append({
                "month": month_date.strftime("%b"),
                "count": month_count
            })
        
        # 2. Leads por origem
        origins_data = {}
        for indication_doc in all_indications:
            indication_data = indication_doc.to_dict()
            origin = indication_data.get("origin", "website")
            origins_data[origin] = origins_data.get(origin, 0) + 1
        
        leads_origin = [{"name": k, "value": v} for k, v in origins_data.items()]
        
        # 3. Conversão por segmento
        segments_data = {}
        converted_segments = {}
        for indication_doc in all_indications:
            indication_data = indication_doc.to_dict()
            segment = indication_data.get("segment", "geral")
            converted = indication_data.get("converted", False)
            
            segments_data[segment] = segments_data.get(segment, 0) + 1
            if converted:
                converted_segments[segment] = converted_segments.get(segment, 0) + 1
        
        conversion_by_segment = []
        for segment, total in segments_data.items():
            converted = converted_segments.get(segment, 0)
            conversion_rate = (converted / total * 100) if total > 0 else 0
            conversion_by_segment.append({
                "segment": segment,
                "total": total,
                "converted": converted,
                "rate": round(conversion_rate, 1)
            })
        
        # 4. Vendas mês a mês (comissões como proxy)
        sales_monthly = []
        for i in range(6):
            month_date = datetime.now() - timedelta(days=30*i)
            month_sales = 0
            for commission_doc in all_commissions:
                commission_data = commission_doc.to_dict()
                created_at = commission_data.get("createdAt")
                if created_at and created_at.month == month_date.month and created_at.year == month_date.year:
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
                        if created_at and created_at >= sixty_days_ago:
                            has_recent_activity = True
                            break
                
                if has_recent_activity:
                    active_ambassadors += 1
        
        active_percentage = (active_ambassadors / total_ambassadors * 100) if total_ambassadors > 0 else 0

        dashboard_data["stats"] = {
            "totalUsers": users_count,
            "totalIndications": indications_count,
            "totalCommissions": commissions_count,
            "monthlyCommissions": monthly_commissions,
            "activeAmbassadors": active_ambassadors,
            "activePercentage": round(active_percentage, 1)
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
@app.route("/setup", methods=["POST", "OPTIONS"])
def setup_admin():
    if request.method == "OPTIONS":
        return "", 200
        
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
        "version": "3.3",
        "status": "online",
        "cors_configured": True,
        "gunicorn_compatible": True,
        "endpoints": [
            "/auth/login",
            "/auth/verify",
            "/indications",
            "/commissions",
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


