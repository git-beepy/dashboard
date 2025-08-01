from flask import Blueprint, jsonify, request
from firebase_admin import firestore
from datetime import datetime
from firestore_service import db
from commission_utils import create_commission_parcels
from models import Indication

bp = Blueprint("indications", __name__)

@bp.route("/indications", methods=["POST"])
def create_indication():
    try:
        data = request.get_json()
        data['createdAt'] = datetime.now()
        data['updatedAt'] = datetime.now()

        doc_ref = db.collection("indications").add(data)
        indication_id = doc_ref[1].id  # doc_ref is (write_result, doc_ref)

        return jsonify({"id": indication_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route("/indications/<indication_id>/status", methods=["PUT"])
def update_indication_status(indication_id):
    try:
        data = request.get_json()
        status = data.get("status")

        indication_ref = db.collection("indications").document(indication_id)
        indication_snapshot = indication_ref.get()
        if not indication_snapshot.exists:
            return jsonify({"error": "Indicação não encontrada"}), 404

        indication = indication_snapshot.to_dict()
        indication_ref.update({
            "status": status,
            "updatedAt": datetime.now()
        })

        if status == "aprovado":
            parcels = create_commission_parcels(
                indication_id=indication_id,
                ambassador_id=indication["ambassadorId"],
                ambassador_name=indication["ambassadorName"],
                client_name=indication["clientName"],
                approval_date=datetime.now()
            )

            # Salvar todas as parcelas no Firestore
            for parcel in parcels:
                db.collection("commissions").add(parcel.to_dict())

        return jsonify({"message": "Status atualizado com sucesso"}), 200

    except Exception as e:
        return jsonify({"error": f"Erro ao atualizar status: {str(e)}"}), 500
