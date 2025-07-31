#!/usr/bin/env python3
"""
Script de teste para validar o sistema de comissões parceladas do Beepy
"""

import requests
import json
from datetime import datetime, timedelta
import sys

# Configurações
API_BASE_URL = "http://localhost:10000"
TEST_USER_EMAIL = "admin@beepy.com"
TEST_USER_PASSWORD = "admin123"

class BeepyTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        
    def login(self):
        """Realiza login no sistema"""
        print("🔐 Realizando login...")
        
        login_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
        
        try:
            response = self.session.post(
                f"{API_BASE_URL}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_id = data.get("user", {}).get("id")
                print(f"✅ Login realizado com sucesso! User ID: {self.user_id}")
                return True
            else:
                print(f"❌ Erro no login: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            return False
    
    def get_headers(self):
        """Retorna headers com autenticação"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def create_test_indication(self):
        """Cria uma indicação de teste"""
        print("\n📝 Criando indicação de teste...")
        
        indication_data = {
            "clientName": "Cliente Teste Comissão",
            "clientEmail": "cliente.teste@email.com",
            "clientPhone": "(11) 99999-9999",
            "origin": "website",
            "segment": "tecnologia"
        }
        
        try:
            response = self.session.post(
                f"{API_BASE_URL}/indications",
                json=indication_data,
                headers=self.get_headers()
            )
            
            if response.status_code == 201:
                data = response.json()
                indication_id = data.get("id")
                print(f"✅ Indicação criada com sucesso! ID: {indication_id}")
                return indication_id
            else:
                print(f"❌ Erro ao criar indicação: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Erro na criação da indicação: {e}")
            return None
    
    def approve_indication(self, indication_id):
        """Aprova uma indicação para gerar comissões"""
        print(f"\n✅ Aprovando indicação {indication_id}...")
        
        try:
            response = self.session.put(
                f"{API_BASE_URL}/indications/{indication_id}/status",
                json={"status": "aprovado"},
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                print("✅ Indicação aprovada com sucesso!")
                return True
            else:
                print(f"❌ Erro ao aprovar indicação: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erro na aprovação da indicação: {e}")
            return False
    
    def get_commissions(self):
        """Busca todas as comissões"""
        print("\n💰 Buscando comissões...")
        
        try:
            response = self.session.get(
                f"{API_BASE_URL}/commissions",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    commissions = data.get("commissions", [])
                    print(f"✅ Encontradas {len(commissions)} comissões")
                    return commissions
                else:
                    print(f"❌ Erro na resposta: {data.get('message')}")
                    return []
            else:
                print(f"❌ Erro ao buscar comissões: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Erro na busca de comissões: {e}")
            return []
    
    def validate_commission_parcels(self, commissions, indication_id):
        """Valida se as 3 parcelas foram criadas corretamente"""
        print(f"\n🔍 Validando parcelas para indicação {indication_id}...")
        
        # Filtrar comissões da indicação específica
        indication_commissions = [c for c in commissions if c.get("indication_id") == indication_id]
        
        if len(indication_commissions) != 3:
            print(f"❌ Erro: Esperadas 3 parcelas, encontradas {len(indication_commissions)}")
            return False
        
        # Verificar se todas as parcelas têm R$ 300,00
        for i, commission in enumerate(indication_commissions, 1):
            amount = commission.get("amount", 0)
            parcel_number = commission.get("parcel_number", 0)
            status = commission.get("payment_status", "")
            due_date = commission.get("due_date", "")
            
            print(f"  Parcela {parcel_number}: R$ {amount:.2f} - Status: {status} - Vencimento: {due_date}")
            
            if amount != 300.0:
                print(f"❌ Erro: Parcela {parcel_number} deveria ter R$ 300,00, mas tem R$ {amount:.2f}")
                return False
            
            if status != "pendente":
                print(f"❌ Erro: Parcela {parcel_number} deveria estar pendente, mas está {status}")
                return False
        
        print("✅ Todas as parcelas estão corretas!")
        return True
    
    def test_commission_status_update(self, commissions, indication_id):
        """Testa a atualização de status de uma comissão"""
        print(f"\n🔄 Testando atualização de status...")
        
        # Pegar a primeira parcela da indicação
        indication_commissions = [c for c in commissions if c.get("indication_id") == indication_id]
        if not indication_commissions:
            print("❌ Nenhuma comissão encontrada para testar")
            return False
        
        commission_id = indication_commissions[0].get("id")
        
        try:
            # Marcar como pago
            response = self.session.put(
                f"{API_BASE_URL}/commissions/{commission_id}",
                json={"payment_status": "pago"},
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                print("✅ Status atualizado para 'pago' com sucesso!")
                
                # Verificar se a atualização foi persistida
                updated_commissions = self.get_commissions()
                updated_commission = next((c for c in updated_commissions if c.get("id") == commission_id), None)
                
                if updated_commission and updated_commission.get("payment_status") == "pago":
                    print("✅ Status persistido corretamente!")
                    return True
                else:
                    print("❌ Status não foi persistido corretamente")
                    return False
            else:
                print(f"❌ Erro ao atualizar status: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erro na atualização de status: {e}")
            return False
    
    def run_tests(self):
        """Executa todos os testes"""
        print("🚀 Iniciando testes do sistema de comissões parceladas...")
        print("=" * 60)
        
        # 1. Login
        if not self.login():
            print("❌ Falha no login. Encerrando testes.")
            return False
        
        # 2. Criar indicação
        indication_id = self.create_test_indication()
        if not indication_id:
            print("❌ Falha na criação da indicação. Encerrando testes.")
            return False
        
        # 3. Aprovar indicação (deve gerar comissões)
        if not self.approve_indication(indication_id):
            print("❌ Falha na aprovação da indicação. Encerrando testes.")
            return False
        
        # 4. Buscar comissões
        commissions = self.get_commissions()
        if not commissions:
            print("❌ Nenhuma comissão encontrada. Encerrando testes.")
            return False
        
        # 5. Validar parcelas
        if not self.validate_commission_parcels(commissions, indication_id):
            print("❌ Falha na validação das parcelas. Encerrando testes.")
            return False
        
        # 6. Testar atualização de status
        if not self.test_commission_status_update(commissions, indication_id):
            print("❌ Falha no teste de atualização de status.")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 Todos os testes passaram com sucesso!")
        print("✅ Sistema de comissões parceladas está funcionando corretamente!")
        return True

def main():
    """Função principal"""
    tester = BeepyTester()
    
    try:
        success = tester.run_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Testes interrompidos pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

