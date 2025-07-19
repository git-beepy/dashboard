import json
from datetime import datetime
from flask import jsonify


class CustomJSONEncoder(json.JSONEncoder):
    """Encoder personalizado para serializar objetos datetime e outros tipos especiais"""
    
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def safe_jsonify(data, status_code=200):
    """Função helper para retornar JSON de forma segura"""
    try:
        response = jsonify(data)
        response.status_code = status_code
        return response
    except Exception as e:
        print(f"Erro ao serializar JSON: {e}")
        error_response = jsonify({"error": "Erro interno do servidor"})
        error_response.status_code = 500
        return error_response


def serialize_firestore_data(data):
    """Serializa dados do Firestore para JSON"""
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            result[key] = serialize_firestore_data(value)
        return result
    elif isinstance(data, list):
        return [serialize_firestore_data(item) for item in data]
    elif hasattr(data, 'timestamp'):
        # Timestamp do Firestore
        return data.timestamp()
    elif isinstance(data, datetime):
        return data.isoformat()
    else:
        return data

