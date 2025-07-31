"""
Testes para o sistema de validação
"""
import pytest
from validators import (
    EmailValidator, PhoneValidator, PasswordValidator, 
    UserValidator, IndicationValidator, CommissionValidator,
    validate_request_data, ValidationError
)

class TestEmailValidator:
    """Testes para validação de email"""
    
    def test_valid_email(self):
        validator = EmailValidator()
        assert validator.validate('teste@exemplo.com') == True
        assert validator.is_valid() == True
    
    def test_invalid_email_format(self):
        validator = EmailValidator()
        assert validator.validate('email_invalido') == False
        assert len(validator.get_errors()) > 0
        assert validator.get_errors()[0]['code'] == 'invalid_format'
    
    def test_empty_email(self):
        validator = EmailValidator()
        assert validator.validate('') == False
        assert validator.get_errors()[0]['code'] == 'required'
    
    def test_none_email(self):
        validator = EmailValidator()
        assert validator.validate(None) == False
        assert validator.get_errors()[0]['code'] == 'required'

class TestPhoneValidator:
    """Testes para validação de telefone"""
    
    def test_valid_brazilian_phone(self):
        validator = PhoneValidator()
        assert validator.validate('+5511999999999') == True
        assert validator.is_valid() == True
    
    def test_valid_phone_without_country_code(self):
        validator = PhoneValidator()
        assert validator.validate('11999999999', country_code='BR') == True
    
    def test_invalid_phone_format(self):
        validator = PhoneValidator()
        assert validator.validate('123') == False
        assert len(validator.get_errors()) > 0
    
    def test_empty_phone(self):
        validator = PhoneValidator()
        assert validator.validate('') == False
        assert validator.get_errors()[0]['code'] == 'required'

class TestPasswordValidator:
    """Testes para validação de senha"""
    
    def test_valid_password(self):
        validator = PasswordValidator(min_length=6, require_special=False)
        assert validator.validate('Senha123') == True
        assert validator.is_valid() == True
    
    def test_password_too_short(self):
        validator = PasswordValidator(min_length=8)
        assert validator.validate('123') == False
        assert validator.get_errors()[0]['code'] == 'too_short'
    
    def test_password_no_uppercase(self):
        validator = PasswordValidator(require_uppercase=True)
        assert validator.validate('senha123') == False
        assert validator.get_errors()[0]['code'] == 'no_uppercase'
    
    def test_password_no_lowercase(self):
        validator = PasswordValidator(require_lowercase=True)
        assert validator.validate('SENHA123') == False
        assert validator.get_errors()[0]['code'] == 'no_lowercase'
    
    def test_password_no_numbers(self):
        validator = PasswordValidator(require_numbers=True)
        assert validator.validate('SenhaABC') == False
        assert validator.get_errors()[0]['code'] == 'no_numbers'
    
    def test_password_no_special_chars(self):
        validator = PasswordValidator(require_special=True)
        assert validator.validate('Senha123') == False
        assert validator.get_errors()[0]['code'] == 'no_special'
    
    def test_empty_password(self):
        validator = PasswordValidator()
        assert validator.validate('') == False
        assert validator.get_errors()[0]['code'] == 'required'

class TestUserValidator:
    """Testes para validação de usuário"""
    
    def test_valid_user_create(self):
        validator = UserValidator()
        data = {
            'name': 'João Silva',
            'email': 'joao@exemplo.com',
            'password': 'senha123',
            'role': 'embaixadora'
        }
        assert validator.validate_create(data) == True
        assert validator.is_valid() == True
    
    def test_user_create_missing_name(self):
        validator = UserValidator()
        data = {
            'email': 'joao@exemplo.com',
            'password': 'senha123',
            'role': 'embaixadora'
        }
        assert validator.validate_create(data) == False
        errors = validator.get_errors()
        assert any(error['field'] == 'name' and error['code'] == 'required' for error in errors)
    
    def test_user_create_short_name(self):
        validator = UserValidator()
        data = {
            'name': 'A',
            'email': 'joao@exemplo.com',
            'password': 'senha123',
            'role': 'embaixadora'
        }
        assert validator.validate_create(data) == False
        errors = validator.get_errors()
        assert any(error['field'] == 'name' and error['code'] == 'too_short' for error in errors)
    
    def test_user_create_invalid_email(self):
        validator = UserValidator()
        data = {
            'name': 'João Silva',
            'email': 'email_invalido',
            'password': 'senha123',
            'role': 'embaixadora'
        }
        assert validator.validate_create(data) == False
        errors = validator.get_errors()
        assert any(error['field'] == 'email' for error in errors)
    
    def test_user_create_invalid_role(self):
        validator = UserValidator()
        data = {
            'name': 'João Silva',
            'email': 'joao@exemplo.com',
            'password': 'senha123',
            'role': 'role_invalida'
        }
        assert validator.validate_create(data) == False
        errors = validator.get_errors()
        assert any(error['field'] == 'role' and error['code'] == 'invalid_choice' for error in errors)
    
    def test_user_update_partial_data(self):
        validator = UserValidator()
        data = {
            'name': 'João Silva Atualizado'
        }
        assert validator.validate_update(data) == True
        assert validator.is_valid() == True
    
    def test_user_update_empty_name(self):
        validator = UserValidator()
        data = {
            'name': ''
        }
        assert validator.validate_update(data) == False
        errors = validator.get_errors()
        assert any(error['field'] == 'name' and error['code'] == 'required' for error in errors)

class TestIndicationValidator:
    """Testes para validação de indicação"""
    
    def test_valid_indication_create(self):
        validator = IndicationValidator()
        data = {
            'clientName': 'Cliente Teste',
            'clientEmail': 'cliente@teste.com',
            'clientPhone': '+5511999999999',
            'segment': 'tecnologia',
            'origin': 'indicacao_pessoal',
            'observations': 'Cliente interessado'
        }
        assert validator.validate_create(data) == True
        assert validator.is_valid() == True
    
    def test_indication_create_missing_client_name(self):
        validator = IndicationValidator()
        data = {
            'clientEmail': 'cliente@teste.com',
            'clientPhone': '+5511999999999',
            'segment': 'tecnologia'
        }
        assert validator.validate_create(data) == False
        errors = validator.get_errors()
        assert any(error['field'] == 'clientName' and error['code'] == 'required' for error in errors)
    
    def test_indication_create_invalid_segment(self):
        validator = IndicationValidator()
        data = {
            'clientName': 'Cliente Teste',
            'clientEmail': 'cliente@teste.com',
            'clientPhone': '+5511999999999',
            'segment': 'segmento_invalido'
        }
        assert validator.validate_create(data) == False
        errors = validator.get_errors()
        assert any(error['field'] == 'segment' and error['code'] == 'invalid_choice' for error in errors)
    
    def test_indication_create_long_observations(self):
        validator = IndicationValidator()
        data = {
            'clientName': 'Cliente Teste',
            'clientEmail': 'cliente@teste.com',
            'clientPhone': '+5511999999999',
            'segment': 'tecnologia',
            'observations': 'x' * 1001  # Mais de 1000 caracteres
        }
        assert validator.validate_create(data) == False
        errors = validator.get_errors()
        assert any(error['field'] == 'observations' and error['code'] == 'too_long' for error in errors)
    
    def test_indication_update_status_valid(self):
        validator = IndicationValidator()
        assert validator.validate_update_status('aprovada') == True
        assert validator.is_valid() == True
    
    def test_indication_update_status_invalid(self):
        validator = IndicationValidator()
        assert validator.validate_update_status('status_invalido') == False
        errors = validator.get_errors()
        assert any(error['field'] == 'status' and error['code'] == 'invalid_choice' for error in errors)

class TestCommissionValidator:
    """Testes para validação de comissão"""
    
    def test_valid_commission_create(self):
        validator = CommissionValidator()
        data = {
            'amount': 100.50,
            'status': 'pendente'
        }
        assert validator.validate_create(data) == True
        assert validator.is_valid() == True
    
    def test_commission_create_missing_amount(self):
        validator = CommissionValidator()
        data = {
            'status': 'pendente'
        }
        assert validator.validate_create(data) == False
        errors = validator.get_errors()
        assert any(error['field'] == 'amount' and error['code'] == 'required' for error in errors)
    
    def test_commission_create_negative_amount(self):
        validator = CommissionValidator()
        data = {
            'amount': -10.0,
            'status': 'pendente'
        }
        assert validator.validate_create(data) == False
        errors = validator.get_errors()
        assert any(error['field'] == 'amount' and error['code'] == 'invalid_value' for error in errors)
    
    def test_commission_create_too_high_amount(self):
        validator = CommissionValidator()
        data = {
            'amount': 200000.0,  # Muito alto
            'status': 'pendente'
        }
        assert validator.validate_create(data) == False
        errors = validator.get_errors()
        assert any(error['field'] == 'amount' and error['code'] == 'too_high' for error in errors)
    
    def test_commission_create_invalid_amount_format(self):
        validator = CommissionValidator()
        data = {
            'amount': 'não_é_número',
            'status': 'pendente'
        }
        assert validator.validate_create(data) == False
        errors = validator.get_errors()
        assert any(error['field'] == 'amount' and error['code'] == 'invalid_format' for error in errors)
    
    def test_commission_create_invalid_status(self):
        validator = CommissionValidator()
        data = {
            'amount': 100.0,
            'status': 'status_invalido'
        }
        assert validator.validate_create(data) == False
        errors = validator.get_errors()
        assert any(error['field'] == 'status' and error['code'] == 'invalid_choice' for error in errors)

class TestValidateRequestData:
    """Testes para função utilitária de validação"""
    
    def test_validate_request_data_success(self):
        data = {
            'name': 'João Silva',
            'email': 'joao@exemplo.com',
            'password': 'senha123',
            'role': 'embaixadora'
        }
        result = validate_request_data(UserValidator, data, 'create')
        assert result['valid'] == True
        assert len(result['errors']) == 0
    
    def test_validate_request_data_failure(self):
        data = {
            'name': '',  # Nome vazio
            'email': 'email_invalido',
            'password': '123',  # Senha muito curta
            'role': 'role_invalida'
        }
        result = validate_request_data(UserValidator, data, 'create')
        assert result['valid'] == False
        assert len(result['errors']) > 0
    
    def test_validate_request_data_invalid_method(self):
        data = {'name': 'Teste'}
        result = validate_request_data(UserValidator, data, 'metodo_inexistente')
        assert result['valid'] == False
        assert len(result['errors']) > 0

