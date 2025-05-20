def test_admin_access_users(client):
    """Testa que apenas admin pode acessar a listagem de usuários."""
    # Login como admin
    admin_token = get_jwt_token(client, username="admin", password="admin123")
    # Admin deve conseguir acessar /users
    response = client.get('/users', headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code in (200, 404)  # 404 se não houver usuários, 200 se houver
    # Cria um usuário comum
    unique_user = f"usuario{random.randint(10000,99999)}"
    user_data = {
        "username": unique_user,
        "email": f"{unique_user}@teste.com",
        "password": "senha123"
    }
    reg_response = client.post('/auth/register', json=user_data)
    assert reg_response.status_code == 201
    # Login como usuário comum
    login_response = client.post('/auth/login', json={"username": unique_user, "password": "senha123"})
    assert login_response.status_code == 200
    user_token = login_response.get_json()["token"]
    # Usuário comum NÃO deve conseguir acessar /users
    response = client.get('/users', headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 403
    data = response.get_json()
    assert data["success"] is False
    assert "message" in data
def test_register_user(client):
    """Testa registro de novo usuário."""
    unique_user = f"usuario{random.randint(10000,99999)}"
    user_data = {
        "username": unique_user,
        "email": f"{unique_user}@teste.com",
        "password": "senha123"
    }
    response = client.post('/auth/register', json=user_data)
    assert response.status_code == 201
    data = response.get_json()
    assert data["success"] is True
    assert "user" in data
    assert data["user"]["username"] == user_data["username"]

def test_login_user(client):
    """Testa login de usuário recém-registrado."""
    unique_user = f"usuario{random.randint(10000,99999)}"
    user_data = {
        "username": unique_user,
        "email": f"{unique_user}@teste.com",
        "password": "senha123"
    }
    # Registra o usuário
    reg_response = client.post('/auth/register', json=user_data)
    assert reg_response.status_code == 201
    # Faz login
    login_response = client.post('/auth/login', json={"username": unique_user, "password": "senha123"})
    assert login_response.status_code == 200
    data = login_response.get_json()
    assert data["success"] is True
    assert "token" in data
    assert "user" in data
def test_get_suppliers_unauthenticated(client):
    """Testa acesso à listagem de fornecedores sem autenticação."""
    response = client.get('/suppliers')
    assert response.status_code == 401
    data = response.get_json()
    # Flask-JWT-Extended retorna 'msg' para erros de autenticação
    assert "msg" in data or "message" in data

def test_create_supplier_invalid_data(client):
    """Testa criação de fornecedor com dados inválidos."""
    token = get_jwt_token(client)
    # Dados inválidos: CNPJ faltando
    supplier_data = {
        "name": "Fornecedor Inválido",
        # "cnpj": "",  # omitido
        "email": "invalido@teste.com",
        "phone": "11999999999"
    }
    response = client.post(
        '/suppliers',
        json=supplier_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "message" in data

def test_create_supplier_unauthenticated(client):
    """Testa criação de fornecedor sem autenticação."""
    unique_cnpj = str(10000000000000 + random.randint(0, 89999999999999))
    supplier_data = {
        "name": "Fornecedor Sem Auth",
        "cnpj": unique_cnpj,
        "email": f"sem_auth{unique_cnpj[-4:]}@teste.com",
        "phone": "11999999999"
    }
    response = client.post(
        '/suppliers',
        json=supplier_data
    )
    assert response.status_code == 401
    data = response.get_json()
    assert "msg" in data or "message" in data
import pytest
import random
from api.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_root_redirect(client):
    """Testa se a raiz redireciona para o frontend."""
    response = client.get('/')
    assert response.status_code in (301, 302)
    assert 'Location' in response.headers

def test_swagger_ui(client):
    """Testa se a documentação Swagger está acessível."""
    response = client.get('/api/docs/')
    assert response.status_code == 200
    # Verifica se o HTML contém o div principal do Swagger UI
    assert b'id="swagger-ui"' in response.data


def get_jwt_token(client, username="admin", password="admin123"):
    """Auxiliar para obter um token JWT válido."""
    response = client.post('/auth/login', json={"username": username, "password": password})
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "token" in data
    return data["token"]

def test_get_suppliers_authenticated(client):
    """Testa acesso autenticado à listagem de fornecedores."""
    token = get_jwt_token(client)
    response = client.get('/suppliers', headers={"Authorization": f"Bearer {token}"})
    # Espera 200 OK ou 404 se não houver fornecedores
    assert response.status_code in (200, 404)
    data = response.get_json()
    assert "success" in data


def test_create_supplier_authenticated(client):
    """Testa criação de fornecedor autenticado."""
    token = get_jwt_token(client)
    # Gera CNPJ único para evitar duplicidade
    unique_cnpj = str(10000000000000 + random.randint(0, 89999999999999))
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
    # Retorna o ID do fornecedor criado para os próximos testes
    return data["data"]["id"]


def test_update_supplier_authenticated(client):
    """Testa atualização de fornecedor autenticado."""
    token = get_jwt_token(client)
    # Cria um fornecedor para atualizar
    supplier_id = test_create_supplier_authenticated(client)
    unique_cnpj = str(10000000000000 + random.randint(0, 89999999999999))
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
    # Cria um fornecedor para excluir
    supplier_id = test_create_supplier_authenticated(client)
    response = client.delete(
        f'/suppliers/{supplier_id}',
        headers={"Authorization": f"Bearer {token}"}
    )
    # Espera 204 No Content para exclusão bem-sucedida
    assert response.status_code == 204
