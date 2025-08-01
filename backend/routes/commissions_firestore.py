from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from models import CommissionInstallmentModel, create_commission_installments, get_installment_summary
from utils import serialize_firestore_data, safe_jsonify
from google.cloud.firestore_v1._helpers import TimestampWithNanoseconds

commissions_bp = Blueprint('commissions', __name__)

def get_db():
    from main import db
    return db

@commissions_bp.route('/installments', methods=['GET', 'OPTIONS'])
@jwt_required()
def get_installments():
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

        installments_ref = db.collection("commission_installments")
        if user_data["role"] == "admin":
            query = installments_ref
        else:
            query = installments_ref.where("ambassadorId", "==", current_user_id)

        status_filter = request.args.get('status')
        ambassador_filter = request.args.get('ambassador')
        month_filter = request.args.get('month')
        year_filter = request.args.get('year')

        if status_filter:
            query = query.where("status", "==", status_filter)

        if ambassador_filter and user_data["role"] == "admin":
            query = query.where("ambassadorId", "==", ambassador_filter)

        docs = query.stream()
        installments = []

        for doc in docs:
            installment_data = doc.to_dict()
            installment_data["id"] = doc.id
            installment_data = serialize_firestore_data(installment_data)

            if month_filter or year_filter:
                due_date = installment_data.get('dueDate')
                if due_date:
                    if isinstance(due_date, str):
                        try:
                            due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                        except:
                            continue
                    if month_filter and due_date.month != int(month_filter):
                        continue
                    if year_filter and due_date.year != int(year_filter):
                        continue

            installments.append(installment_data)

        return safe_jsonify(installments, 200)

    except Exception as e:
        print(f"Erro ao buscar parcelas: {str(e)}")
        return safe_jsonify({"error": str(e)}, 500)

@commissions_bp.route('/installments/<installment_id>/status', methods=['PUT', 'OPTIONS'])
@jwt_required()
def update_installment_status(installment_id):
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

        data = request.get_json()
        new_status = data.get("status")

        if new_status not in CommissionInstallmentModel.VALID_STATUSES:
            return safe_jsonify({
                "error": f"Status inválido. Use um dos seguintes: {', '.join(CommissionInstallmentModel.VALID_STATUSES)}"
            }, 400)

        installment_doc = db.collection("commission_installments").document(installment_id).get()
        if not installment_doc.exists:
            return safe_jsonify({"error": "Parcela não encontrada"}, 404)

        update_data = {
            "status": new_status,
            "updatedAt": datetime.now()
        }

        if new_status == "pago":
            update_data["paymentDate"] = datetime.now()

        db.collection("commission_installments").document(installment_id).update(update_data)

        return safe_jsonify({"message": "Status da parcela atualizado com sucesso"}, 200)

    except Exception as e:
        print(f"Erro ao atualizar status da parcela: {str(e)}")
        return safe_jsonify({"error": str(e)}, 500)

@commissions_bp.route('/installments/summary', methods=['GET', 'OPTIONS'])
@jwt_required()
def get_installments_summary():
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

        installments_ref = db.collection("commission_installments")
        if user_data["role"] == "admin":
            query = installments_ref
        else:
            query = installments_ref.where("ambassadorId", "==", current_user_id)

        docs = query.stream()

        total_installments = 0
        pending_installments = 0
        paid_installments = 0
        overdue_installments = 0
        total_pending_value = 0.0
        total_paid_value = 0.0
        total_overdue_value = 0.0

        current_date = datetime.now()

        for doc in docs:
            installment_data = doc.to_dict()
            total_installments += 1
            status = installment_data.get('status', 'pendente')
            value = installment_data.get('value', 0.0)
            due_date = installment_data.get('dueDate')

            if isinstance(due_date, TimestampWithNanoseconds):
                due_date = due_date.replace(tzinfo=None)

            if status == 'pago':
                paid_installments += 1
                total_paid_value += value
            elif status == 'pendente':
                if due_date and due_date < current_date:
                    overdue_installments += 1
                    total_overdue_value += value
                else:
                    pending_installments += 1
                    total_pending_value += value
            elif status == 'atrasado':
                overdue_installments += 1
                total_overdue_value += value

        summary = {
            'total_installments': total_installments,
            'pending_installments': pending_installments,
            'paid_installments': paid_installments,
            'overdue_installments': overdue_installments,
            'total_pending_value': total_pending_value,
            'total_paid_value': total_paid_value,
            'total_overdue_value': total_overdue_value
        }

        return safe_jsonify(summary, 200)

    except Exception as e:
        print(f"Erro ao buscar resumo das parcelas: {str(e)}")
        return safe_jsonify({"error": str(e)}, 500)

@commissions_bp.route('/installments/create-for-indication', methods=['POST', 'OPTIONS'])
@jwt_required()
def create_installments_for_indication():
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

        data = request.get_json()
        indication_id = data.get("indication_id")

        if not indication_id:
            return safe_jsonify({"error": "ID da indicação é obrigatório"}, 400)

        indication_doc = db.collection("indications").document(indication_id).get()
        if not indication_doc.exists:
            return safe_jsonify({"error": "Indicação não encontrada"}, 404)

        indication_data = indication_doc.to_dict()

        ambassador_id = indication_data.get("ambassadorId")
        ambassador_doc = db.collection("users").document(ambassador_id).get()
        if not ambassador_doc.exists:
            return safe_jsonify({"error": "Embaixadora não encontrada"}, 404)

        ambassador_data = ambassador_doc.to_dict()

        existing_query = db.collection("commission_installments").where(
            "indicationId", "==", indication_id
        )
        existing_docs = list(existing_query.stream())

        if existing_docs:
            return safe_jsonify({"error": "Parcelas já existem para esta indicação"}, 400)

        indication_date = indication_data.get('createdAt', datetime.now())
        if isinstance(indication_date, TimestampWithNanoseconds):
            indication_date = indication_date.replace(tzinfo=None)
        elif not isinstance(indication_date, datetime):
            indication_date = datetime.now()

        installments_data = create_commission_installments(
            indication_id=indication_id,
            ambassador_id=ambassador_id,
            ambassador_name=ambassador_data.get('name', 'Nome não informado'),
            client_name=indication_data.get('client_name', 'Cliente não informado'),
            indication_date=indication_date
        )

        created_installments = []
        for installment_data in installments_data:
            doc_ref = db.collection("commission_installments").add(installment_data)
            installment_data["id"] = doc_ref[1].id
            created_installments.append(serialize_firestore_data(installment_data))

        return safe_jsonify({
            "message": "Parcelas criadas com sucesso",
            "installments": created_installments
        }, 201)

    except Exception as e:
        print(f"Erro ao criar parcelas: {str(e)}")
        return safe_jsonify({"error": str(e)}, 500)
