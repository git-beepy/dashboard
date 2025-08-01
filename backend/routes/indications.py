from flask import Blueprint, request, jsonify
from firebase_admin import firestore
from datetime import datetime
from commission_utils import create_commission_parcels

db = firestore.client()
indications_bp = Blueprint("indications", __name__)

@indications_bp.route("/indications/<string:indication_id>/status", methods=["PUT"])
def update_indication_status(indication_id):
    try:
        data = request.get_json()
        new_status = data.get("status")

        if new_status is None:
            return jsonify({"error": "Campo 'status' é obrigatório"}), 400

        indication_ref = db.collection("indications").document(indication_id)
        indication_doc = indication_ref.get()

        if not indication_doc.exists:
            return jsonify({"error": "Indicação não encontrada"}), 404

        indication_data = indication_doc.to_dict()
        indication_ref.update({
            "status": new_status,
            "updatedAt": datetime.now()
        })

        # Se status mudou para aprovado, cria as comissões parceladas
        if new_status == "aprovado":
            ambassador_id = indication_data.get("ambassadorId")
            ambassador_name = indication_data.get("ambassadorName")
            client_name = indication_data.get("clientName")

            approval_date = indication_data.get("updatedAt", datetime.now())
            if hasattr(approval_date, "timestamp"):
                approval_date = approval_date.replace(tzinfo=None)

            parcels = create_commission_parcels(
                indication_id,
                ambassador_id,
                ambassador_name,
                client_name,
                approval_date
            )

            # Salva todas as parcelas no Firestore
            for parcel in parcels:
                db.collection("commissions").add(parcel.to_dict())

            print(f"Nova comissão criada para indicação aprovada: {indication_id} -> {ambassador_id}")

        return jsonify({"message": "Status atualizado com sucesso"}), 200

    except Exception as e:
        print("Erro ao criar parcelas:", e)
        return jsonify({"error": str(e)}), 500
