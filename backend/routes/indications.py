from flask import Blueprint, request, jsonify
from firebase_admin import firestore
from datetime import datetime

from models import Indication
from commission_utils import create_commission_parcels

db = firestore.client()
indications_bp = Blueprint("indications", __name__)

@indications_bp.route("/indications", methods=["POST"])
def create_indication():
    data = request.get_json()
    data["createdAt"] = datetime.now()
    data["updatedAt"] = datetime.now()
    doc_ref = db.collection("indications").add(data)
    indication_id = doc_ref[1].id

    # Quando status é 'aprovado', gerar comissões
    if data.get("status") == "aprovado":
        try:
            parcels = create_commission_parcels(
                indication_id=indication_id,
                ambassador_id=data["ambassadorId"],
                ambassador_name=data["ambassadorName"],
                client_name=data["clientName"],
                approval_date=data.get("updatedAt", datetime.now())
            )
            for parcel in parcels:
                db.collection("commissions").add(parcel.to_dict())

            print(f"Nova comissão criada para indicação aprovada: {indication_id} -> {doc_ref[1].id}")
        except Exception as e:
            print("Erro ao criar parcelas:", str(e))

    return jsonify({"id": indication_id}), 201
