from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from utils import serialize_firestore_data, safe_jsonify

dashboard_bp = Blueprint('dashboard', __name__)

def get_db():
    """Importa o db do main.py"""
    from main import db
    return db

@dashboard_bp.route("/admin", methods=["GET", "OPTIONS"])
@jwt_required()
def admin_dashboard():
    if request.method == "OPTIONS":
        return "", 200
        
    try:
        db = get_db()
        if not db:
            return safe_jsonify({"error": "Erro de conexão com banco de dados"}, 500)
            
        current_user_id = get_jwt_identity()
        user_doc = db.collection("users").document(current_user_id).get()

        if not user_doc.exists:
            return safe_jsonify({"error": "Usuário não encontrado"}, 404)
            
        user_data = user_doc.to_dict()
        if user_data["role"] != "admin":
            return safe_jsonify({"error": "Acesso negado"}, 403)

        # Buscar indicações
        indications_ref = db.collection("indications")
        indications = [doc.to_dict() for doc in indications_ref.stream()]
        
        # Buscar parcelas de comissão
        installments_ref = db.collection("commission_installments")
        installments = [doc.to_dict() for doc in installments_ref.stream()]
        
        # Buscar embaixadoras ativas
        users_ref = db.collection("users")
        ambassadors_query = users_ref.where(field_path="role", op_string="==", value="embaixadora")
        active_ambassadors = len([doc.to_dict() for doc in ambassadors_query.stream()])

        # Calcular estatísticas
        total_indications = len(indications)
        approved_indications = len([i for i in indications if i.get("status") == "aprovado"])
        approval_rate = (approved_indications / total_indications * 100) if total_indications > 0 else 0
        
        # Comissões pendentes do mês atual
        current_date = datetime.now()
        monthly_commissions = sum([
            i.get("value", 0) for i in installments 
            if i.get("status") == "pendente" and 
            isinstance(i.get("dueDate"), datetime) and
            i.get("dueDate").month == current_date.month
        ])

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
                    {"month": "Jan", "value": 4500},
                    {"month": "Fev", "value": 5400},
                    {"month": "Mar", "value": 6600},
                    {"month": "Abr", "value": 6000},
                    {"month": "Mai", "value": 7800},
                    {"month": "Jun", "value": 9000}
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
                ],
                "installmentsSummary": {
                    "totalPending": len([i for i in installments if i.get("status") == "pendente"]),
                    "totalPaid": len([i for i in installments if i.get("status") == "pago"]),
                    "totalOverdue": len([i for i in installments if i.get("status") == "atrasado"]),
                    "pendingValue": sum([i.get("value", 0) for i in installments if i.get("status") == "pendente"]),
                    "paidValue": sum([i.get("value", 0) for i in installments if i.get("status") == "pago"])
                }
            }
        }

        return safe_jsonify(dashboard_data, 200)

    except Exception as e:
        print(f"Erro no dashboard admin: {str(e)}")
        return safe_jsonify({"error": "Erro interno do servidor"}, 500)

@dashboard_bp.route("/ambassador", methods=["GET", "OPTIONS"])
@jwt_required()
def ambassador_dashboard():
    if request.method == "OPTIONS":
        return "", 200
        
    try:
        db = get_db()
        if not db:
            return safe_jsonify({"error": "Erro de conexão com banco de dados"}, 500)
            
        current_user_id = get_jwt_identity()
        user_doc = db.collection("users").document(current_user_id).get()

        if not user_doc.exists:
            return safe_jsonify({"error": "Usuário não encontrado"}, 404)
            
        user_data = user_doc.to_dict()
        if user_data["role"] != "embaixadora":
            return safe_jsonify({"error": "Acesso negado"}, 403)

        # Buscar indicações da embaixadora
        indications_ref = db.collection("indications")
        user_indications_query = indications_ref.where(field_path="ambassadorId", op_string="==", value=current_user_id)
        user_indications = [doc.to_dict() for doc in user_indications_query.stream()]
        
        # Buscar parcelas de comissão da embaixadora
        installments_ref = db.collection("commission_installments")
        user_installments_query = installments_ref.where(field_path="ambassadorId", op_string="==", value=current_user_id)
        user_installments = [doc.to_dict() for doc in user_installments_query.stream()]
        
        total_indications = len(user_indications)
        approved_sales = len([i for i in user_indications if i.get("status") == "aprovado"])
        
        # Comissão do mês atual (parcelas pendentes e pagas do mês)
        current_date = datetime.now()
        current_month_commission = sum([
            i.get("value", 0) for i in user_installments 
            if isinstance(i.get("dueDate"), datetime) and
            i.get("dueDate").month == current_date.month
        ])
        
        conversion_rate = (approved_sales / total_indications * 100) if total_indications > 0 else 0

        dashboard_data = {
            "stats": {
                "total_indications": total_indications,
                "approved_sales": approved_sales,
                "current_month_commission": current_month_commission,
                "conversion_rate": conversion_rate
            },
            "monthly_commissions": [
                {"month": "Jan", "total": 900.00},
                {"month": "Fev", "total": 1200.00},
                {"month": "Mar", "total": 1800.00},
                {"month": "Abr", "total": 1500.00},
                {"month": "Mai", "total": 2100.00},
                {"month": "Jun", "total": current_month_commission}
            ],
            "niche_stats": [
                {"niche": "Geral", "count": 10, "percent": 0.4},
                {"niche": "Premium", "count": 8, "percent": 0.32},
                {"niche": "Corporativo", "count": 5, "percent": 0.2},
                {"niche": "Startup", "count": 2, "percent": 0.08}
            ],
            "installments_summary": {
                "totalExpected": len(user_installments),
                "totalPaid": len([i for i in user_installments if i.get("status") == "pago"]),
                "totalPending": len([i for i in user_installments if i.get("status") == "pendente"]),
                "expectedValue": sum([i.get("value", 0) for i in user_installments]),
                "paidValue": sum([i.get("value", 0) for i in user_installments if i.get("status") == "pago"]),
                "pendingValue": sum([i.get("value", 0) for i in user_installments if i.get("status") == "pendente"])
            }
        }

        return safe_jsonify(dashboard_data, 200)

    except Exception as e:
        print(f"Erro no dashboard embaixadora: {str(e)}")
        return safe_jsonify({"error": "Erro interno do servidor"}, 500)

