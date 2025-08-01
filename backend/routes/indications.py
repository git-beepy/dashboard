from flask import Blueprint, request, jsonify
from firebase_admin import firestore
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from datetime import datetime
from utils import generate_uuid
from commission_utils import create_commission_parcels
from models import Commission

bp = Blueprint("indications", __name__)
db = firestore.client()


@bp.route("/indications", methods=["POST"])
def create_indication():
    try:
        data = request.get_json()
        data["createdAt"] = datetime.now()
        data["updatedAt"] = datetime.now()

        doc_ref = db.collection("indications").document()
        data["id"] = doc_ref.id
        doc_ref.set(data)

        return jsonify(data), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/indications", methods=["GET"])
def get_indications():
    try:
        indications_ref = db.collection("indications")
        docs = indications_ref.stream()
        indications = [doc.to_dict() for doc in docs]
        return jsonify(indications), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/indications/<id>", methods=["DELETE"])
def delete_indication(id):
    try:
        db.collection("indications").document(id).delete()
        return jsonify({"message": f"Indicação {id} deletada com sucesso."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/indications/<id>/status", methods=["PUT"])
def update_indication_status(id):
    try:
        doc_ref = db.collection("indications").document(id)
        doc = doc_ref.get()

        if not doc.exists:
            return jsonify({"error": "Indicação não encontrada."}), 404

        data = doc.to_dict()
        new_status = request.json.get("status")
        approval_date = datetime.now()

        doc_ref.update({
            "status": new_status,
            "updatedAt": approval_date,
        })

        if new_status == "aprovado":
            parcels = create_commission_parcels(
                indication_id=id,
                ambassador_id=data.get("ambassadorId"),
                ambassador_name=data.get("ambassadorName"),
                client_name=data.get("clientName"),
                approval_date=approval_date,
            )

            batch = db.batch()
            for parcel in parcels:
                parcel_ref = db.collection("commissions").document()
                parcel.id = parcel_ref.id
                batch.set(parcel_ref, parcel.to_dict())

            batch.commit()

            print(f"Nova comissão criada para indicação aprovada: {id} -> {[p.id for p in parcels]}")

        return jsonify({"message": "Status atualizado com sucesso."}), 200

    except Exception as e:
        print("Erro ao criar parcelas:", str(e))
        return jsonify({"error": str(e)}), 500
