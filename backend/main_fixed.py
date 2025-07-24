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

# Health check
@app.route("/health", methods=["GET"])
def health_check():
    return safe_jsonify({
        "status": "healthy",
        "service": "beepy-api",
        "firebase_connected": db is not None,
        "cors_configured": True,
        "gunicorn_compatible": True
    })

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
        docs = query.stream()

        user_doc = None
        for doc in docs:
            user_doc = doc
            break

        if not user_doc:
            return safe_jsonify({"error": "Credenciais inválidas"}, 401)

        user_data = user_doc.to_dict()

        # Verificar senha
        if not bcrypt.checkpw(password.encode("utf-8"), user_data["password"].encode("utf-8")):
            return safe_jsonify({"error": "Credenciais inválidas"}, 401)

        # Verificar se usuário está ativo
        if not user_data.get("active", True):
            return safe_jsonify({"error": "Usuário inativo"}, 401)

        # Criar token JWT
        access_token = create_access_token(identity=user_doc.id)

        # Preparar dados do usuário para resposta
        user_response = {
            "id": user_doc.id,
            "name": user_data.get("name"),
            "email": user_data.get("email"),
            "role": user_data.get("role"),
            "phone": user_data.get("phone"),
            "active": user_data.get("active", True)
        }

        return safe_jsonify({
            "message": "Login realizado com sucesso",
            "access_token": access_token,
            "user": user_response
        })

    except Exception as e:
        print(f"Erro no login: {str(e)}")
        return safe_jsonify({"error": "Erro interno do servidor"}, 500)

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
                "name": user_data.get("name"),
                "email": user_data.get("email"),
                "role": user_data.get("role"),
                "phone": user_data.get("phone"),
                "active": user_data.get("active", True)
            }
        }

        return safe_jsonify(response_data)

    except Exception as e:
        print(f"Erro na verificação do token: {str(e)}")
        return safe_jsonify({"error": "Token inválido"}, 401)

# Dashboard endpoints
@app.route("/dashboard/admin", methods=["GET", "OPTIONS"])
@jwt_required()
def admin_dashboard():
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
        if user_data.get("role") != "admin":
            return safe_jsonify({"error": "Acesso negado"}, 403)

        # Dados mockados para demonstração
        dashboard_data = {
            "stats": {
                "monthlyCommissions": 15000.00,
                "approvalRate": 75.5,
                "totalIndications": 150,
                "activeAmbassadors": 12
            },
            "charts": {
                "indicationsMonthly": [
                    {"month": "Jan", "count": 20},
                    {"month": "Fev", "count": 25},
                    {"month": "Mar", "count": 30},
                    {"month": "Abr", "count": 28},
                    {"month": "Mai", "count": 35},
                    {"month": "Jun", "count": 40}
                ],
                "salesMonthly": [
                    {"month": "Jan", "value": 15},
                    {"month": "Fev", "value": 18},
                    {"month": "Mar", "value": 22},
                    {"month": "Abr", "value": 20},
                    {"month": "Mai", "value": 26},
                    {"month": "Jun", "value": 30}
                ],
                "conversionBySegment": [
                    {"segment": "Geral", "converted": 45, "rate": 75.0},
                    {"segment": "Premium", "converted": 30, "rate": 85.7},
                    {"segment": "Corporativo", "converted": 25, "rate": 83.3},
                    {"segment": "Startup", "converted": 20, "rate": 66.7}
                ],
                "topAmbassadors": [
                    {"name": "Maria Silva", "indications": 25},
                    {"name": "Ana Costa", "indications": 22},
                    {"name": "Julia Santos", "indications": 18},
                    {"name": "Carla Oliveira", "indications": 15},
                    {"name": "Fernanda Lima", "indications": 12}
                ]
            }
        }

        return safe_jsonify(dashboard_data)

    except Exception as e:
        print(f"Erro no dashboard admin: {str(e)}")
        return safe_jsonify({"error": "Erro interno do servidor"}, 500)

@app.route("/dashboard/ambassador", methods=["GET", "OPTIONS"])
@jwt_required()
def ambassador_dashboard():
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
        if user_data.get("role") != "ambassador":
            return safe_jsonify({"error": "Acesso negado"}, 403)

        # Dados mockados para demonstração
        dashboard_data = {
            "stats": {
                "total_indications": 25,
                "approved_sales": 18,
                "current_month_commission": 2500.00,
                "conversion_rate": 72.0
            },
            "monthly_commissions": [
                {"month": "Jan", "total": 1800.00},
                {"month": "Fev", "total": 2200.00},
                {"month": "Mar", "total": 2800.00},
                {"month": "Abr", "total": 2400.00},
                {"month": "Mai", "total": 3200.00},
                {"month": "Jun", "total": 2500.00}
            ],
            "niche_stats": [
                {"niche": "Geral", "count": 10, "percent": 0.4},
                {"niche": "Premium", "count": 8, "percent": 0.32},
                {"niche": "Corporativo", "count": 5, "percent": 0.2},
                {"niche": "Startup", "count": 2, "percent": 0.08}
            ]
        }

        return safe_jsonify(dashboard_data)

    except Exception as e:
        print(f"Erro no dashboard embaixadora: {str(e)}")
        return safe_jsonify({"error": "Erro interno do servidor"}, 500)

# Indicações endpoints
@app.route("/indications", methods=["GET", "POST", "OPTIONS"])
@jwt_required()
def indications():
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

        if request.method == "GET":
            # Dados mockados para demonstração
            indications_data = [
                {
                    "id": "1",
                    "client_name": "João Silva",
                    "clientName": "João Silva",
                    "email": "joao@email.com",
                    "clientEmail": "joao@email.com",
                    "phone": "(11) 99999-9999",
                    "origin": "instagram",
                    "segment": "geral",
                    "status": "agendado",
                    "createdAt": "2025-07-20T10:00:00Z",
                    "created_at": "2025-07-20T10:00:00Z",
                    "ambassadorName": "Maria Silva" if user_data.get("role") == "admin" else None
                },
                {
                    "id": "2",
                    "client_name": "Ana Costa",
                    "clientName": "Ana Costa",
                    "email": "ana@email.com",
                    "clientEmail": "ana@email.com",
                    "phone": "(11) 88888-8888",
                    "origin": "website",
                    "segment": "premium",
                    "status": "aprovado",
                    "createdAt": "2025-07-19T14:30:00Z",
                    "created_at": "2025-07-19T14:30:00Z",
                    "ambassadorName": "Maria Silva" if user_data.get("role") == "admin" else None
                }
            ]
            
            return safe_jsonify(indications_data)

        elif request.method == "POST":
            data = request.get_json()
            if not data:
                return safe_jsonify({"error": "Dados não fornecidos"}, 400)

            # Validar campos obrigatórios
            required_fields = ["client_name", "email", "phone"]
            for field in required_fields:
                if not data.get(field):
                    return safe_jsonify({"error": f"Campo {field} é obrigatório"}, 400)

            # Simular criação da indicação
            new_indication = {
                "id": "new_" + str(datetime.now().timestamp()),
                "client_name": data["client_name"],
                "email": data["email"],
                "phone": data["phone"],
                "origin": data.get("origin", "website"),
                "segment": data.get("segment", "geral"),
                "status": "agendado",
                "ambassador_id": current_user_id,
                "created_at": datetime.now().isoformat()
            }

            return safe_jsonify({"message": "Indicação criada com sucesso", "indication": new_indication}, 201)

    except Exception as e:
        print(f"Erro nas indicações: {str(e)}")
        return safe_jsonify({"error": "Erro interno do servidor"}, 500)

@app.route("/indications/<indication_id>/status", methods=["PUT", "OPTIONS"])
@jwt_required()
def update_indication_status(indication_id):
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
        if user_data.get("role") != "admin":
            return safe_jsonify({"error": "Acesso negado"}, 403)

        data = request.get_json()
        if not data or "status" not in data:
            return safe_jsonify({"error": "Status é obrigatório"}, 400)

        # Simular atualização
        return safe_jsonify({"message": "Status atualizado com sucesso"})

    except Exception as e:
        print(f"Erro ao atualizar status: {str(e)}")
        return safe_jsonify({"error": "Erro interno do servidor"}, 500)

# Comissões endpoints
@app.route("/commissions", methods=["GET", "OPTIONS"])
@jwt_required()
def commissions():
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

        # Dados mockados para demonstração
        commissions_data = [
            {
                "id": "1",
                "clientName": "João Silva",
                "ambassadorName": "Maria Silva" if user_data.get("role") == "admin" else None,
                "value": 500.00,
                "amount": 500.00,
                "status": "pendente",
                "payment_status": "pendente",
                "createdAt": "2025-07-20T10:00:00Z",
                "created_at": "2025-07-20T10:00:00Z"
            },
            {
                "id": "2",
                "clientName": "Ana Costa",
                "ambassadorName": "Maria Silva" if user_data.get("role") == "admin" else None,
                "value": 750.00,
                "amount": 750.00,
                "status": "pago",
                "payment_status": "pago",
                "createdAt": "2025-07-19T14:30:00Z",
                "created_at": "2025-07-19T14:30:00Z"
            }
        ]
        
        return safe_jsonify(commissions_data)

    except Exception as e:
        print(f"Erro nas comissões: {str(e)}")
        return safe_jsonify({"error": "Erro interno do servidor"}, 500)

@app.route("/commissions/<commission_id>", methods=["PUT", "OPTIONS"])
@jwt_required()
def update_commission(commission_id):
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
        if user_data.get("role") != "admin":
            return safe_jsonify({"error": "Acesso negado"}, 403)

        data = request.get_json()
        if not data:
            return safe_jsonify({"error": "Dados não fornecidos"}, 400)

        # Simular atualização
        return safe_jsonify({"message": "Comissão atualizada com sucesso"})

    except Exception as e:
        print(f"Erro ao atualizar comissão: {str(e)}")
        return safe_jsonify({"error": "Erro interno do servidor"}, 500)

# Para desenvolvimento local
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"Iniciando servidor na porta {port}")
    app.run(host="0.0.0.0", port=port, debug=True)

