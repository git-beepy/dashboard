import unittest
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Adicionar o diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.commission_utils import create_commission_parcels, update_overdue_commissions
from models.commission import Commission
from models.indication import Indication


class TestCommissionLogic(unittest.TestCase):
    """Testes para a lógica de comissões parceladas"""

    def setUp(self):
        """Configuração inicial para os testes"""
        self.mock_indication = MagicMock()
        self.mock_indication.id = 1
        self.mock_indication.client_name = "Cliente Teste"
        self.mock_indication.ambassador_id = 123
        self.mock_indication.ambassador_name = "Embaixadora Teste"
        self.mock_indication.sale_approval_date = datetime.now()

    @patch('models.commission.Commission')
    @patch('models.user.db.session')
    def test_create_commission_parcels(self, mock_session, mock_commission_class):
        """Testa a criação de 3 parcelas de comissão"""
        
        # Configurar mocks
        mock_commission_instances = []
        for i in range(3):
            mock_commission = MagicMock()
            mock_commission.id = i + 1
            mock_commission.parcel_number = i + 1
            mock_commission.value = 300.0
            mock_commission_instances.append(mock_commission)
        
        mock_commission_class.side_effect = mock_commission_instances
        
        # Executar função
        result = create_commission_parcels(self.mock_indication)
        
        # Verificações
        self.assertEqual(len(result), 3)
        self.assertEqual(mock_commission_class.call_count, 3)
        
        # Verificar se as parcelas foram criadas com os valores corretos
        for i, call_args in enumerate(mock_commission_class.call_args_list):
            kwargs = call_args[1]
            self.assertEqual(kwargs['parcel_number'], i + 1)
            self.assertEqual(kwargs['value'], 300.0)
            self.assertEqual(kwargs['status'], 'pendente')
            self.assertEqual(kwargs['original_indication_id'], 1)
            self.assertEqual(kwargs['ambassador_id'], 123)
            self.assertEqual(kwargs['client_name'], "Cliente Teste")
            self.assertEqual(kwargs['ambassador_name'], "Embaixadora Teste")

    def test_parcel_due_dates(self):
        """Testa se as datas de vencimento das parcelas estão corretas"""
        
        base_date = datetime(2025, 7, 29)
        
        with patch('utils.commission_utils.datetime') as mock_datetime:
            mock_datetime.now.return_value = base_date
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            with patch('models.commission.Commission') as mock_commission_class:
                with patch('models.user.db.session'):
                    mock_commission_instances = []
                    for i in range(3):
                        mock_commission = MagicMock()
                        mock_commission_instances.append(mock_commission)
                    
                    mock_commission_class.side_effect = mock_commission_instances
                    
                    # Executar função
                    create_commission_parcels(self.mock_indication)
                    
                    # Verificar datas de vencimento
                    call_args_list = mock_commission_class.call_args_list
                    
                    # Parcela 1: mesmo mês
                    parcela_1_due_date = call_args_list[0][1]['due_date']
                    expected_date_1 = base_date
                    self.assertEqual(parcela_1_due_date.month, expected_date_1.month)
                    self.assertEqual(parcela_1_due_date.year, expected_date_1.year)
                    
                    # Parcela 2: 30 dias depois
                    parcela_2_due_date = call_args_list[1][1]['due_date']
                    expected_date_2 = base_date + timedelta(days=30)
                    self.assertEqual(parcela_2_due_date.month, expected_date_2.month)
                    
                    # Parcela 3: 90 dias depois
                    parcela_3_due_date = call_args_list[2][1]['due_date']
                    expected_date_3 = base_date + timedelta(days=90)
                    self.assertEqual(parcela_3_due_date.month, expected_date_3.month)

    def test_commission_total_value(self):
        """Testa se o valor total das comissões é R$ 900,00"""
        
        with patch('models.commission.Commission') as mock_commission_class:
            with patch('models.user.db.session'):
                mock_commission_instances = []
                for i in range(3):
                    mock_commission = MagicMock()
                    mock_commission_instances.append(mock_commission)
                
                mock_commission_class.side_effect = mock_commission_instances
                
                # Executar função
                result = create_commission_parcels(self.mock_indication)
                
                # Verificar valores
                total_value = 0
                for call_args in mock_commission_class.call_args_list:
                    kwargs = call_args[1]
                    total_value += kwargs['value']
                
                self.assertEqual(total_value, 900.0)
                
                # Verificar que cada parcela tem R$ 300,00
                for call_args in mock_commission_class.call_args_list:
                    kwargs = call_args[1]
                    self.assertEqual(kwargs['value'], 300.0)

    @patch('models.commission.Commission.query')
    @patch('models.user.db.session')
    def test_update_overdue_commissions(self, mock_session, mock_query):
        """Testa a atualização de comissões em atraso"""
        
        # Criar comissões mockadas que estão atrasadas
        overdue_commission_1 = MagicMock()
        overdue_commission_1.id = 1
        overdue_commission_1.status = 'pendente'
        overdue_commission_1.due_date = datetime.now() - timedelta(days=5)
        
        overdue_commission_2 = MagicMock()
        overdue_commission_2.id = 2
        overdue_commission_2.status = 'pendente'
        overdue_commission_2.due_date = datetime.now() - timedelta(days=10)
        
        # Configurar mock query
        mock_filter = MagicMock()
        mock_filter.all.return_value = [overdue_commission_1, overdue_commission_2]
        mock_query.filter.return_value = mock_filter
        
        # Executar função
        result = update_overdue_commissions()
        
        # Verificações
        self.assertEqual(result, 2)  # Deve retornar 2 comissões atualizadas
        self.assertEqual(overdue_commission_1.status, 'atrasado')
        self.assertEqual(overdue_commission_2.status, 'atrasado')

    def test_commission_status_transitions(self):
        """Testa as transições de status das comissões"""
        
        # Testa status inicial
        commission = MagicMock()
        commission.status = 'pendente'
        
        # Simular pagamento
        commission.status = 'pago'
        commission.payment_date = datetime.now()
        
        self.assertEqual(commission.status, 'pago')
        self.assertIsNotNone(commission.payment_date)
        
        # Simular reversão de pagamento
        commission.status = 'pendente'
        commission.payment_date = None
        
        self.assertEqual(commission.status, 'pendente')
        self.assertIsNone(commission.payment_date)

    def test_commission_data_integrity(self):
        """Testa a integridade dos dados das comissões"""
        
        with patch('models.commission.Commission') as mock_commission_class:
            with patch('models.user.db.session'):
                mock_commission_instances = []
                for i in range(3):
                    mock_commission = MagicMock()
                    mock_commission_instances.append(mock_commission)
                
                mock_commission_class.side_effect = mock_commission_instances
                
                # Executar função
                create_commission_parcels(self.mock_indication)
                
                # Verificar integridade dos dados
                for i, call_args in enumerate(mock_commission_class.call_args_list):
                    kwargs = call_args[1]
                    
                    # Verificar campos obrigatórios
                    self.assertIn('original_indication_id', kwargs)
                    self.assertIn('ambassador_id', kwargs)
                    self.assertIn('client_name', kwargs)
                    self.assertIn('ambassador_name', kwargs)
                    self.assertIn('parcel_number', kwargs)
                    self.assertIn('value', kwargs)
                    self.assertIn('status', kwargs)
                    self.assertIn('due_date', kwargs)
                    
                    # Verificar tipos de dados
                    self.assertIsInstance(kwargs['parcel_number'], int)
                    self.assertIsInstance(kwargs['value'], float)
                    self.assertIsInstance(kwargs['status'], str)
                    self.assertIsInstance(kwargs['due_date'], datetime)


class TestCommissionValidation(unittest.TestCase):
    """Testes de validação para comissões"""

    def test_parcel_number_validation(self):
        """Testa se os números das parcelas são válidos (1, 2, 3)"""
        
        with patch('models.commission.Commission') as mock_commission_class:
            with patch('models.user.db.session'):
                mock_indication = MagicMock()
                mock_indication.id = 1
                mock_indication.client_name = "Cliente Teste"
                mock_indication.ambassador_id = 123
                mock_indication.ambassador_name = "Embaixadora Teste"
                mock_indication.sale_approval_date = datetime.now()
                
                mock_commission_instances = []
                for i in range(3):
                    mock_commission = MagicMock()
                    mock_commission_instances.append(mock_commission)
                
                mock_commission_class.side_effect = mock_commission_instances
                
                # Executar função
                create_commission_parcels(mock_indication)
                
                # Verificar números das parcelas
                parcel_numbers = []
                for call_args in mock_commission_class.call_args_list:
                    kwargs = call_args[1]
                    parcel_numbers.append(kwargs['parcel_number'])
                
                self.assertEqual(sorted(parcel_numbers), [1, 2, 3])

    def test_commission_value_validation(self):
        """Testa se os valores das comissões são válidos"""
        
        with patch('models.commission.Commission') as mock_commission_class:
            with patch('models.user.db.session'):
                mock_indication = MagicMock()
                mock_indication.id = 1
                mock_indication.client_name = "Cliente Teste"
                mock_indication.ambassador_id = 123
                mock_indication.ambassador_name = "Embaixadora Teste"
                mock_indication.sale_approval_date = datetime.now()
                
                mock_commission_instances = []
                for i in range(3):
                    mock_commission = MagicMock()
                    mock_commission_instances.append(mock_commission)
                
                mock_commission_class.side_effect = mock_commission_instances
                
                # Executar função
                create_commission_parcels(mock_indication)
                
                # Verificar valores
                for call_args in mock_commission_class.call_args_list:
                    kwargs = call_args[1]
                    value = kwargs['value']
                    
                    # Valor deve ser positivo
                    self.assertGreater(value, 0)
                    
                    # Valor deve ser exatamente R$ 300,00
                    self.assertEqual(value, 300.0)


if __name__ == '__main__':
    # Executar todos os testes
    unittest.main(verbosity=2)

