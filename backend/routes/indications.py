from flask import Blueprint, request, jsonify
from firestore_service import db
from utils import get_collection, generate_id
from commission_utils import create_commission_parcels
from models import Indication
from google.cloud.firestore_v1.base_document import DocumentSnapshot

bp = Blueprint("indications", __name__, url_prefix="/indications")

collection = get_collection("indications")

@bp.route("", methods=["GET"])
def list_indications():
    docs = collection.stream()
    indications = []

    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        indications.append(data)

    return jsonify(indications), 200

@bp.route("", methods=["POST"])
def create_indication():
    data = request.get_json()

    if not data.get("ambassadorId") or not data.get("clientName"):
        return jsonify({"error": "Dados obrigatórios faltando"}), 400

    new_id = generate_id()
    data.update({
        "status": "pendente",
        "createdAt": datetime.now(),
        "updatedAt": datetime.now()
    })

    collection.document(new_id).set(data)

    data["id"] = new_id
    return jsonify(data), 201

@bp.route("/<indication_id>/status", methods=["PUT"])
def update_indication_status(indication_id):
    doc_ref = collection.document(indication_id)
    doc_snapshot: DocumentSnapshot = doc_ref.get()

    if not doc_snapshot.exists:
        return jsonify({"error": "Indicação não encontrada"}), 404

    indication_data = doc_snapshot.to_dict()
    body = request.get_json()

    new_status = body.get("status")
    if new_status not in ["pendente", "aprovada", "rejeitada"]:
        return jsonify({"error": "Status inválido"}), 400

    # Atualiza o status
    doc_ref.update({
        "status": new_status,
        "updatedAt": datetime.now()
    })

    # Se for aprovada, cria as comissões
    if new_status == "aprovada":
        try:
            ambassador_id = indication_data["ambassadorId"]
            ambassador_name = indication_data.get("ambassadorName", "")
            client_name = indication_data.get("clientName", "")
            approval_date = datetime.now()

            create_commission_parcels(
                indication_id=indication_id,
                ambassador_id=ambassador_id,
                ambassador_name=ambassador_name,
                client_name=client_name,
                approval_date=approval_date
            )

            print(f"Nova comissão criada para indicação aprovada: {indication_id}")

        except Exception as e:
            print(f"Erro ao criar parcelas: {e}")

    return jsonify({"message": "Status atualizado com sucesso"}), 200
