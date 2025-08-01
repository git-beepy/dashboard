from datetime import datetime, timedelta
from google.cloud import firestore
from typing import List, Dict, Any, Optional


class CommissionInstallment:
    """Classe para gerenciar parcelas de comissão"""

    def __init__(self, db: firestore.Client):
        self.db = db
        self.collection_name = "commission_installments"

    def create_installments_for_indication(self, indication_id: str, ambassador_id: str,
                                           ambassador_name: str, client_name: str) -> List[str]:
        """
        Cria automaticamente 3 parcelas de R$ 300,00 para uma indicação
        """
        try:
            now = datetime.now()
            total_commission = 900.0
            installment_value = 300.0
            installment_ids = []

            installment_dates = [
                now,
                now + timedelta(days=30),
                now + timedelta(days=90)
            ]

            for i, due_date in enumerate(installment_dates, 1):
                installment_data = {
                    "indication_id": indication_id,
                    "ambassador_id": ambassador_id,
                    "ambassador_name": ambassador_name,
                    "client_name": client_name,
                    "installment_number": i,
                    "value": installment_value,
                    "due_date": due_date,
                    "status": "pendente",
                    "payment_date": None,
                    "created_at": now,
                    "updated_at": now,
                    "total_commission": total_commission,
                    "notes": ""
                }

                doc_ref, _ = self.db.collection(self.collection_name).add(installment_data)
                installment_ids.append(doc_ref.id)

                print(f"Parcela {i} criada: R$ {installment_value} - Vencimento: {due_date.strftime('%d/%m/%Y')}")

            return installment_ids

        except Exception as e:
            print(f"Erro ao criar parcelas: {str(e)}")
            raise

    def get_installments_by_indication(self, indication_id: str) -> List[Dict[str, Any]]:
        """
        Busca todas as parcelas de uma indicação específica
        """
        try:
            query = self.db.collection(self.collection_name).where(
                "indication_id", "==", indication_id
            ).order_by("installment_number")

            docs = query.stream()
            return [self._add_doc_id(doc) for doc in docs]

        except Exception as e:
            print(f"Erro ao buscar parcelas da indicação {indication_id}: {str(e)}")
            return []

    def get_installments_by_ambassador(self, ambassador_id: str,
                                       status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Busca todas as parcelas de uma embaixadora, com filtro opcional de status
        """
        try:
            query = self.db.collection(self.collection_name).where(
                "ambassador_id", "==", ambassador_id
            )

            if status_filter:
                query = query.where("status", "==", status_filter)

            query = query.order_by("due_date")
            docs = query.stream()

            return [self._add_doc_id(doc) for doc in docs]

        except Exception as e:
            print(f"Erro ao buscar parcelas da embaixadora {ambassador_id}: {str(e)}")
            return []

    def get_all_installments(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Busca todas as parcelas, com filtros opcionais
        """
        try:
            query = self.db.collection(self.collection_name)

            if filters:
                if filters.get("status"):
                    query = query.where("status", "==", filters["status"])

                if filters.get("ambassador_id"):
                    query = query.where("ambassador_id", "==", filters["ambassador_id"])

            query = query.order_by("due_date", direction=firestore.Query.DESCENDING)
            docs = query.stream()
            installments = [self._add_doc_id(doc) for doc in docs]

            if filters:
                month = filters.get("month")
                year = filters.get("year")
                if month:
                    month = int(month)
                if year:
                    year = int(year)

                def match_date(i):
                    due_date = i.get("due_date")
                    if not isinstance(due_date, datetime):
                        return False
                    return (
                        (not month or due_date.month == month) and
                        (not year or due_date.year == year)
                    )

                installments = [i for i in installments if match_date(i)]

            return installments

        except Exception as e:
            print(f"Erro ao buscar todas as parcelas: {str(e)}")
            return []

    def update_installment_status(self, installment_id: str, new_status: str,
                                  payment_date: Optional[datetime] = None,
                                  notes: Optional[str] = None) -> bool:
        """
        Atualiza o status de uma parcela
        """
        try:
            if new_status not in ["pendente", "pago", "atrasado"]:
                raise ValueError("Status inválido. Use: pendente, pago, atrasado")

            now = datetime.now()
            update_data = {
                "status": new_status,
                "updated_at": now
            }

            if payment_date:
                update_data["payment_date"] = payment_date
            elif new_status == "pago":
                update_data["payment_date"] = now

            if notes is not None:
                update_data["notes"] = notes

            self.db.collection(self.collection_name).document(installment_id).update(update_data)
            print(f"Parcela {installment_id} atualizada para status: {new_status}")
            return True

        except Exception as e:
            print(f"Erro ao atualizar parcela {installment_id}: {str(e)}")
            return False

    def check_overdue_installments(self) -> List[Dict[str, Any]]:
        """
        Verifica e marca parcelas em atraso
        """
        try:
            now = datetime.now()
            query = self.db.collection(self.collection_name).where("status", "==", "pendente")
            docs = query.stream()

            overdue = []

            for doc in docs:
                data = doc.to_dict()
                due_date = data.get("due_date")
                if isinstance(due_date, datetime) and due_date < now:
                    self.update_installment_status(doc.id, "atrasado")
                    data["id"] = doc.id
                    overdue.append(data)

            return overdue

        except Exception as e:
            print(f"Erro ao verificar parcelas em atraso: {str(e)}")
            return []

    def get_commission_summary(self, ambassador_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Gera resumo das comissões
        """
        try:
            query = self.db.collection(self.collection_name)

            if ambassador_id:
                query = query.where("ambassador_id", "==", ambassador_id)

            docs = query.stream()
            summary = {
                "total_installments": 0,
                "total_value": 0.0,
                "paid_installments": 0,
                "paid_value": 0.0,
                "pending_installments": 0,
                "pending_value": 0.0,
                "overdue_installments": 0,
                "overdue_value": 0.0
            }

            for doc in docs:
                data = doc.to_dict()
                value = data.get("value", 0.0)
                status = data.get("status", "pendente")

                summary["total_installments"] += 1
                summary["total_value"] += value

                if status == "pago":
                    summary["paid_installments"] += 1
                    summary["paid_value"] += value
                elif status == "pendente":
                    summary["pending_installments"] += 1
                    summary["pending_value"] += value
                elif status == "atrasado":
                    summary["overdue_installments"] += 1
                    summary["overdue_value"] += value

            return summary

        except Exception as e:
            print(f"Erro ao gerar resumo das comissões: {str(e)}")
            return {}

    @staticmethod
    def _add_doc_id(doc: firestore.DocumentSnapshot) -> Dict[str, Any]:
        data = doc.to_dict()
        data["id"] = doc.id
        return data
