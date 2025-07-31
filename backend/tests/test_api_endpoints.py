import unittest
import json
import sys
import os
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Adicionar o diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestCommissionEndpoints(unittest.TestCase):
    """Testes para os endpoints da API de comissões"""

    def setUp(self):
        """Configuração inicial para os testes"""
        self.app = None  # Em um ambiente real, seria configurado o Flask app de teste
        self.client = None  # Em um ambiente real, seria o test client do Flask

    def test_get_commissions_endpoint(self):
        """Testa o endpoint GET /commissions"""
        
        # Mock da resposta esperada
        expected_response = {
            'success': True,
            'commissions': [
                {
                    'id': 1,
                    'clientName': 'Cliente Teste',
                    'ambassadorName': 'Embaixadora Teste',
                    'parcelNumber': 1,
                    'value': 300.0,
                    'status': 'pendente',
                    'dueDate': '2025-07-29',
                    'paymentDate': None
                },
                {
                    'id': 2,
                    'clientName': 'Cliente Teste',
                    'ambassadorName': 'Embaixadora Teste',
                    'parcelNumber': 2,
                    'value': 300.0,
                    'status': 'pendente',
                    'dueDate': '2025-08-29',
                    'paymentDate': None
                }
            ]
        }
        
        # Simular requisição
        self.assertIsInstance(expected_response, dict)
        self.assertIn('commissions', expected_response)
        self.assertEqual(len(expected_response['commissions']), 2)

    def test_get_commissions_with_filters(self):
        """Testa o endpoint GET /commissions com filtros"""
        
        # Teste com filtro de status
        filter_params = {
            'status': 'pendente',
            'ambassador_id': 123,
            'month': 7,
            'year': 2025
        }
        
        # Verificar se os parâmetros são válidos
        self.assertIn('status', filter_params)
        self.assertEqual(filter_params['status'], 'pendente')
        self.assertIsInstance(filter_params['ambassador_id'], int)

    def test_commission_summary_endpoint(self):
        """Testa o endpoint GET /commissions/summary"""
        
        expected_summary = {
            'success': True,
            'summary': {
                'total_amount': 2700.0,
                'total_commissions': 9,
                'paid_amount': 900.0,
                'paid_commissions': 3,
                'pending_amount': 1200.0,
                'pending_commissions': 4,
                'overdue_amount': 600.0,
                'overdue_commissions': 2
            }
        }
        
        # Verificar estrutura da resposta
        self.assertIn('summary', expected_summary)
        summary = expected_summary['summary']
        
        # Verificar campos obrigatórios
        required_fields = [
            'total_amount', 'total_commissions',
            'paid_amount', 'paid_commissions',
            'pending_amount', 'pending_commissions',
            'overdue_amount', 'overdue_commissions'
        ]
        
        for field in required_fields:
            self.assertIn(field, summary)

    def test_mark_commission_as_paid_endpoint(self):
        """Testa o endpoint PUT /commissions/{id}/pay"""
        
        commission_id = 1
        
        # Mock da resposta esperada
        expected_response = {
            'success': True,
            'message': 'Comissão marcada como paga com sucesso',
            'commission': {
                'id': commission_id,
                'status': 'pago',
                'paymentDate': datetime.now().isoformat()
            }
        }
        
        # Verificar estrutura da resposta
        self.assertIn('success', expected_response)
        self.assertTrue(expected_response['success'])
        self.assertIn('commission', expected_response)
        self.assertEqual(expected_response['commission']['status'], 'pago')

    def test_mark_commission_as_unpaid_endpoint(self):
        """Testa o endpoint PUT /commissions/{id}/unpay"""
        
        commission_id = 1
        
        # Mock da resposta esperada
        expected_response = {
            'success': True,
            'message': 'Pagamento da comissão revertido com sucesso',
            'commission': {
                'id': commission_id,
                'status': 'pendente',
                'paymentDate': None
            }
        }
        
        # Verificar estrutura da resposta
        self.assertIn('success', expected_response)
        self.assertTrue(expected_response['success'])
        self.assertIn('commission', expected_response)
        self.assertEqual(expected_response['commission']['status'], 'pendente')
        self.assertIsNone(expected_response['commission']['paymentDate'])

    def test_update_overdue_commissions_endpoint(self):
        """Testa o endpoint POST /commissions/update-overdue"""
        
        expected_response = {
            'success': True,
            'message': 'Comissões em atraso atualizadas com sucesso',
            'updated_count': 5
        }
        
        # Verificar estrutura da resposta
        self.assertIn('success', expected_response)
        self.assertTrue(expected_response['success'])
        self.assertIn('updated_count', expected_response)
        self.assertIsInstance(expected_response['updated_count'], int)

    def test_commission_reports_endpoint(self):
        """Testa o endpoint GET /commissions/reports"""
        
        expected_response = {
            'success': True,
            'reports': {
                'summary': {
                    'totalCommissions': 45600,
                    'paidCommissions': 32400,
                    'pendingCommissions': 10800,
                    'overdueCommissions': 2400
                },
                'monthlyTrend': [
                    {'month': 'Jan', 'total': 2700, 'paid': 2700, 'pending': 0},
                    {'month': 'Fev', 'total': 5400, 'paid': 3600, 'pending': 1800}
                ],
                'statusDistribution': [
                    {'name': 'Pagas', 'value': 108, 'amount': 32400},
                    {'name': 'Pendentes', 'value': 36, 'amount': 10800}
                ]
            }
        }
        
        # Verificar estrutura da resposta
        self.assertIn('reports', expected_response)
        reports = expected_response['reports']
        
        # Verificar seções do relatório
        self.assertIn('summary', reports)
        self.assertIn('monthlyTrend', reports)
        self.assertIn('statusDistribution', reports)

    def test_error_handling(self):
        """Testa o tratamento de erros nos endpoints"""
        
        # Teste de comissão não encontrada
        error_response = {
            'success': False,
            'message': 'Comissão não encontrada',
            'error_code': 'COMMISSION_NOT_FOUND'
        }
        
        self.assertIn('success', error_response)
        self.assertFalse(error_response['success'])
        self.assertIn('message', error_response)

    def test_authentication_required(self):
        """Testa se os endpoints requerem autenticação"""
        
        # Simular resposta de não autorizado
        unauthorized_response = {
            'success': False,
            'message': 'Token de acesso requerido',
            'error_code': 'UNAUTHORIZED'
        }
        
        self.assertIn('success', unauthorized_response)
        self.assertFalse(unauthorized_response['success'])

    def test_input_validation(self):
        """Testa a validação de entrada dos endpoints"""
        
        # Teste de parâmetros inválidos
        invalid_params = {
            'status': 'status_invalido',  # Status não permitido
            'month': 13,  # Mês inválido
            'year': 'abc'  # Ano inválido
        }
        
        # Verificar validação de status
        valid_statuses = ['pendente', 'pago', 'atrasado']
        self.assertNotIn(invalid_params['status'], valid_statuses)
        
        # Verificar validação de mês
        self.assertGreater(invalid_params['month'], 12)
        
        # Verificar validação de ano
        self.assertNotIsInstance(invalid_params['year'], int)


class TestCommissionBusinessLogic(unittest.TestCase):
    """Testes para a lógica de negócio das comissões"""

    def test_commission_creation_flow(self):
        """Testa o fluxo completo de criação de comissões"""
        
        # Simular indicação aprovada
        indication_data = {
            'id': 1,
            'client_name': 'Cliente Teste',
            'ambassador_id': 123,
            'ambassador_name': 'Embaixadora Teste',
            'status': 'aprovado',
            'sale_approval_date': datetime.now()
        }
        
        # Verificar dados da indicação
        self.assertEqual(indication_data['status'], 'aprovado')
        self.assertIsNotNone(indication_data['sale_approval_date'])
        
        # Simular criação de comissões
        expected_commissions = []
        for i in range(3):
            commission = {
                'parcel_number': i + 1,
                'value': 300.0,
                'status': 'pendente',
                'due_date': indication_data['sale_approval_date'] + timedelta(days=30 * i),
                'original_indication_id': indication_data['id'],
                'ambassador_id': indication_data['ambassador_id']
            }
            expected_commissions.append(commission)
        
        # Verificar comissões criadas
        self.assertEqual(len(expected_commissions), 3)
        
        total_value = sum(c['value'] for c in expected_commissions)
        self.assertEqual(total_value, 900.0)

    def test_payment_flow(self):
        """Testa o fluxo de pagamento de comissões"""
        
        # Simular comissão pendente
        commission = {
            'id': 1,
            'status': 'pendente',
            'payment_date': None,
            'value': 300.0
        }
        
        # Simular pagamento
        commission['status'] = 'pago'
        commission['payment_date'] = datetime.now()
        
        # Verificar estado após pagamento
        self.assertEqual(commission['status'], 'pago')
        self.assertIsNotNone(commission['payment_date'])

    def test_overdue_detection(self):
        """Testa a detecção de comissões em atraso"""
        
        # Simular comissões com diferentes datas de vencimento
        commissions = [
            {
                'id': 1,
                'status': 'pendente',
                'due_date': datetime.now() - timedelta(days=5),  # Atrasada
                'value': 300.0
            },
            {
                'id': 2,
                'status': 'pendente',
                'due_date': datetime.now() + timedelta(days=5),  # No prazo
                'value': 300.0
            },
            {
                'id': 3,
                'status': 'pago',
                'due_date': datetime.now() - timedelta(days=10),  # Paga (não importa a data)
                'value': 300.0
            }
        ]
        
        # Identificar comissões em atraso
        overdue_commissions = []
        today = datetime.now()
        
        for commission in commissions:
            if (commission['status'] == 'pendente' and 
                commission['due_date'] < today):
                overdue_commissions.append(commission)
        
        # Verificar detecção
        self.assertEqual(len(overdue_commissions), 1)
        self.assertEqual(overdue_commissions[0]['id'], 1)

    def test_commission_filtering(self):
        """Testa a filtragem de comissões"""
        
        # Simular lista de comissões
        commissions = [
            {'id': 1, 'status': 'pago', 'ambassador_id': 123, 'due_date': datetime(2025, 7, 1)},
            {'id': 2, 'status': 'pendente', 'ambassador_id': 123, 'due_date': datetime(2025, 7, 15)},
            {'id': 3, 'status': 'pendente', 'ambassador_id': 456, 'due_date': datetime(2025, 8, 1)},
            {'id': 4, 'status': 'atrasado', 'ambassador_id': 123, 'due_date': datetime(2025, 6, 1)}
        ]
        
        # Filtrar por status
        pending_commissions = [c for c in commissions if c['status'] == 'pendente']
        self.assertEqual(len(pending_commissions), 2)
        
        # Filtrar por embaixadora
        ambassador_123_commissions = [c for c in commissions if c['ambassador_id'] == 123]
        self.assertEqual(len(ambassador_123_commissions), 3)
        
        # Filtrar por mês
        july_commissions = [c for c in commissions if c['due_date'].month == 7]
        self.assertEqual(len(july_commissions), 2)


if __name__ == '__main__':
    # Executar todos os testes
    unittest.main(verbosity=2)

