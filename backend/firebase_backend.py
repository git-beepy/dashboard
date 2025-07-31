import os
import bcrypt
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
SECRET_KEY = "dev-secret-key-change-in-production"
JWT_SECRET_KEY = "jwt-secret-key-change-in-production"

# Inicializar Firebase
try:
    cred_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'firebase_credentials.json')
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
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

# Configurar CORS
allowed_origins = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:3001').split(',')
CORS(app, supports_credentials=True, resources={r"/*": {"origins": allowed_origins}})

# Health check
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "beepy-api-firebase",
        "firebase_connected": db is not None,
        "cors_configured": True
    })

# Função para criar usuários padrão se não existirem
def create_default_users():
    if not db:
        return
    
    try:
        # Verificar se usuários já existem
        users_ref = db.collection('users')
        admin_doc = users_ref.document('admin').get()
        
        if not admin_doc.exists:
            # Criar usuário admin
            admin_data = {
                "id": "admin",
                "name": "Administrador",
                "email": "admin@beepy.com",
                "password": bcrypt.hashpw("admin123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
                "role": "admin",
                "phone": "(11) 99999-9999",
                "active": True,
                "created_at": datetime.now()
            }
            users_ref.document('admin').set(admin_data)
            print("Usuário admin criado")
        
        ambassador_doc = users_ref.document('ambassador').get()
        if not ambassador_doc.exists:
            # Criar usuário embaixadora
            ambassador_data = {
                "id": "ambassador",
                "name": "Maria Silva",
                "email": "maria@beepy.com",
                "password": bcrypt.hashpw("maria123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
                "role": "ambassador",
                "phone": "(11) 88888-8888",
                "active": True,
                "created_at": datetime.now()
            }
            users_ref.document('ambassador').set(ambassador_data)
            print("Usuário embaixadora criado")
            
        # Criar algumas indicações de exemplo
        indications_ref = db.collection('indications')
        indication1_doc = indications_ref.document('1').get()
        
        if not indication1_doc.exists:
            indication1_data = {
                "id": "1",
                "client_name": "João Silva",
                "email": "joao@email.com",
                "phone": "(11) 99999-9999",
                "origin": "instagram",
                "segment": "geral",
                "status": "agendado",
                "ambassador_id": "ambassador",
                "ambassador_name": "Maria Silva",
                "created_at": datetime.now()
            }
            indications_ref.document('1').set(indication1_data)
            
            indication2_data = {
                "id": "2",
                "client_name": "Ana Costa",
                "email": "ana@email.com",
                "phone": "(11) 88888-8888",
                "origin": "website",
                "segment": "premium",
                "status": "aprovado",
                "ambassador_id": "ambassador",
                "ambassador_name": "Maria Silva",
                "created_at": datetime.now()
            }
            indications_ref.document('2').set(indication2_data)
            print("Indicações de exemplo criadas")
            
        # Criar algumas comissões de exemplo
        commissions_ref = db.collection('commissions')
        commission1_doc = commissions_ref.document('1').get()
        
        if not commission1_doc.exists:
            commission1_data = {
                "id": "1",
                "client_name": "João Silva",
                "ambassador_id": "ambassador",
                "ambassador_name": "Maria Silva",
                "amount": 500.00,
                "status": "pendente",
                "created_at": datetime.now()
            }
            commissions_ref.document('1').set(commission1_data)
            
            commission2_data = {
                "id": "2",
                "client_name": "Ana Costa",
                "ambassador_id": "ambassador",
                "ambassador_name": "Maria Silva",
                "amount": 750.00,
                "status": "pago",
                "created_at": datetime.now()
            }
            commissions_ref.document('2').set(commission2_data)
            print("Comissões de exemplo criadas")
            
    except Exception as e:
        print(f"Erro ao criar dados padrão: {e}")

# Rotas de autenticação
@app.route("/auth/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return "", 200
    
    try:
        if not db:
            return jsonify({"error": "Banco de dados não disponível"}), 500
            
        data = request.get_json()
        if not data:
            return jsonify({"error": "Dados não fornecidos"}), 400

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email e senha são obrigatórios"}), 400

        # Buscar usuário no Firebase
        users_ref = db.collection('users')
        query = users_ref.where('email', '==', email).limit(1)
        docs = query.stream()
        
        user = None
        user_id = None
        for doc in docs:
            user = doc.to_dict()
            user_id = doc.id
            break

        if not user:
            return jsonify({"error": "Credenciais inválidas"}), 401

        # Verificar senha
        if not bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
            return jsonify({"error": "Credenciais inválidas"}), 401

        # Criar token JWT
        access_token = create_access_token(identity=user_id)

        # Preparar dados do usuário para resposta
        user_response = {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "phone": user["phone"],
            "active": user["active"]
        }

        return jsonify({
            "message": "Login realizado com sucesso",
            "access_token": access_token,
            "user": user_response
        })

    except Exception as e:
        print(f"Erro no login: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route("/auth/verify", methods=["GET", "OPTIONS"])
@jwt_required()
def verify_token():
    if request.method == "OPTIONS":
        return "", 200
        
    try:
        if not db:
            return jsonify({"error": "Banco de dados não disponível"}), 500
            
        current_user_id = get_jwt_identity()
        user_doc = db.collection('users').document(current_user_id).get()

        if not user_doc.exists:
            return jsonify({"error": "Usuário não encontrado"}), 404

        user = user_doc.to_dict()
        response_data = {
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"],
                "phone": user["phone"],
                "active": user["active"]
            }
        }

        return jsonify(response_data)

    except Exception as e:
        print(f"Erro na verificação do token: {str(e)}")
        return jsonify({"error": "Token inválido"}), 401

# Dashboard endpoints
@app.route("/dashboard/admin", methods=["GET", "OPTIONS"])
@jwt_required()
def admin_dashboard():
    if request.method == "OPTIONS":
        return "", 200
        
    try:
        if not db:
            return jsonify({"error": "Banco de dados não disponível"}), 500
            
        current_user_id = get_jwt_identity()
        user_doc = db.collection('users').document(current_user_id).get()

        if not user_doc.exists:
            return jsonify({"error": "Usuário não encontrado"}), 404
            
        user = user_doc.to_dict()
        if user["role"] != "admin":
            return jsonify({"error": "Acesso negado"}), 403

        # Buscar indicações
        indications_ref = db.collection('indications')
        indications = [doc.to_dict() for doc in indications_ref.stream()]
        
        # Buscar comissões
        commissions_ref = db.collection('commissions')
        commissions = [doc.to_dict() for doc in commissions_ref.stream()]
        
        # Buscar embaixadoras ativas
        users_ref = db.collection('users')
        ambassadors_query = users_ref.where('role', '==', 'ambassador').where('active', '==', True)
        active_ambassadors = len([doc.to_dict() for doc in ambassadors_query.stream()])

        # Calcular estatísticas
        total_indications = len(indications)
        approved_indications = len([i for i in indications if i["status"] == "aprovado"])
        approval_rate = (approved_indications / total_indications * 100) if total_indications > 0 else 0
        monthly_commissions = sum([c["amount"] for c in commissions if c["status"] == "pendente"])

        dashboard_data = {
            "stats": {
                "monthlyCommissions": monthly_commissions,
                "approvalRate": approval_rate,
                "totalIndications": total_indications,
                "activeAmbassadors": active_ambassadors
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

        return jsonify(dashboard_data)

    except Exception as e:
        print(f"Erro no dashboard admin: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route("/dashboard/ambassador", methods=["GET", "OPTIONS"])
@jwt_required()
def ambassador_dashboard():
    if request.method == "OPTIONS":
        return "", 200
        
    try:
        if not db:
            return jsonify({"error": "Banco de dados não disponível"}), 500
            
        current_user_id = get_jwt_identity()
        user_doc = db.collection('users').document(current_user_id).get()

        if not user_doc.exists:
            return jsonify({"error": "Usuário não encontrado"}), 404
            
        user = user_doc.to_dict()
        if user["role"] != "ambassador":
            return jsonify({"error": "Acesso negado"}), 403

        # Buscar indicações da embaixadora
        indications_ref = db.collection('indications')
        user_indications_query = indications_ref.where('ambassador_id', '==', current_user_id)
        user_indications = [doc.to_dict() for doc in user_indications_query.stream()]
        
        # Buscar comissões da embaixadora
        commissions_ref = db.collection('commissions')
        user_commissions_query = commissions_ref.where('ambassador_id', '==', current_user_id)
        user_commissions = [doc.to_dict() for doc in user_commissions_query.stream()]
        
        total_indications = len(user_indications)
        approved_sales = len([i for i in user_indications if i["status"] == "aprovado"])
        current_month_commission = sum([c["amount"] for c in user_commissions if c["status"] == "pendente"])
        conversion_rate = (approved_sales / total_indications * 100) if total_indications > 0 else 0

        dashboard_data = {
            "stats": {
                "total_indications": total_indications,
                "approved_sales": approved_sales,
                "current_month_commission": current_month_commission,
                "conversion_rate": conversion_rate
            },
            "monthly_commissions": [
                {"month": "Jan", "total": 1800.00},
                {"month": "Fev", "total": 2200.00},
                {"month": "Mar", "total": 2800.00},
                {"month": "Abr", "total": 2400.00},
                {"month": "Mai", "total": 3200.00},
                {"month": "Jun", "total": current_month_commission}
            ],
            "niche_stats": [
                {"niche": "Geral", "count": 10, "percent": 0.4},
                {"niche": "Premium", "count": 8, "percent": 0.32},
                {"niche": "Corporativo", "count": 5, "percent": 0.2},
                {"niche": "Startup", "count": 2, "percent": 0.08}
            ]
        }

        return jsonify(dashboard_data)

    except Exception as e:
        print(f"Erro no dashboard embaixadora: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

# Indicações endpoints
@app.route("/indications", methods=["GET", "POST", "OPTIONS"])
@jwt_required()
def indications():
    if request.method == "OPTIONS":
        return "", 200
        
    try:
        if not db:
            return jsonify({"error": "Banco de dados não disponível"}), 500
            
        current_user_id = get_jwt_identity()
        user_doc = db.collection('users').document(current_user_id).get()

        if not user_doc.exists:
            return jsonify({"error": "Usuário não encontrado"}), 404
            
        user = user_doc.to_dict()

        if request.method == "GET":
            # Buscar indicações
            indications_ref = db.collection('indications')
            
            if user["role"] == "admin":
                indications_query = indications_ref
            else:
                indications_query = indications_ref.where('ambassador_id', '==', current_user_id)
            
            indications = [doc.to_dict() for doc in indications_query.stream()]
            
            # Formatar dados para compatibilidade
            formatted_indications = []
            for indication in indications:
                formatted_indication = {
                    "id": indication["id"],
                    "client_name": indication["client_name"],
                    "clientName": indication["client_name"],
                    "email": indication["email"],
                    "clientEmail": indication["email"],
                    "phone": indication["phone"],
                    "origin": indication["origin"],
                    "segment": indication["segment"],
                    "status": indication["status"],
                    "createdAt": indication["created_at"].isoformat() if hasattr(indication["created_at"], 'isoformat') else str(indication["created_at"]),
                    "created_at": indication["created_at"].isoformat() if hasattr(indication["created_at"], 'isoformat') else str(indication["created_at"])
                }
                if user["role"] == "admin":
                    formatted_indication["ambassadorName"] = indication["ambassador_name"]
                formatted_indications.append(formatted_indication)
            
            return jsonify(formatted_indications)

        elif request.method == "POST":
            data = request.get_json()
            if not data:
                return jsonify({"error": "Dados não fornecidos"}), 400

            # Validar campos obrigatórios
            required_fields = ["client_name", "email", "phone"]
            for field in required_fields:
                if not data.get(field):
                    return jsonify({"error": f"Campo {field} é obrigatório"}), 400

            # Gerar novo ID
            indications_ref = db.collection('indications')
            new_doc_ref = indications_ref.document()
            new_id = new_doc_ref.id

            # Criar nova indicação
            new_indication = {
                "id": new_id,
                "client_name": data["client_name"],
                "email": data["email"],
                "phone": data["phone"],
                "origin": data.get("origin", "website"),
                "segment": data.get("segment", "geral"),
                "status": "agendado",
                "ambassador_id": current_user_id,
                "ambassador_name": user["name"],
                "created_at": datetime.now()
            }

            new_doc_ref.set(new_indication)

            return jsonify({"message": "Indicação criada com sucesso", "indication": new_indication}), 201

    except Exception as e:
        print(f"Erro nas indicações: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route("/indications/<indication_id>/status", methods=["PUT", "OPTIONS"])
@jwt_required()
def update_indication_status(indication_id):
    if request.method == "OPTIONS":
        return "", 200
        
    try:
        if not db:
            return jsonify({"error": "Banco de dados não disponível"}), 500
            
        current_user_id = get_jwt_identity()
        user_doc = db.collection('users').document(current_user_id).get()

        if not user_doc.exists:
            return jsonify({"error": "Usuário não encontrado"}), 404
            
        user = user_doc.to_dict()
        if user["role"] != "admin":
            return jsonify({"error": "Acesso negado"}), 403

        data = request.get_json()
        if not data or "status" not in data:
            return jsonify({"error": "Status é obrigatório"}), 400

        # Encontrar e atualizar indicação
        indication_doc = db.collection('indications').document(indication_id).get()
        if not indication_doc.exists:
            return jsonify({"error": "Indicação não encontrada"}), 404
            
        indication = indication_doc.to_dict()
        
        # Atualizar status
        db.collection('indications').document(indication_id).update({
            "status": data["status"]
        })
        
        # Se aprovado, criar comissão
        if data["status"] == "aprovado":
            commissions_ref = db.collection('commissions')
            new_commission_ref = commissions_ref.document()
            
            new_commission = {
                "id": new_commission_ref.id,
                "client_name": indication["client_name"],
                "ambassador_id": indication["ambassador_id"],
                "ambassador_name": indication["ambassador_name"],
                "amount": 500.00,  # Valor fixo para demonstração
                "status": "pendente",
                "created_at": datetime.now()
            }
            new_commission_ref.set(new_commission)
        
        return jsonify({"message": "Status atualizado com sucesso"})

    except Exception as e:
        print(f"Erro ao atualizar status: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

# Comissões endpoints
@app.route("/commissions", methods=["GET", "OPTIONS"])
@jwt_required()
def commissions():
    if request.method == "OPTIONS":
        return "", 200
        
    try:
        if not db:
            return jsonify({"error": "Banco de dados não disponível"}), 500
            
        current_user_id = get_jwt_identity()
        user_doc = db.collection('users').document(current_user_id).get()

        if not user_doc.exists:
            return jsonify({"error": "Usuário não encontrado"}), 404
            
        user = user_doc.to_dict()

        # Buscar comissões
        commissions_ref = db.collection('commissions')
        
        if user["role"] == "admin":
            commissions_query = commissions_ref
        else:
            commissions_query = commissions_ref.where('ambassador_id', '==', current_user_id)
        
        commissions = [doc.to_dict() for doc in commissions_query.stream()]
        
        # Formatar dados para compatibilidade
        formatted_commissions = []
        for commission in commissions:
            formatted_commission = {
                "id": commission["id"],
                "clientName": commission["client_name"],
                "value": commission["amount"],
                "amount": commission["amount"],
                "status": commission["status"],
                "payment_status": commission["status"],
                "createdAt": commission["created_at"].isoformat() if hasattr(commission["created_at"], 'isoformat') else str(commission["created_at"]),
                "created_at": commission["created_at"].isoformat() if hasattr(commission["created_at"], 'isoformat') else str(commission["created_at"])
            }
            if user["role"] == "admin":
                formatted_commission["ambassadorName"] = commission["ambassador_name"]
            formatted_commissions.append(formatted_commission)
        
        return jsonify(formatted_commissions)

    except Exception as e:
        print(f"Erro nas comissões: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

@app.route("/commissions/<commission_id>", methods=["PUT", "OPTIONS"])
@jwt_required()
def update_commission(commission_id):
    if request.method == "OPTIONS":
        return "", 200
        
    try:
        if not db:
            return jsonify({"error": "Banco de dados não disponível"}), 500
            
        current_user_id = get_jwt_identity()
        user_doc = db.collection('users').document(current_user_id).get()

        if not user_doc.exists:
            return jsonify({"error": "Usuário não encontrado"}), 404
            
        user = user_doc.to_dict()
        if user["role"] != "admin":
            return jsonify({"error": "Acesso negado"}), 403

        data = request.get_json()
        if not data:
            return jsonify({"error": "Dados não fornecidos"}), 400

        # Encontrar e atualizar comissão
        commission_doc = db.collection('commissions').document(commission_id).get()
        if not commission_doc.exists:
            return jsonify({"error": "Comissão não encontrada"}), 404
            
        update_data = {}
        if "status" in data:
            update_data["status"] = data["status"]
            
        db.collection('commissions').document(commission_id).update(update_data)
        
        return jsonify({"message": "Comissão atualizada com sucesso"})

    except Exception as e:
        print(f"Erro ao atualizar comissão: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

# Para desenvolvimento local
if __name__ == "__main__":
    # Criar dados padrão se necessário
    create_default_users()
    
    port = int(os.environ.get("PORT", 10003))
    print(f"Iniciando servidor Firebase na porta {port}")
    app.run(host="0.0.0.0", port=port, debug=True)

