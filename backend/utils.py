from datetime import datetime
from flask import jsonify

def serialize_firestore_data(data):
    """Serializa dados do Firestore para JSON"""
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, dict):
                result[key] = serialize_firestore_data(value)
            elif isinstance(value, list):
                result[key] = [serialize_firestore_data(item) if isinstance(item, (dict, datetime)) else item for item in value]
            else:
                result[key] = value
        return result
    elif isinstance(data, datetime):
        return data.isoformat()
    else:
        return data

def safe_jsonify(data, status_code=200):
    """Wrapper seguro para jsonify"""
    try:
        response = jsonify(data)
        response.status_code = status_code
        return response
    except Exception as e:
        error_response = jsonify({"error": f"Erro na serialização: {str(e)}"})
        error_response.status_code = 500
        return error_response
