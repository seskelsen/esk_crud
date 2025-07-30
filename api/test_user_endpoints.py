import pytest
import random
from api.app import app
from api.validators import CNPJValidator

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def get_jwt_token(client, username="admin", password="admin123"):
    response = client.post('/auth/login', json={"username": username, "password": password})
    assert response.status_code == 200
    return response.get_json()['token']

# Test Swagger JSON endpoint

def test_swagger_json(client):
    response = client.get('/api/swagger.json')
    assert response.status_code == 200
    data = response.get_json()
    assert 'openapi' in data
    assert 'paths' in data

# Test CNPJValidator

def test_cnpj_validator_valid():
    validator = CNPJValidator()
    # valid alphanumeric CNPJ (14 chars)
    valid = 'ABC123DEF456GH'
    assert validator(valid) == valid

@pytest.mark.parametrize('cnpj', ['short', 'TOO_LONG_CNPJ_1234567890', 'invalid!cnpj'])
def test_cnpj_validator_invalid(cnpj):
    validator = CNPJValidator()
    with pytest.raises(Exception):
        validator(cnpj)

# Test user endpoints

def test_get_users_admin(client):
    token = get_jwt_token(client)
    response = client.get('/users', headers={"Authorization": f"Bearer {token}"})
    assert response.status_code in (200, 404)


def test_get_users_non_admin_forbidden(client):
    # register non-admin user
    username = f"user{random.randint(1000,9999)}"
    client.post('/auth/register', json={"username": username, "email": f"{username}@test.com", "password": "pass123"})
    login = client.post('/auth/login', json={"username": username, "password": "pass123"})
    token = login.get_json()['token']
    response = client.get('/users', headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_user_crud_admin(client):
    token = get_jwt_token(client)
    # Create user
    username = f"u{random.randint(10000,99999)}"
    email = f"{username}@test.com"
    response = client.post('/users', json={"username": username, "email": email, "password": "pass"}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404 or response.status_code == 405
    # Directly use register endpoint
    reg = client.post('/auth/register', json={"username": username, "email": email, "password": "pass"})
    assert reg.status_code == 201
    user_data = reg.get_json()['user']
    user_id = user_data['id']
    # Get user
    resp = client.get(f'/users/{user_id}', headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    # Update user
    upd = client.put(f'/users/{user_id}', json={"username": username, "email": email, "role": "user"}, headers={"Authorization": f"Bearer {token}"})
    assert upd.status_code == 200
    # Delete user
    del_resp = client.delete(f'/users/{user_id}', headers={"Authorization": f"Bearer {token}"})
    assert del_resp.status_code == 200
    
# Novos testes de validação e erros de usuários
def test_register_missing_fields(client):
    # Campo obrigatório ausente deve retornar 400
    resp1 = client.post('/auth/register', json={"username": "u1", "password": "p"})
    assert resp1.status_code == 400
    resp2 = client.post('/auth/register', json={"username": "u2", "email": "u2@test.com"})
    assert resp2.status_code == 400

def test_register_duplicate(client):
    username = f"dup{random.randint(1000,9999)}"
    email = f"{username}@test.com"
    # Primeiro registro
    resp1 = client.post('/auth/register', json={"username": username, "email": email, "password": "pass"})
    assert resp1.status_code == 201
    # Usuário duplicado
    resp2 = client.post('/auth/register', json={"username": username, "email": f"other@test.com", "password": "pass"})
    assert resp2.status_code == 400
    # Email duplicado
    resp3 = client.post('/auth/register', json={"username": f"{username}x", "email": email, "password": "pass"})
    assert resp3.status_code == 400

def test_access_users_without_token(client):
    # Acesso sem token retorna 401
    resp = client.get('/users')
    assert resp.status_code == 401
    resp2 = client.get('/users/someid')
    assert resp2.status_code == 401

def test_crud_user_not_found(client):
    token = get_jwt_token(client)
    fake_id = "0123456789abcdef01234567"
    # GET não existente
    resp_get = client.get(f'/users/{fake_id}', headers={"Authorization": f"Bearer {token}"})
    assert resp_get.status_code == 404
    # PUT não existente
    resp_put = client.put(
        f'/users/{fake_id}',
        json={"username": "x", "email": "x@x.com", "role": "user"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp_put.status_code == 404
    # DELETE não existente
    resp_del = client.delete(f'/users/{fake_id}', headers={"Authorization": f"Bearer {token}"})
    assert resp_del.status_code == 404
