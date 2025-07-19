import json
from datetime import datetime
from decimal import Decimal
from firebase_admin import firestore


class CustomJSONEncoder(json.JSONEncoder):
    """Encoder JSON customizado para lidar com tipos especiais do Firebase e Python."""

    def default(self, obj):
        # Converter datetime para string ISO 8601
        if isinstance(obj, datetime):
            return obj.isoformat()

        # Converter Timestamp do Firestore para string ISO 8601
        if hasattr(obj, 'timestamp'):  # Firestore Timestamp
            return obj.isoformat()

        # Converter Decimal para float
        if isinstance(obj, Decimal):
            return float(obj)

        # Converter DocumentReference do Firestore para string
        if hasattr(obj, 'path'):  # Firestore DocumentReference
            return obj.path

        # Para outros tipos não serializáveis, tentar converter para string
        try:
            return str(obj)
        except:
            return super().default(obj)


def serialize_firestore_data(data):
    """
    Serializa dados do Firestore convertendo tipos especiais para tipos JSON-serializáveis.
    """
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            result[key] = serialize_firestore_data(value)
        return result
    elif isinstance(data, list):
        return [serialize_firestore_data(item) for item in data]
    elif isinstance(data, datetime):
        return data.isoformat()
    elif hasattr(data, 'timestamp'):  # Firestore Timestamp
        return data.isoformat()
    elif isinstance(data, Decimal):
        return float(data)
    elif hasattr(data, 'path'):  # Firestore DocumentReference
        return data.path
    else:
        return data


def safe_jsonify(data, status_code=200):
    """
    Função helper para retornar JSON de forma segura, lidando com tipos especiais.
    """
    from flask import Response

    try:
        # Primeiro, serializar os dados
        serialized_data = serialize_firestore_data(data)

        # Depois, converter para JSON usando o encoder customizado
        json_string = json.dumps(serialized_data, cls=CustomJSONEncoder, ensure_ascii=False)

        return Response(
            json_string,
            status=status_code,
            mimetype='application/json'
        )
    except Exception as e:
        # Em caso de erro, retornar erro de serialização
        error_data = {"error": f"Erro de serialização JSON: {str(e)}"}
        json_string = json.dumps(error_data, ensure_ascii=False)
        return Response(
            json_string,
            status=500,
            mimetype='application/json'
        )

