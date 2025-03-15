import json
import pytest
from app import app
from supplier import Supplier
import os
import tempfile
from pathlib import Path

@pytest.fixture
def client():
    # Criar um arquivo temporário para o banco de dados
    db_fd, db_path = tempfile.mkstemp()
    os.close(db_fd)  # Fechar o descritor de arquivo
    
    # Criar uma nova instância do Supplier com o banco de dados temporário
    app.config['supplier'] = Supplier(db_path=db_path)
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client
    
    # Limpar após os testes
    try:
        os.unlink(db_path)
    except:
        pass

def test_get_all_empty(client):
    """Testa listagem de fornecedores vazia"""
    response = client.get('/')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['success'] is True
    assert isinstance(data['data'], dict)
    assert len(data['data']) == 0

def test_create_supplier(client):
    """Testa criação de fornecedor"""
    test_supplier = {
        'name': 'Teste Ltda',
        'cnpj': '12345678901234',
        'email': 'teste@empresa.com',
        'phone': '11999999999'
    }
    
    response = client.post('/',
                         data=json.dumps(test_supplier),
                         content_type='application/json')
    data = json.loads(response.data)
    
    assert response.status_code == 200
    assert data['success'] is True
    assert data['data']['name'] == test_supplier['name']
    assert data['data']['cnpj'] == test_supplier['cnpj']
    assert data['data']['email'] == test_supplier['email']
    assert data['data']['phone'] == test_supplier['phone']
    assert 'id' in data['data']

def test_create_invalid_supplier(client):
    """Testa criação de fornecedor com dados inválidos"""
    invalid_supplier = {
        'name': 'Teste Ltda',
        'cnpj': '123', # CNPJ inválido
        'email': 'email-invalido',
        'phone': '123'
    }
    
    response = client.post('/',
                         data=json.dumps(invalid_supplier),
                         content_type='application/json')
    data = json.loads(response.data)
    
    assert response.status_code == 400
    assert data['success'] is False
    assert 'message' in data

def test_get_one_supplier(client):
    """Testa busca de um fornecedor específico"""
    # Primeiro cria um fornecedor
    test_supplier = {
        'name': 'Teste Ltda',
        'cnpj': '12345678901234',
        'email': 'teste@empresa.com',
        'phone': '11999999999'
    }
    
    create_response = client.post('/',
                               data=json.dumps(test_supplier),
                               content_type='application/json')
    create_data = json.loads(create_response.data)
    supplier_id = create_data['data']['id']
    
    # Depois busca o fornecedor criado
    get_response = client.get(f'/{supplier_id}')
    get_data = json.loads(get_response.data)
    
    assert get_response.status_code == 200
    assert get_data['success'] is True
    assert get_data['data']['id'] == supplier_id

def test_get_nonexistent_supplier(client):
    """Testa busca de fornecedor inexistente"""
    response = client.get('/sup_nonexistent')
    data = json.loads(response.data)
    
    assert response.status_code == 404
    assert data['success'] is False
    assert 'message' in data

def test_update_supplier(client):
    """Testa atualização de fornecedor"""
    # Primeiro cria um fornecedor
    test_supplier = {
        'name': 'Teste Ltda',
        'cnpj': '12345678901234',
        'email': 'teste@empresa.com',
        'phone': '11999999999'
    }
    
    create_response = client.post('/',
                               data=json.dumps(test_supplier),
                               content_type='application/json')
    create_data = json.loads(create_response.data)
    supplier_id = create_data['data']['id']
    
    # Atualiza o fornecedor
    updated_data = {
        'name': 'Teste Atualizado Ltda',
        'cnpj': '12345678901234',
        'email': 'novo@empresa.com',
        'phone': '11988888888'
    }
    
    update_response = client.put(f'/{supplier_id}',
                              data=json.dumps(updated_data),
                              content_type='application/json')
    update_data = json.loads(update_response.data)
    
    assert update_response.status_code == 200
    assert update_data['success'] is True
    assert update_data['data']['name'] == updated_data['name']
    assert update_data['data']['email'] == updated_data['email']
    assert update_data['data']['phone'] == updated_data['phone']

def test_update_nonexistent_supplier(client):
    """Testa atualização de fornecedor inexistente"""
    test_data = {
        'name': 'Teste Ltda',
        'cnpj': '12345678901234',
        'email': 'teste@empresa.com',
        'phone': '11999999999'
    }
    
    response = client.put('/sup_nonexistent',
                        data=json.dumps(test_data),
                        content_type='application/json')
    data = json.loads(response.data)
    
    assert response.status_code == 404
    assert data['success'] is False
    assert 'message' in data

def test_delete_supplier(client):
    """Testa exclusão de fornecedor"""
    # Primeiro cria um fornecedor
    test_supplier = {
        'name': 'Teste Ltda',
        'cnpj': '12345678901234',
        'email': 'teste@empresa.com',
        'phone': '11999999999'
    }
    
    create_response = client.post('/',
                               data=json.dumps(test_supplier),
                               content_type='application/json')
    create_data = json.loads(create_response.data)
    supplier_id = create_data['data']['id']
    
    # Exclui o fornecedor
    delete_response = client.delete(f'/{supplier_id}')
    delete_data = json.loads(delete_response.data)
    
    assert delete_response.status_code == 200
    assert delete_data['success'] is True
    
    # Verifica se o fornecedor foi realmente excluído
    get_response = client.get(f'/{supplier_id}')
    assert get_response.status_code == 404

def test_delete_nonexistent_supplier(client):
    """Testa exclusão de fornecedor inexistente"""
    response = client.delete('/sup_nonexistent')
    data = json.loads(response.data)
    
    assert response.status_code == 404
    assert data['success'] is False
    assert 'message' in data

def test_create_duplicate_cnpj(client):
    """Testa criação de fornecedor com CNPJ duplicado"""
    test_supplier = {
        'name': 'Teste Ltda',
        'cnpj': '12345678901234',
        'email': 'teste@empresa.com',
        'phone': '11999999999'
    }
    
    # Cria o primeiro fornecedor
    client.post('/',
               data=json.dumps(test_supplier),
               content_type='application/json')
    
    # Tenta criar outro fornecedor com o mesmo CNPJ
    duplicate_response = client.post('/',
                                  data=json.dumps(test_supplier),
                                  content_type='application/json')
    data = json.loads(duplicate_response.data)
    
    assert duplicate_response.status_code == 500
    assert data['success'] is False
    assert 'CNPJ já cadastrado' in data['message']

def test_home(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'Welcome' in rv.data

def test_get_suppliers(client):
    rv = client.get('/suppliers')
    assert rv.status_code == 200
    assert b'suppliers' in rv.data

def test_add_supplier(client):
    new_supplier = {
        'name': 'Test Supplier',
        'cnpj': '00.000.000/0000-00',
        'email': 'test@supplier.com',
        'phone': '(00) 00000-0000'
    }
    rv = client.post('/suppliers', json=new_supplier)
    assert rv.status_code == 201
    assert b'Test Supplier' in rv.data

def test_update_supplier(client):
    updated_supplier = {
        'name': 'Updated Supplier',
        'cnpj': '00.000.000/0000-00',
        'email': 'updated@supplier.com',
        'phone': '(00) 00000-0000'
    }
    rv = client.put('/suppliers/1', json=updated_supplier)
    assert rv.status_code == 200
    assert b'Updated Supplier' in rv.data

def test_delete_supplier(client):
    rv = client.delete('/suppliers/1')
    assert rv.status_code == 204