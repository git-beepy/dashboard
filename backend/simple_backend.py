import os
import bcrypt
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

# Configurações
SECRET_KEY = "dev-secret-key-change-in-production"
JWT_SECRET_KEY = "jwt-secret-key-change-in-production"

# Dados mockados em memória
users_db = {
    "admin": {
        "id": "admin",
        "name": "Administrador",
        "email": "admin@beepy.com",
        "password": bcrypt.hashpw("admin123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
        "role": "admin",
        "phone": "(11) 99999-9999",
        "active": True
    },
    "ambassador": {
        "id": "ambassador",
        "name": "Maria Silva",
        "email": "maria@beepy.com",
        "password": bcrypt.hashpw("maria123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
        "role": "ambassador",
        "phone": "(11) 88888-8888",
        "active": True
    }
}

indications_db = [
    {
        "id": "1",
        "client_name": "João Silva",
        "email": "joao@email.com",
        "phone": "(11) 99999-9999",
        "origin": "instagram",
        "segment": "geral",
        "status": "agendado",
        "ambassador_id": "ambassador",
        "ambassador_name": "Maria Silva",
        "created_at": "2025-07-20T10:00:00Z"
    },
    {
        "id": "2",
        "client_name": "Ana Costa",
        "email": "ana@email.com",
        "phone": "(11) 88888-8888",
        "origin": "website",
        "segment": "premium",
        "status": "aprovado",
        "ambassador_id": "ambassador",
        "ambassador_name": "Maria Silva",
        "created_at": "2025-07-19T14:30:00Z"
    }
]

commissions_db = [
    {
        "id": "1",
        "client_name": "João Silva",
        "ambassador_id": "ambassador",
        "ambassador_name": "Maria Silva",
        "amount": 500.00,
        "status": "pendente",
        "created_at": "2025-07-20T10:00:00Z"
    },
    {
        "id": "2",
        "client_name": "Ana Costa",
        "ambassador_id": "ambassador",
        "ambassador_name": "Maria Silva",
        "amount": 750.00,
        "status": "pago",
        "created_at": "2025-07-19T14:30:00Z"
    }
]

# Inicializar Flask
app = Flask(__name__)

# Configurações do Flask
app.config["SECRET_KEY"] = SECRET_KEY
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)

# Inicializar JWT
jwt = JWTManager(app)

# Configurar CORS
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

# Health check
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "beepy-api-simple",
        "cors_configured": True
    })

# Rotas de autenticação
@app.route("/auth/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return "", 200
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Dados não fornecidos"}), 400

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email e senha são obrigatórios"}), 400

        # Buscar usuário
        user = None
        user_id = None
        for uid, user_data in users_db.items():
            if user_data["email"] == email:
                user = user_data
                user_id = uid
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
        current_user_id = get_jwt_identity()
        user = users_db.get(current_user_id)

        if not user:
            return jsonify({"error": "Usuário não encontrado"}), 404

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
        current_user_id = get_jwt_identity()
        user = users_db.get(current_user_id)

        if not user or user["role"] != "admin":
            return jsonify({"error": "Acesso negado"}), 403

        # Calcular estatísticas
        total_indications = len(indications_db)
        approved_indications = len([i for i in indications_db if i["status"] == "aprovado"])
        approval_rate = (approved_indications / total_indications * 100) if total_indications > 0 else 0
        monthly_commissions = sum([c["amount"] for c in commissions_db if c["status"] == "pendente"])
        active_ambassadors = len([u for u in users_db.values() if u["role"] == "ambassador" and u["active"]])

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
        current_user_id = get_jwt_identity()
        user = users_db.get(current_user_id)

        if not user or user["role"] != "ambassador":
            return jsonify({"error": "Acesso negado"}), 403

        # Filtrar dados da embaixadora
        user_indications = [i for i in indications_db if i["ambassador_id"] == current_user_id]
        user_commissions = [c for c in commissions_db if c["ambassador_id"] == current_user_id]
        
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
        current_user_id = get_jwt_identity()
        user = users_db.get(current_user_id)

        if not user:
            return jsonify({"error": "Usuário não encontrado"}), 404

        if request.method == "GET":
            # Filtrar indicações baseado no role
            if user["role"] == "admin":
                filtered_indications = indications_db
            else:
                filtered_indications = [i for i in indications_db if i["ambassador_id"] == current_user_id]
            
            # Formatar dados para compatibilidade
            formatted_indications = []
            for indication in filtered_indications:
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
                    "createdAt": indication["created_at"],
                    "created_at": indication["created_at"]
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

            # Criar nova indicação
            new_indication = {
                "id": str(len(indications_db) + 1),
                "client_name": data["client_name"],
                "email": data["email"],
                "phone": data["phone"],
                "origin": data.get("origin", "website"),
                "segment": data.get("segment", "geral"),
                "status": "agendado",
                "ambassador_id": current_user_id,
                "ambassador_name": user["name"],
                "created_at": datetime.now().isoformat()
            }

            indications_db.append(new_indication)

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
        current_user_id = get_jwt_identity()
        user = users_db.get(current_user_id)

        if not user or user["role"] != "admin":
            return jsonify({"error": "Acesso negado"}), 403

        data = request.get_json()
        if not data or "status" not in data:
            return jsonify({"error": "Status é obrigatório"}), 400

        # Encontrar e atualizar indicação
        for indication in indications_db:
            if indication["id"] == indication_id:
                indication["status"] = data["status"]
                
                # Se aprovado, criar comissão
                if data["status"] == "aprovado":
                    new_commission = {
                        "id": str(len(commissions_db) + 1),
                        "client_name": indication["client_name"],
                        "ambassador_id": indication["ambassador_id"],
                        "ambassador_name": indication["ambassador_name"],
                        "amount": 500.00,  # Valor fixo para demonstração
                        "status": "pendente",
                        "created_at": datetime.now().isoformat()
                    }
                    commissions_db.append(new_commission)
                
                return jsonify({"message": "Status atualizado com sucesso"})

        return jsonify({"error": "Indicação não encontrada"}), 404

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
        current_user_id = get_jwt_identity()
        user = users_db.get(current_user_id)

        if not user:
            return jsonify({"error": "Usuário não encontrado"}), 404

        # Filtrar comissões baseado no role
        if user["role"] == "admin":
            filtered_commissions = commissions_db
        else:
            filtered_commissions = [c for c in commissions_db if c["ambassador_id"] == current_user_id]
        
        # Formatar dados para compatibilidade
        formatted_commissions = []
        for commission in filtered_commissions:
            formatted_commission = {
                "id": commission["id"],
                "clientName": commission["client_name"],
                "value": commission["amount"],
                "amount": commission["amount"],
                "status": commission["status"],
                "payment_status": commission["status"],
                "createdAt": commission["created_at"],
                "created_at": commission["created_at"]
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
        current_user_id = get_jwt_identity()
        user = users_db.get(current_user_id)

        if not user or user["role"] != "admin":
            return jsonify({"error": "Acesso negado"}), 403

        data = request.get_json()
        if not data:
            return jsonify({"error": "Dados não fornecidos"}), 400

        # Encontrar e atualizar comissão
        for commission in commissions_db:
            if commission["id"] == commission_id:
                if "status" in data:
                    commission["status"] = data["status"]
                return jsonify({"message": "Comissão atualizada com sucesso"})

        return jsonify({"error": "Comissão não encontrada"}), 404

    except Exception as e:
        print(f"Erro ao atualizar comissão: {str(e)}")
        return jsonify({"error": "Erro interno do servidor"}), 500

# Para desenvolvimento local
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10002))
    print(f"Iniciando servidor simplificado na porta {port}")
    app.run(host="0.0.0.0", port=port, debug=True)

