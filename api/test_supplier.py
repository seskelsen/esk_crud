import pytest
import tempfile
import os
import json
from supplier import Supplier
from pathlib import Path

@pytest.fixture
def supplier_instance():
    # Criar um arquivo temporário para o banco de dados
    db_fd, db_path = tempfile.mkstemp()
    os.close(db_fd)  # Fechar o descritor de arquivo

    # Criar uma instância do Supplier com o arquivo temporário
    instance = Supplier(db_path=db_path)
    
    yield instance
    
    # Limpar após os testes
    try:
        os.unlink(db_path)
    except:
        pass

@pytest.fixture
def supplier():
    return Supplier(name='Test Supplier', cnpj='00.000.000/0000-00', email='test@supplier.com', phone='(00) 00000-0000')

def test_create_supplier(supplier_instance):
    """Testa a criação de um fornecedor"""
    supplier_data = {
        'name': 'Empresa Teste',
        'cnpj': '12345678901234',
        'email': 'teste@empresa.com',
        'phone': '11999999999'
    }
    
    result = supplier_instance.create(supplier_data)
    
    assert result is not None
    assert result['name'] == supplier_data['name']
    assert result['cnpj'] == supplier_data['cnpj']
    assert result['email'] == supplier_data['email']
    assert result['phone'] == supplier_data['phone']
    assert result['id'].startswith('sup_')

def test_get_supplier(supplier_instance):
    """Testa a busca de um fornecedor"""
    # Primeiro cria um fornecedor
    supplier_data = {
        'name': 'Empresa Teste',
        'cnpj': '12345678901234',
        'email': 'teste@empresa.com',
        'phone': '11999999999'
    }
    created = supplier_instance.create(supplier_data)
    
    # Depois busca o fornecedor criado
    result = supplier_instance.get(created['id'])
    
    assert result is not None
    assert result['id'] == created['id']
    assert result['name'] == supplier_data['name']
    assert result['cnpj'] == supplier_data['cnpj']

def test_get_all_suppliers(supplier_instance):
    """Testa a listagem de todos os fornecedores"""
    # Criar alguns fornecedores para testar
    suppliers = [
        {
            'name': 'Empresa A',
            'cnpj': '11111111111111',
            'email': 'a@empresa.com',
            'phone': '11999999991'
        },
        {
            'name': 'Empresa B',
            'cnpj': '22222222222222',
            'email': 'b@empresa.com',
            'phone': '11999999992'
        }
    ]
    
    for sup in suppliers:
        supplier_instance.create(sup)
    
    result = supplier_instance.get_all()
    
    assert isinstance(result, dict)
    assert len(result) == 2
    
    # Verificar se todos os fornecedores criados estão na lista
    for id, data in result.items():
        assert id.startswith('sup_')
        assert data['name'] in ['Empresa A', 'Empresa B']
        assert data['cnpj'] in ['11111111111111', '22222222222222']

def test_update_supplier(supplier_instance):
    """Testa a atualização de um fornecedor"""
    # Primeiro cria um fornecedor
    original_data = {
        'name': 'Empresa Original',
        'cnpj': '12345678901234',
        'email': 'original@empresa.com',
        'phone': '11999999999'
    }
    created = supplier_instance.create(original_data)
    
    # Dados para atualização
    update_data = {
        'name': 'Empresa Atualizada',
        'cnpj': '12345678901234',  # Mesmo CNPJ
        'email': 'atualizado@empresa.com',
        'phone': '11988888888'
    }
    
    result = supplier_instance.update(created['id'], update_data)
    
    assert result is not None
    assert result['id'] == created['id']
    assert result['name'] == update_data['name']
    assert result['email'] == update_data['email']
    assert result['phone'] == update_data['phone']

def test_delete_supplier(supplier_instance):
    """Testa a exclusão de um fornecedor"""
    # Primeiro cria um fornecedor
    supplier_data = {
        'name': 'Empresa Teste',
        'cnpj': '12345678901234',
        'email': 'teste@empresa.com',
        'phone': '11999999999'
    }
    created = supplier_instance.create(supplier_data)
    
    # Exclui o fornecedor
    result = supplier_instance.delete(created['id'])
    assert result is True
    
    # Verifica se o fornecedor foi realmente excluído
    assert supplier_instance.get(created['id']) is None

def test_duplicate_cnpj(supplier_instance):
    """Testa tentativa de criar fornecedor com CNPJ duplicado"""
    supplier_data = {
        'name': 'Empresa A',
        'cnpj': '12345678901234',
        'email': 'a@empresa.com',
        'phone': '11999999999'
    }
    
    # Cria o primeiro fornecedor
    supplier_instance.create(supplier_data)
    
    # Tenta criar outro com o mesmo CNPJ
    duplicate_data = {
        'name': 'Empresa B',
        'cnpj': '12345678901234',  # Mesmo CNPJ
        'email': 'b@empresa.com',
        'phone': '11988888888'
    }
    
    with pytest.raises(ValueError, match="CNPJ já cadastrado"):
        supplier_instance.create(duplicate_data)

def test_clean_data(supplier_instance):
    """Testa a limpeza de dados do fornecedor"""
    # Dados com caracteres especiais
    supplier_data = {
        'name': 'Empresa Teste',
        'cnpj': '12.345.678/0001-34',
        'email': ' teste@empresa.com ',
        'phone': '(11) 99999-9999'
    }
    
    result = supplier_instance.create(supplier_data)
    
    assert result['cnpj'] == '12345678000134'
    assert result['email'] == 'teste@empresa.com'
    assert result['phone'] == '11999999999'

def test_invalid_id_operations(supplier_instance):
    """Testa operações com IDs inválidos"""
    assert supplier_instance.get('invalid_id') is None
    assert supplier_instance.update('invalid_id', {}) is None
    assert supplier_instance.delete('invalid_id') is False

def test_data_persistence(supplier_instance):
    """Testa se os dados são persistidos corretamente"""
    supplier_data = {
        'name': 'Empresa Teste',
        'cnpj': '12345678901234',
        'email': 'teste@empresa.com',
        'phone': '11999999999'
    }
    
    # Cria um fornecedor
    created = supplier_instance.create(supplier_data)
    
    # Cria uma nova instância para ler os dados
    new_instance = Supplier()
    new_instance.db_file = supplier_instance.db_file
    
    # Verifica se os dados foram persistidos
    loaded = new_instance.get(created['id'])
    assert loaded is not None
    assert loaded['id'] == created['id']
    assert loaded['name'] == supplier_data['name']

def test_supplier_creation(supplier):
    assert supplier.name == 'Test Supplier'
    assert supplier.cnpj == '00.000.000/0000-00'
    assert supplier.email == 'test@supplier.com'
    assert supplier.phone == '(00) 00000-0000'

def test_supplier_update(supplier):
    supplier.name = 'Updated Supplier'
    supplier.email = 'updated@supplier.com'
    assert supplier.name == 'Updated Supplier'
    assert supplier.email == 'updated@supplier.com'

def test_supplier_to_dict(supplier):
    supplier_dict = supplier.to_dict()
    assert supplier_dict['name'] == 'Test Supplier'
    assert supplier_dict['cnpj'] == '00.000.000/0000-00'
    assert supplier_dict['email'] == 'test@supplier.com'
    assert supplier_dict['phone'] == '(00) 00000-0000'