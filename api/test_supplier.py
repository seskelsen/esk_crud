import pytest
import random
from api.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_suppliers_authenticated(client):
    """Testa acesso autenticado à listagem de fornecedores."""
    token = get_jwt_token(client)
    response = client.get('/suppliers', headers={"Authorization": f"Bearer {token}"})
    assert response.status_code in (200, 404)
    data = response.get_json()
    assert "success" in data

def test_create_supplier_authenticated(client):
    """Testa criação de fornecedor autenticado com CNPJ alfanumérico."""
    token = get_jwt_token(client)
    unique_cnpj = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=16))
    supplier_data = {
        "name": "Fornecedor Teste",
        "cnpj": unique_cnpj,
        "email": f"fornecedor{unique_cnpj[-4:]}@teste.com",
        "phone": "11999999999"
    }
    response = client.post(
        '/suppliers',
        json=supplier_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["success"] is True
    assert "data" in data
    assert data["data"]["name"] == supplier_data["name"]
    assert data["data"]["cnpj"] == supplier_data["cnpj"]
    supplier_id = data["data"]["id"]
    print(f"Fornecedor criado com ID: {supplier_id}")
    return supplier_id

def test_update_supplier_authenticated(client):
    """Testa atualização de fornecedor autenticado."""
    token = get_jwt_token(client)
    supplier_id = test_create_supplier_authenticated(client)
    print(f"Atualizando fornecedor com ID: {supplier_id}")
    unique_cnpj = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=16))
    update_data = {
        "name": "Fornecedor Atualizado",
        "cnpj": unique_cnpj,
        "email": f"atualizado{unique_cnpj[-4:]}@teste.com",
        "phone": "11988888888"
    }
    response = client.put(
        f'/suppliers/{supplier_id}',
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["name"] == update_data["name"]

def test_delete_supplier_authenticated(client):
    """Testa exclusão de fornecedor autenticado."""
    token = get_jwt_token(client)
    supplier_id = test_create_supplier_authenticated(client)
    print(f"Excluindo fornecedor com ID: {supplier_id}")
    response = client.delete(
        f'/suppliers/{supplier_id}',
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True

def get_jwt_token(client, username="admin", password="admin123"):
    """Auxiliar para obter um token JWT válido."""
    response = client.post('/auth/login', json={"username": username, "password": password})
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "token" in data
    return data["token"]