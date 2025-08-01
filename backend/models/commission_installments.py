"""
Modelo para gerenciar comissões parceladas no Firestore
"""
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
        
        Args:
            indication_id: ID da indicação
            ambassador_id: ID da embaixadora
            ambassador_name: Nome da embaixadora
            client_name: Nome do cliente
            
        Returns:
            Lista com os IDs das parcelas criadas
        """
        try:
            base_date = datetime.now()
            total_commission = 900.0
            installment_value = 300.0
            installment_ids = []
            
            # Definir as datas das parcelas
            installment_dates = [
                base_date,  # 1ª parcela: no mesmo mês
                base_date + timedelta(days=30),  # 2ª parcela: 30 dias depois
                base_date + timedelta(days=90)   # 3ª parcela: 90 dias depois
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
                    "status": "pendente",  # pendente, pago, atrasado
                    "payment_date": None,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now(),
                    "total_commission": total_commission,
                    "notes": ""
                }
                
                # Adicionar ao Firestore
                doc_ref, _ = self.db.collection(self.collection_name).add(installment_data)
                installment_ids.append(doc_ref.id)
                
                print(f"Parcela {i} criada: R$ {installment_value} - Vencimento: {due_date.strftime('%d/%m/%Y')}")
            
            return installment_ids
            
        except Exception as e:
            print(f"Erro ao criar parcelas: {str(e)}")
            raise e
    
    def get_installments_by_indication(self, indication_id: str) -> List[Dict[str, Any]]:
        """
        Busca todas as parcelas de uma indicação específica
        
        Args:
            indication_id: ID da indicação
            
        Returns:
            Lista de parcelas
        """
        try:
            query = self.db.collection(self.collection_name).where(
                field_path="indication_id", op_string="==", value=indication_id
            ).order_by("installment_number")
            
            docs = query.stream()
            installments = []
            
            for doc in docs:
                installment_data = doc.to_dict()
                installment_data["id"] = doc.id
                installments.append(installment_data)
            
            return installments
            
        except Exception as e:
            print(f"Erro ao buscar parcelas da indicação {indication_id}: {str(e)}")
            return []
    
    def get_installments_by_ambassador(self, ambassador_id: str, 
                                     status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Busca todas as parcelas de uma embaixadora
        
        Args:
            ambassador_id: ID da embaixadora
            status_filter: Filtro por status (opcional)
            
        Returns:
            Lista de parcelas
        """
        try:
            print(f"Buscando parcelas para embaixadora: {ambassador_id}")
            
            query = self.db.collection(self.collection_name).where(
                field_path="ambassador_id", op_string="==", value=ambassador_id
            )
            
            if status_filter:
                query = query.where(field_path="status", op_string="==", value=status_filter)
            
            # Tentar ordenar por data de vencimento
            try:
                query = query.order_by("due_date")
            except Exception as order_error:
                print(f"Erro ao ordenar por due_date: {order_error}")
                # Se não conseguir ordenar, continuar sem ordenação
                pass
                
            docs = query.stream()
            installments = []
            
            for doc in docs:
                installment_data = doc.to_dict()
                installment_data["id"] = doc.id
                installments.append(installment_data)
                print(f"Parcela encontrada: {doc.id} - Valor: {installment_data.get('value')} - Status: {installment_data.get('status')}")
            
            print(f"Total de parcelas encontradas para embaixadora {ambassador_id}: {len(installments)}")
            return installments
            
        except Exception as e:
            print(f"Erro ao buscar parcelas da embaixadora {ambassador_id}: {str(e)}")
            return []
    
    def get_all_installments(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Busca todas as parcelas com filtros opcionais

        Args:
            filters: Dicionário com filtros (status, ambassador_id, month, year)

        Returns:
            Lista de parcelas
        """
        try:
            query = self.db.collection(self.collection_name)

            # Aplicar filtros diretos no Firestore quando possível
            if filters:
                status = filters.get("status")
                ambassador_id = filters.get("ambassador_id")
                
                # Aplicar filtros que podem ser feitos no Firestore
                if status:
                    query = query.where(field_path="status", op_string="==", value=status)
                
                if ambassador_id:
                    query = query.where(field_path="ambassador_id", op_string="==", value=ambassador_id)

            # Ordenar por data de vencimento
            try:
                query = query.order_by("due_date", direction=firestore.Query.DESCENDING)
            except Exception as order_error:
                print(f"Erro ao ordenar por due_date: {order_error}")
                # Se não conseguir ordenar, continuar sem ordenação
                pass

            # Executar consulta
            docs = query.stream()

            # Coletar documentos
            installments = []
            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id
                installments.append(data)

            # Aplicar filtros de data em memória (month/year)
            if filters:
                month = filters.get("month")
                year = filters.get("year")

                if month:
                    try:
                        month = int(month)
                    except (ValueError, TypeError):
                        month = None
                        
                if year:
                    try:
                        year = int(year)
                    except (ValueError, TypeError):
                        year = None

                if month or year:
                    filtered_installments = []
                    for item in installments:
                        due_date = item.get("due_date")
                        
                        # Verificar se a data existe e é válida
                        if not due_date or not isinstance(due_date, datetime):
                            continue
                        
                        # Aplicar filtros de data
                        if month and due_date.month != month:
                            continue
                        
                        if year and due_date.year != year:
                            continue
                            
                        filtered_installments.append(item)
                    
                    installments = filtered_installments

            print(f"Retornando {len(installments)} parcelas")
            return installments

        except Exception as e:
            print(f"Erro ao buscar todas as parcelas: {str(e)}")
            return []

    
    def update_installment_status(self, installment_id: str, new_status: str, 
                                payment_date: Optional[datetime] = None, 
                                notes: Optional[str] = None) -> bool:
        """
        Atualiza o status de uma parcela
        
        Args:
            installment_id: ID da parcela
            new_status: Novo status (pendente, pago, atrasado)
            payment_date: Data do pagamento (opcional)
            notes: Observações (opcional)
            
        Returns:
            True se atualizado com sucesso
        """
        try:
            if new_status not in ["pendente", "pago", "atrasado"]:
                raise ValueError("Status inválido. Use: pendente, pago, atrasado")
            
            update_data = {
                "status": new_status,
                "updated_at": datetime.now()
            }
            
            if payment_date:
                update_data["payment_date"] = payment_date
            
            if notes is not None:
                update_data["notes"] = notes
            
            # Se marcando como pago e não tem data de pagamento, usar data atual
            if new_status == "pago" and not payment_date:
                update_data["payment_date"] = datetime.now()
            
            self.db.collection(self.collection_name).document(installment_id).update(update_data)
            print(f"Parcela {installment_id} atualizada para status: {new_status}")
            return True
            
        except Exception as e:
            print(f"Erro ao atualizar parcela {installment_id}: {str(e)}")
            return False
    
    def check_overdue_installments(self) -> List[Dict[str, Any]]:
        """
        Verifica e marca parcelas em atraso
        
        Returns:
            Lista de parcelas que foram marcadas como atrasadas
        """
        try:
            current_date = datetime.now()
            
            # Buscar parcelas pendentes com data de vencimento passada
            query = self.db.collection(self.collection_name).where(
                field_path="status", op_string="==", value="pendente"
            )
            
            docs = query.stream()
            overdue_installments = []
            
            for doc in docs:
                installment_data = doc.to_dict()
                due_date = installment_data.get("due_date")
                
                if due_date and due_date < current_date:
                    # Marcar como atrasada
                    self.update_installment_status(doc.id, "atrasado")
                    installment_data["id"] = doc.id
                    overdue_installments.append(installment_data)
            
            return overdue_installments
            
        except Exception as e:
            print(f"Erro ao verificar parcelas em atraso: {str(e)}")
            return []
    
    def get_commission_summary(self, ambassador_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Gera resumo das comissões
        
        Args:
            ambassador_id: ID da embaixadora (opcional, se None retorna resumo geral)
            
        Returns:
            Dicionário com resumo das comissões
        """
        try:
            query = self.db.collection(self.collection_name)
            
            if ambassador_id:
                query = query.where(field_path="ambassador_id", op_string="==", value=ambassador_id)
            
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
                installment_data = doc.to_dict()
                value = installment_data.get("value", 0.0)
                status = installment_data.get("status", "pendente")
                
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

