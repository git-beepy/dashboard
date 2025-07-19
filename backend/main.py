import os
import sys
import firebase_admin
from firebase_admin import credentials, firestore, auth
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import bcrypt
from utils import CustomJSONEncoder, safe_jsonify, serialize_firestore_data
import json

# Inicializar Firebase
# Tenta carregar as credenciais da variável de ambiente GOOGLE_APPLICATION_CREDENTIALS primeiro
if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
    try:
        # Usar json.loads do módulo json padrão através de __import__
        cred_json = __import__("json").loads(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))
        cred = credentials.Certificate(cred_json)
    except __import__("json").JSONDecodeError:
        # Fallback para o arquivo local se a variável de ambiente não for um JSON válido
        # (Isso não deve acontecer se o JSON for copiado corretamente para a variável)
        cred = credentials.Certificate("projeto-beepy-firebase-adminsdk-fbsvc-45c41daaaf.json")
else:
    # Fallback para o arquivo local se a variável de ambiente não estiver definida
    cred = credentials.Certificate("projeto-beepy-firebase-adminsdk-fbsvc-45c41daaaf.json")

firebase_admin.initialize_app(cred)
db = firestore.client()


def create_app():
    flask_app = Flask(__name__)

    flask_app.config["SECRET_KEY"] = "beepy-secret-key-2024"
    flask_app.config["JWT_SECRET_KEY"] = "beepy-jwt-secret-key-2024"
    flask_app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)

    jwt = JWTManager(flask_app)
    CORS(flask_app, supports_credentials=True, origins=os.environ.get("ALLOWED_ORIGINS").split(",") if os.environ.get("ALLOWED_ORIGINS") else "*")

    # Rotas de autenticação
    @flask_app.route("/api/auth/login", methods=["POST"])
    def login():
        try:
            data = request.get_json()
            email = data.get("email")
            password = data.get("password")

            if not email or not password:
                return safe_jsonify({"error": "Email e senha são obrigatórios"}, 400)

            users_ref = db.collection("users")
            query = users_ref.where(field_path="email", op_string="==", value=email).limit(1)
            docs = list(query.stream())

            if not docs:
                return safe_jsonify({"error": "Usuário não encontrado"}, 401)

            user_doc = docs[0]
            user_data = user_doc.to_dict()

            # Verificar senha
            stored_password = user_data.get("password", "")
            if isinstance(stored_password, str):
                try:
                    if bcrypt.checkpw(password.encode("utf-8"), stored_password.encode("utf-8")):
                        access_token = create_access_token(
                            identity=user_doc.id,
                            additional_claims={
                                "email": user_data["email"],
                                "role": user_data["role"]
                            }
                        )

                        response_data = {
                            "access_token": access_token,
                            "user": {
                                "id": user_doc.id,
                                "email": user_data["email"],
                                "role": user_data["role"],
                                "name": user_data.get("name", "")
                            }
                        }

                        return safe_jsonify(response_data, 200)
                    else:
                        return safe_jsonify({"error": "Senha incorreta"}, 401)
                except ValueError as e:
                    print(f"Erro ao validar hash da senha: {str(e)}")
                    return safe_jsonify({"error": f"Erro interno: hash de senha inválido"}, 500)
            else:
                return safe_jsonify({"error": "Senha em formato inválido"}, 500)

        except Exception as e:
            print(f"Erro no login: {str(e)}")
            return safe_jsonify({"error": f"Erro interno: {str(e)}"}, 500)

    # Rotas de indicações
    @flask_app.route("/api/indications", methods=["GET"])
    @jwt_required()
    def get_indications():
        try:
            current_user_id = get_jwt_identity()

            # Buscar dados do usuário atual
            user_doc = db.collection("users").document(current_user_id).get()
            if not user_doc.exists:
                return safe_jsonify({"error": "Usuário não encontrado"}, 404)

            user_data = user_doc.to_dict()

            # Se for admin, retorna todas as indicações
            if user_data["role"] == "admin":
                indications_ref = db.collection("indications")
            else:
                # Se for embaixadora, retorna apenas suas indicações
                indications_ref = db.collection("indications").where(field_path="ambassadorId", op_string="==", value=current_user_id)

            docs = indications_ref.stream()
            indications = []

            for doc in docs:
                indication_data = doc.to_dict()
                indication_data["id"] = doc.id
                # Serializar dados do Firestore
                indication_data = serialize_firestore_data(indication_data)
                indications.append(indication_data)

            return safe_jsonify(indications, 200)

        except Exception as e:
            print(f"Erro ao buscar indicações: {str(e)}")
            return safe_jsonify({"error": str(e)}, 500)

    @flask_app.route("/api/indications", methods=["POST"])
    @jwt_required()
    def create_indication():
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json()

            indication_data = {
                "ambassadorId": current_user_id,
                "clientName": data.get("clientName"),
                "clientEmail": data.get("clientEmail"),
                "clientPhone": data.get("clientPhone"),
                "origin": data.get("origin", "website"),
                "segment": data.get("segment", "geral"),
                "converted": False,
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            }

            doc_ref = db.collection("indications").add(indication_data)
            indication_data["id"] = doc_ref[1].id

            # Serializar dados antes de retornar
            indication_data = serialize_firestore_data(indication_data)

            return safe_jsonify(indication_data, 201)

        except Exception as e:
            print(f"Erro ao criar indicação: {str(e)}")
            return safe_jsonify({"error": str(e)}, 500)

    @flask_app.route("/api/indications/<indication_id>", methods=["PUT"])
    @jwt_required()
    def update_indication(indication_id):
        try:
            data = request.get_json()

            update_data = {
                "updatedAt": datetime.now()
            }

            if "converted" in data:
                update_data["converted"] = data["converted"]
            if "clientName" in data:
                update_data["clientName"] = data["clientName"]
            if "clientEmail" in data:
                update_data["clientEmail"] = data["clientEmail"]
            if "clientPhone" in data:
                update_data["clientPhone"] = data["clientPhone"]
            if "origin" in data:
                update_data["origin"] = data["origin"]
            if "segment" in data:
                update_data["segment"] = data["segment"]

            db.collection("indications").document(indication_id).update(update_data)

            return safe_jsonify({"message": "Indicação atualizada com sucesso"}, 200)

        except Exception as e:
            print(f"Erro ao atualizar indicação: {str(e)}")
            return safe_jsonify({"error": str(e)}, 500)

    @flask_app.route("/api/indications/<indication_id>", methods=["DELETE"])
    @jwt_required()
    def delete_indication(indication_id):
        try:
            db.collection("indications").document(indication_id).delete()
            return safe_jsonify({"message": "Indicação excluída com sucesso"}, 200)

        except Exception as e:
            print(f"Erro ao excluir indicação: {str(e)}")
            return safe_jsonify({"error": str(e)}, 500)

    # Rotas de usuários
    @flask_app.route("/api/users", methods=["GET"])
    @jwt_required()
    def get_users():
        try:
            current_user_id = get_jwt_identity()

            # Verificar se é admin
            user_doc = db.collection("users").document(current_user_id).get()
            if not user_doc.exists:
                return safe_jsonify({"error": "Usuário não encontrado"}, 404)

            user_data = user_doc.to_dict()
            if user_data["role"] != "admin":
                return safe_jsonify({"error": "Acesso negado"}, 403)

            # Buscar todos os usuários
            users_ref = db.collection("users")
            docs = users_ref.stream()
            users = []

            for doc in docs:
                user_data = doc.to_dict()
                user_data["id"] = doc.id
                # Remover senha do retorno
                if "password" in user_data:
                    del user_data["password"]
                # Serializar dados do Firestore
                user_data = serialize_firestore_data(user_data)
                users.append(user_data)

            return safe_jsonify(users, 200)

        except Exception as e:
            print(f"Erro ao buscar usuários: {str(e)}")
            return safe_jsonify({"error": str(e)}, 500)

    @flask_app.route("/api/users", methods=["POST"])
    @jwt_required()
    def create_user():
        try:
            current_user_id = get_jwt_identity()

            # Verificar se é admin
            user_doc = db.collection("users").document(current_user_id).get()
            if not user_doc.exists:
                return safe_jsonify({"error": "Usuário não encontrado"}, 404)

            user_data = user_doc.to_dict()
            if user_data["role"] != "admin":
                return safe_jsonify({"error": "Acesso negado"}, 403)

            data = request.get_json()

            # Validar dados obrigatórios
            if not data.get("email") or not data.get("password") or not data.get("name") or not data.get("role"):
                return safe_jsonify({"error": "Email, senha, nome e role são obrigatórios"}, 400)

            # Verificar se email já existe
            users_ref = db.collection("users")
            query = users_ref.where(field_path="email", op_string="==", value=data.get("email")).limit(1)
            existing_users = list(query.stream())

            if existing_users:
                return safe_jsonify({"error": "Email já está em uso"}, 400)

            # Criar hash da senha
            hashed_password = bcrypt.hashpw(data.get("password").encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

            new_user_data = {
                "email": data.get("email"),
                "password": hashed_password,
                "name": data.get("name"),
                "role": data.get("role"),
                "phone": data.get("phone", ""),
                "createdAt": datetime.now(),
                "lastActiveAt": datetime.now()
            }

            doc_ref = db.collection("users").add(new_user_data)
            new_user_data["id"] = doc_ref[1].id

            # Remover senha do retorno
            del new_user_data["password"]

            # Serializar dados antes de retornar
            new_user_data = serialize_firestore_data(new_user_data)

            return safe_jsonify(new_user_data, 201)

        except Exception as e:
            print(f"Erro ao criar usuário: {str(e)}")
            return safe_jsonify({"error": str(e)}, 500)

    @flask_app.route("/api/users/<user_id>", methods=["PUT"])
    @jwt_required()
    def update_user(user_id):
        try:
            current_user_id = get_jwt_identity()

            # Verificar se é admin
            user_doc = db.collection("users").document(current_user_id).get()
            if not user_doc.exists:
                return safe_jsonify({"error": "Usuário não encontrado"}, 404)

            user_data = user_doc.to_dict()
            if user_data["role"] != "admin":
                return safe_jsonify({"error": "Acesso negado"}, 403)

            data = request.get_json()

            update_data = {
                "lastActiveAt": datetime.now()
            }

            if "name" in data:
                update_data["name"] = data["name"]
            if "email" in data:
                # Verificar se email já existe em outro usuário
                users_ref = db.collection("users")
                query = users_ref.where(field_path="email", op_string="==", value=data["email"]).limit(1)
                existing_users = list(query.stream())

                if existing_users and existing_users[0].id != user_id:
                    return safe_jsonify({"error": "Email já está em uso"}, 400)

                update_data["email"] = data["email"]
            if "role" in data:
                update_data["role"] = data["role"]
            if "phone" in data:
                update_data["phone"] = data["phone"]
            if "password" in data and data["password"]:
                # Criar hash da nova senha
                hashed_password = bcrypt.hashpw(data["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
                update_data["password"] = hashed_password

            db.collection("users").document(user_id).update(update_data)

            return safe_jsonify({"message": "Usuário atualizado com sucesso"}, 200)

        except Exception as e:
            print(f"Erro ao atualizar usuário: {str(e)}")
            return safe_jsonify({"error": str(e)}, 500)

    @flask_app.route("/api/users/<user_id>", methods=["DELETE"])
    @jwt_required()
    def delete_user(user_id):
        try:
            current_user_id = get_jwt_identity()

            # Verificar se é admin
            user_doc = db.collection("users").document(current_user_id).get()
            if not user_doc.exists:
                return safe_jsonify({"error": "Usuário não encontrado"}, 404)

            user_data = user_doc.to_dict()
            if user_data["role"] != "admin":
                return safe_jsonify({"error": "Acesso negado"}, 403)

            # Não permitir deletar a si mesmo
            if current_user_id == user_id:
                return safe_jsonify({"error": "Não é possível deletar seu próprio usuário"}, 400)

            db.collection("users").document(user_id).delete()
            return safe_jsonify({"message": "Usuário excluído com sucesso"}, 200)

        except Exception as e:
            print(f"Erro ao excluir usuário: {str(e)}")
            return safe_jsonify({"error": str(e)}, 500)

    # Rotas de comissões
    @flask_app.route("/api/commissions", methods=["GET"])
    @jwt_required()
    def get_commissions():
        try:
            current_user_id = get_jwt_identity()

            # Buscar dados do usuário atual
            user_doc = db.collection("users").document(current_user_id).get()
            if not user_doc.exists:
                return safe_jsonify({"error": "Usuário não encontrado"}, 404)

            user_data = user_doc.to_dict()

            # Se for admin, retorna todas as comissões
            if user_data["role"] == "admin":
                commissions_ref = db.collection("commissions")
            else:
                # Se for embaixadora, retorna apenas suas comissões
                commissions_ref = db.collection("commissions").where(field_path="ambassadorId", op_string="==", value=current_user_id)

            docs = commissions_ref.stream()
            commissions = []

            for doc in docs:
                commission_data = doc.to_dict()
                commission_data["id"] = doc.id
                # Serializar dados do Firestore
                commission_data = serialize_firestore_data(commission_data)
                commissions.append(commission_data)

            return safe_jsonify(commissions, 200)

        except Exception as e:
            print(f"Erro ao buscar comissões: {str(e)}")
            return safe_jsonify({"error": str(e)}, 500)

    @flask_app.route("/api/commissions", methods=["POST"])
    @jwt_required()
    def create_commission():
        try:
            data = request.get_json()

            commission_data = {
                "ambassadorId": data.get("ambassadorId"),
                "indicationId": data.get("indicationId"),
                "value": data.get("value"),
                "status": data.get("status", "pending"),
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            }

            doc_ref = db.collection("commissions").add(commission_data)
            commission_data["id"] = doc_ref[1].id

            # Serializar dados antes de retornar
            commission_data = serialize_firestore_data(commission_data)

            return safe_jsonify(commission_data, 201)

        except Exception as e:
            print(f"Erro ao criar comissão: {str(e)}")
            return safe_jsonify({"error": str(e)}, 500)

    @flask_app.route("/api/commissions/<commission_id>", methods=["PUT"])
    @jwt_required()
    def update_commission(commission_id):
        try:
            data = request.get_json()

            update_data = {
                "updatedAt": datetime.now()
            }

            if "status" in data:
                update_data["status"] = data["status"]
            if "value" in data:
                update_data["value"] = data["value"]

            db.collection("commissions").document(commission_id).update(update_data)

            return safe_jsonify({"message": "Comissão atualizada com sucesso"}, 200)

        except Exception as e:
            print(f"Erro ao atualizar comissão: {str(e)}")
            return safe_jsonify({"error": str(e)}, 500)

    @flask_app.route("/api/commissions/<commission_id>", methods=["DELETE"])
    @jwt_required()
    def delete_commission(commission_id):
        try:
            db.collection("commissions").document(commission_id).delete()
            return safe_jsonify({"message": "Comissão excluída com sucesso"}, 200)

        except Exception as e:
            print(f"Erro ao excluir comissão: {str(e)}")
            return safe_jsonify({"error": str(e)}, 500)

    # Rotas de vendas
    @flask_app.route("/api/sales", methods=["GET"])
    @jwt_required()
    def get_sales():
        try:
            current_user_id = get_jwt_identity()

            # Buscar dados do usuário atual
            user_doc = db.collection("users").document(current_user_id).get()
            if not user_doc.exists:
                return safe_jsonify({"error": "Usuário não encontrado"}, 404)

            user_data = user_doc.to_dict()

            # Se for admin, retorna todas as vendas
            if user_data["role"] == "admin":
                sales_ref = db.collection("sales")
            else:
                # Se for embaixadora, retorna apenas suas vendas
                sales_ref = db.collection("sales").where(field_path="ambassadorId", op_string="==", value=current_user_id)

            docs = sales_ref.stream()
            sales = []

            for doc in docs:
                sale_data = doc.to_dict()
                sale_data["id"] = doc.id
                # Serializar dados do Firestore
                sale_data = serialize_firestore_data(sale_data)
                sales.append(sale_data)

            return safe_jsonify(sales, 200)

        except Exception as e:
            print(f"Erro ao buscar vendas: {str(e)}")
            return safe_jsonify({"error": str(e)}, 500)

    @flask_app.route("/api/sales", methods=["POST"])
    @jwt_required()
    def create_sale():
        try:
            data = request.get_json()

            sale_data = {
                "ambassadorId": data.get("ambassadorId"),
                "indicationId": data.get("indicationId"),
                "value": data.get("value"),
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            }

            doc_ref = db.collection("sales").add(sale_data)
            sale_data["id"] = doc_ref[1].id

            # Serializar dados antes de retornar
            sale_data = serialize_firestore_data(sale_data)

            return safe_jsonify(sale_data, 201)

        except Exception as e:
            print(f"Erro ao criar venda: {str(e)}")
            return safe_jsonify({"error": str(e)}, 500)

    # Rotas de dashboard
    @flask_app.route("/api/dashboard/admin", methods=["GET"])
    @jwt_required()
    def get_admin_dashboard():
        try:
            current_user_id = get_jwt_identity()

            # Verificar se é admin
            user_doc = db.collection("users").document(current_user_id).get()
            if not user_doc.exists:
                return safe_jsonify({"error": "Usuário não encontrado"}, 404)

            user_data = user_doc.to_dict()
            if user_data["role"] != "admin":
                return safe_jsonify({"error": "Acesso negado"}, 403)

            # Buscar dados para o dashboard
            dashboard_data = {}

            # Embaixadoras ativas (últimos 60 dias)
            sixty_days_ago = datetime.now() - timedelta(days=60)
            users_ref = db.collection("users").where(field_path="role", op_string="==", value="embaixadora")
            active_ambassadors = 0
            total_ambassadors = 0

            for user_doc in users_ref.stream():
                total_ambassadors += 1
                user_data = user_doc.to_dict()
                if "lastActiveAt" in user_data:
                    last_active = user_data["lastActiveAt"]
                    # Converter para datetime se necessário
                    if hasattr(last_active, (
                            'timestamp')):
                        last_active = last_active.timestamp()
                        last_active = datetime.fromtimestamp(last_active)
                    elif isinstance(last_active, str):
                        try:
                            last_active = datetime.fromisoformat(last_active.replace("Z", "+00:00"))
                        except:
                            continue

                    if last_active > sixty_days_ago:
                        active_ambassadors += 1

            dashboard_data["activeAmbassadors"] = {
                "active": active_ambassadors,
                "total": total_ambassadors,
                "percentage": (active_ambassadors / total_ambassadors * 100) if total_ambassadors > 0 else 0
            }

            # Indicações por mês
            indications_ref = db.collection("indications")
            indications_by_month = {}

            for indication_doc in indications_ref.stream():
                indication_data = indication_doc.to_dict()
                if "createdAt" in indication_data:
                    created_at = indication_data["createdAt"]
                    if hasattr(created_at, (
                            'timestamp')):
                        created_at = datetime.fromtimestamp(created_at.timestamp())
                    elif isinstance(created_at, str):
                        try:
                            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                        except:
                            created_at = datetime.now()

                    month_key = created_at.strftime("%Y-%m")
                    indications_by_month[month_key] = indications_by_month.get(month_key, 0) + 1

            dashboard_data["indicationsByMonth"] = indications_by_month

            # Leads por origem
            leads_by_origin = {}
            for indication_doc in indications_ref.stream():
                indication_data = indication_doc.to_dict()
                origin = indication_data.get("origin", "unknown")
                leads_by_origin[origin] = leads_by_origin.get(origin, 0) + 1

            dashboard_data["leadsByOrigin"] = leads_by_origin

            # Conversão por segmento
            conversion_by_segment = {}
            for indication_doc in indications_ref.stream():
                indication_data = indication_doc.to_dict()
                segment = indication_data.get("segment", "geral")
                if segment not in conversion_by_segment:
                    conversion_by_segment[segment] = {"total": 0, "converted": 0}
                conversion_by_segment[segment]["total"] += 1
                if indication_data.get("converted", False):
                    conversion_by_segment[segment]["converted"] += 1

            dashboard_data["conversionBySegment"] = conversion_by_segment

            # Vendas por mês
            sales_ref = db.collection("sales")
            sales_by_month = {}

            for sale_doc in sales_ref.stream():
                sale_data = sale_doc.to_dict()
                if "createdAt" in sale_data:
                    created_at = sale_data["createdAt"]
                    if hasattr(created_at, (
                            'timestamp')):
                        created_at = datetime.fromtimestamp(created_at.timestamp())
                    elif isinstance(created_at, str):
                        try:
                            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                        except:
                            created_at = datetime.now()

                    month_key = created_at.strftime("%Y-%m")
                    if month_key not in sales_by_month:
                        sales_by_month[month_key] = 0
                    sales_by_month[month_key] += sale_data.get("value", 0)

            dashboard_data["salesByMonth"] = sales_by_month

            # Top embaixadoras por indicação
            ambassador_indications = {}
            for indication_doc in indications_ref.stream():
                indication_data = indication_doc.to_dict()
                ambassador_id = indication_data.get("ambassadorId")
                if ambassador_id:
                    ambassador_indications[ambassador_id] = ambassador_indications.get(ambassador_id, 0) + 1

            dashboard_data["topAmbassadorsByIndications"] = ambassador_indications

            # Serializar dados antes de retornar
            dashboard_data = serialize_firestore_data(dashboard_data)

            return safe_jsonify(dashboard_data, 200)

        except Exception as e:
            print(f"Erro no dashboard admin: {str(e)}")
            return safe_jsonify({"error": str(e)}, 500)

    @flask_app.route("/api/dashboard/embaixadora", methods=["GET"])
    @jwt_required()
    def get_ambassador_dashboard():
        try:
            current_user_id = get_jwt_identity()

            # Buscar dados do usuário atual
            user_doc = db.collection("users").document(current_user_id).get()
            if not user_doc.exists:
                return safe_jsonify({"error": "Usuário não encontrado"}, 404)

            user_data = user_doc.to_dict()
            if user_data["role"] != "embaixadora":
                return safe_jsonify({"error": "Acesso negado"}, 403)

            # Buscar dados para o dashboard da embaixadora
            dashboard_data = {}

            # Indicações da embaixadora
            indications_ref = db.collection("indications").where(field_path="ambassadorId", op_string="==", value=current_user_id)
            total_indications = 0
            converted_indications = 0
            indications_by_month = {}

            for indication_doc in indications_ref.stream():
                indication_data = indication_doc.to_dict()
                total_indications += 1
                if indication_data.get("converted", False):
                    converted_indications += 1

                if "createdAt" in indication_data:
                    created_at = indication_data["createdAt"]
                    if hasattr(created_at, (
                            'timestamp')):
                        created_at = datetime.fromtimestamp(created_at.timestamp())
                    elif isinstance(created_at, str):
                        try:
                            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                        except:
                            created_at = datetime.now()

                    month_key = created_at.strftime("%Y-%m")
                    indications_by_month[month_key] = indications_by_month.get(month_key, 0) + 1

            dashboard_data["totalIndications"] = total_indications
            dashboard_data["convertedIndications"] = converted_indications
            dashboard_data["conversionRate"] = (converted_indications / total_indications * 100) if total_indications > 0 else 0
            dashboard_data["indicationsByMonth"] = indications_by_month

            # Comissões da embaixadora
            commissions_ref = db.collection("commissions").where(field_path="ambassadorId", op_string="==", value=current_user_id)
            total_commissions = 0
            paid_commissions = 0

            for commission_doc in commissions_ref.stream():
                commission_data = commission_doc.to_dict()
                total_commissions += commission_data.get("value", 0)
                if commission_data.get("status") == "paid":
                    paid_commissions += commission_data.get("value", 0)

            dashboard_data["totalCommissions"] = total_commissions
            dashboard_data["paidCommissions"] = paid_commissions
            dashboard_data["pendingCommissions"] = total_commissions - paid_commissions

            # Serializar dados antes de retornar
            dashboard_data = serialize_firestore_data(dashboard_data)

            return safe_jsonify(dashboard_data, 200)

        except Exception as e:
            print(f"Erro no dashboard embaixadora: {str(e)}")
            return safe_jsonify({"error": str(e)}, 500)

    # Rota para criar usuário admin inicial
    @flask_app.route("/api/setup", methods=["POST"])
    def setup_admin():
        try:
            # Verificar se já existe um admin
            users_ref = db.collection("users").where(field_path="role", op_string="==", value="admin").limit(1)
            docs = list(users_ref.stream())

            if docs:
                return safe_jsonify({"message": "Admin já existe"}, 200)

            # Criar usuário admin
            hashed_password = bcrypt.hashpw("admin123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

            admin_data = {
                "email": "admin@beepy.com",
                "password": hashed_password,
                "role": "admin",
                "name": "Administrador",
                "createdAt": datetime.now(),
                "lastActiveAt": datetime.now()
            }

            db.collection("users").add(admin_data)

            return safe_jsonify({"message": "Usuário admin criado com sucesso"}, 201)

        except Exception as e:
            print(f"Erro ao criar admin: {str(e)}")
            return safe_jsonify({"error": str(e)}, 500)

    @flask_app.route("/")
    def home():
        return safe_jsonify({
            "message": "Beepy API - Sistema de Indicações e Comissões",
            "version": "2.0",
            "endpoints": {
                "auth": "/api/auth",
                "indications": "/api/indications",
                "commissions": "/api/commissions",
                "sales": "/api/sales",
                "dashboard": "/api/dashboard"
            }
        })

    @flask_app.route("/health")
    def health():
        return safe_jsonify({"status": "healthy", "service": "beepy-api"})

    return flask_app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)


