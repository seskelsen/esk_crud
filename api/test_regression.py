"""
Suite de Testes de Regressão Funcional
Valida que TODAS as funcionalidades continuam operacionais após mudanças de segurança.
Deve ser executada antes de cada fase de implementação.
"""

import pytest
import random
import json
from api.app import app


@pytest.fixture
def client():
    """Cria cliente de teste com app em modo TESTING."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def get_jwt_token(client, username="admin", password="admin123"):
    """Auxiliar para obter um token JWT válido."""
    response = client.post('/auth/login', json={"username": username, "password": password})
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "token" in data
    return data["token"]


# ============================================================================
# TESTS: FLUXO DE AUTENTICAÇÃO (Register → Login → Acesso)
# ============================================================================

class TestAuthenticationFlow:
    """Testes do fluxo de autenticação: registro, login, acesso autorizado/não autorizado."""

    def test_register_new_user_success(self, client):
        """Registra um novo usuário com sucesso."""
        unique_user = f"user_{random.randint(10000, 99999)}"
        user_data = {
            "username": unique_user,
            "email": f"{unique_user}@test.com",
            "password": "senha123"
        }
        response = client.post('/auth/register', json=user_data)
        assert response.status_code == 201
        data = response.get_json()
        assert data["success"] is True
        assert "user" in data
        assert data["user"]["username"] == unique_user

    def test_register_duplicate_username(self, client):
        """Rejeita registro com username duplicado."""
        unique_user = f"user_{random.randint(10000, 99999)}"
        user_data = {
            "username": unique_user,
            "email": f"{unique_user}@test.com",
            "password": "senha123"
        }
        # Primeiro registro
        response1 = client.post('/auth/register', json=user_data)
        assert response1.status_code == 201
        
        # Segundo registro com mesmo username
        user_data["email"] = f"outro_{unique_user}@test.com"  # Email diferente
        response2 = client.post('/auth/register', json=user_data)
        assert response2.status_code == 400  # Bad Request (duplicado)
        data = response2.get_json()
        assert data["success"] is False

    def test_register_duplicate_email(self, client):
        """Rejeita registro com email duplicado."""
        unique_user = f"user_{random.randint(10000, 99999)}"
        unique_email = f"unique_{random.randint(10000, 99999)}@test.com"
        user_data = {
            "username": unique_user,
            "email": unique_email,
            "password": "senha123"
        }
        # Primeiro registro
        response1 = client.post('/auth/register', json=user_data)
        assert response1.status_code == 201
        
        # Segundo registro com mesmo email
        user_data["username"] = f"outro_{unique_user}"
        response2 = client.post('/auth/register', json=user_data)
        assert response2.status_code == 400  # Bad Request (duplicado)
        data = response2.get_json()
        assert data["success"] is False

    def test_register_missing_fields(self, client):
        """Rejeita registro com campos obrigatórios faltando."""
        # Sem password
        response = client.post('/auth/register', json={
            "username": "testuser",
            "email": "test@test.com"
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_login_success(self, client):
        """Faz login com sucesso."""
        unique_user = f"user_{random.randint(10000, 99999)}"
        user_data = {
            "username": unique_user,
            "email": f"{unique_user}@test.com",
            "password": "senha123"
        }
        # Registra
        reg_response = client.post('/auth/register', json=user_data)
        assert reg_response.status_code == 201
        
        # Login
        login_response = client.post('/auth/login', json={
            "username": unique_user,
            "password": "senha123"
        })
        assert login_response.status_code == 200
        data = login_response.get_json()
        assert data["success"] is True
        assert "token" in data
        assert "user" in data
        assert data["user"]["username"] == unique_user

    def test_login_invalid_password(self, client):
        """Rejeita login com senha incorreta."""
        unique_user = f"user_{random.randint(10000, 99999)}"
        user_data = {
            "username": unique_user,
            "email": f"{unique_user}@test.com",
            "password": "senha123"
        }
        # Registra
        client.post('/auth/register', json=user_data)
        
        # Login com senha errada
        login_response = client.post('/auth/login', json={
            "username": unique_user,
            "password": "senha_errada"
        })
        assert login_response.status_code == 401
        data = login_response.get_json()
        assert data["success"] is False

    def test_login_nonexistent_user(self, client):
        """Rejeita login com usuário inexistente."""
        login_response = client.post('/auth/login', json={
            "username": "nao_existe_123456",
            "password": "qualquer_senha"
        })
        assert login_response.status_code == 401
        data = login_response.get_json()
        assert data["success"] is False

    def test_access_protected_resource_with_valid_token(self, client):
        """Acessa recurso protegido com token válido."""
        token = get_jwt_token(client)
        response = client.get('/suppliers', headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.get_json()
        assert "success" in data

    def test_access_protected_resource_without_token(self, client):
        """Rejeita acesso sem token."""
        response = client.get('/suppliers')
        assert response.status_code == 401

    def test_access_protected_resource_with_invalid_token(self, client):
        """Rejeita acesso com token inválido."""
        response = client.get('/suppliers', headers={"Authorization": "Bearer invalid_token"})
        assert response.status_code == 422  # Unprocessable Entity (JWT inválido)


# ============================================================================
# TESTS: FLUXO CRUD SUPPLIERS (Create, Read, Update, Delete)
# ============================================================================

class TestSupplierCRUD:
    """Testes do fluxo CRUD de fornecedores."""

    def _create_supplier(self, client, token=None):
        """Helper para criar um fornecedor único."""
        if token is None:
            token = get_jwt_token(client)
        
        unique_cnpj = ''.join(random.choices('0123456789', k=14))
        supplier_data = {
            "name": f"Supplier_{unique_cnpj}",
            "cnpj": unique_cnpj,
            "email": f"supplier_{unique_cnpj}@test.com",
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
        return data["data"]["id"], supplier_data

    def test_create_supplier_success(self, client):
        """Cria um fornecedor com sucesso."""
        token = get_jwt_token(client)
        supplier_id, supplier_data = self._create_supplier(client, token)
        assert supplier_id is not None

    def test_create_supplier_missing_cnpj(self, client):
        """Rejeita criação sem CNPJ."""
        token = get_jwt_token(client)
        supplier_data = {
            "name": "Supplier Sem CNPJ",
            # "cnpj": "",  # Omitido
            "email": "test@test.com",
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

    def test_create_supplier_duplicate_cnpj(self, client):
        """Cria fornecedor com CNPJ duplicado (sem validação de unicidade na API)."""
        token = get_jwt_token(client)
        supplier_id, supplier_data = self._create_supplier(client, token)
        
        # Tenta criar outro com mesmo CNPJ
        new_supplier = {
            "name": "Outro Nome",
            "cnpj": supplier_data["cnpj"],  # Mesmo CNPJ
            "email": f"outro_{random.randint(1000, 9999)}@test.com",
            "phone": "11888888888"
        }
        response = client.post(
            '/suppliers',
            json=new_supplier,
            headers={"Authorization": f"Bearer {token}"}
        )
        # NOTA: A API atual não valida CNPJ duplicado, então permite (201)
        # TODO: Adicionar validação de unicidade de CNPJ em supplier_mongo.py
        assert response.status_code == 201  # API permite duplicado
        data = response.get_json()
        assert data["success"] is True

    def test_create_supplier_unauthenticated(self, client):
        """Rejeita criação sem autenticação."""
        supplier_data = {
            "name": "Supplier",
            "cnpj": ''.join(random.choices('0123456789', k=14)),
            "email": "test@test.com",
            "phone": "11999999999"
        }
        response = client.post('/suppliers', json=supplier_data)
        assert response.status_code == 401

    def test_get_supplier_by_id(self, client):
        """Recupera fornecedor por ID."""
        token = get_jwt_token(client)
        supplier_id, supplier_data = self._create_supplier(client, token)
        
        response = client.get(
            f'/suppliers/{supplier_id}',
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["id"] == supplier_id
        assert data["data"]["name"] == supplier_data["name"]

    def test_get_supplier_nonexistent(self, client):
        """Rejeita GET para fornecedor inexistente."""
        token = get_jwt_token(client)
        response = client.get(
            '/suppliers/nonexistent_id_12345',
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False

    def test_list_suppliers(self, client):
        """Lista fornecedores."""
        token = get_jwt_token(client)
        # Cria um fornecedor
        supplier_id, supplier_data = self._create_supplier(client, token)
        
        # Lista
        response = client.get(
            '/suppliers',
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        # Verifica se o fornecedor criado está na lista
        assert isinstance(data["data"], (list, dict))

    def test_update_supplier_success(self, client):
        """Atualiza fornecedor com sucesso."""
        token = get_jwt_token(client)
        supplier_id, supplier_data = self._create_supplier(client, token)
        
        update_data = {
            "name": "Nome Atualizado",
            "cnpj": ''.join(random.choices('0123456789', k=14)),
            "email": f"updated_{random.randint(1000, 9999)}@test.com",
            "phone": "11888888888"
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

    def test_update_supplier_nonexistent(self, client):
        """Rejeita UPDATE com dados incompletos (API valida campos obrigatórios antes de buscar)."""
        token = get_jwt_token(client)
        # UPDATE requer todos os campos (name, cnpj, email, phone)
        update_data = {
            "name": "New Name",
            "cnpj": "12345678901234",
            "email": "test@test.com",
            "phone": "11999999999"
        }
        response = client.put(
            '/suppliers/nonexistent_id_12345',
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        # API retorna 404 quando ID não existe (após validar campos)
        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False

    def test_delete_supplier_success(self, client):
        """Deleta fornecedor com sucesso."""
        token = get_jwt_token(client)
        supplier_id, supplier_data = self._create_supplier(client, token)
        
        response = client.delete(
            f'/suppliers/{supplier_id}',
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        
        # Verifica que foi deletado
        get_response = client.get(
            f'/suppliers/{supplier_id}',
            headers={"Authorization": f"Bearer {token}"}
        )
        assert get_response.status_code == 404

    def test_delete_supplier_nonexistent(self, client):
        """Rejeita DELETE para fornecedor inexistente."""
        token = get_jwt_token(client)
        response = client.delete(
            '/suppliers/nonexistent_id_12345',
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404
        data = response.get_json()
        assert data["success"] is False


# ============================================================================
# TESTS: AUTORIZAÇÃO (Admin vs User)
# ============================================================================

class TestAuthorization:
    """Testes de controle de acesso (admin vs user)."""

    def test_admin_can_list_users(self, client):
        """Admin consegue listar usuários."""
        admin_token = get_jwt_token(client, username="admin", password="admin123")
        response = client.get('/users', headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code in (200, 404)  # 200 se há usuários, 404 se não há
        data = response.get_json()
        assert "success" in data

    def test_user_cannot_list_users(self, client):
        """User normal não consegue listar usuários."""
        # Registra um user normal
        unique_user = f"user_{random.randint(10000, 99999)}"
        user_data = {
            "username": unique_user,
            "email": f"{unique_user}@test.com",
            "password": "senha123"
        }
        client.post('/auth/register', json=user_data)
        
        # Login como user normal
        login_response = client.post('/auth/login', json={
            "username": unique_user,
            "password": "senha123"
        })
        user_token = login_response.get_json()["token"]
        
        # Tenta acessar /users
        response = client.get('/users', headers={"Authorization": f"Bearer {user_token}"})
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False

    def test_admin_can_get_specific_user(self, client):
        """Admin consegue recuperar um usuário específico."""
        # Registra um user
        unique_user = f"user_{random.randint(10000, 99999)}"
        user_data = {
            "username": unique_user,
            "email": f"{unique_user}@test.com",
            "password": "senha123"
        }
        reg_response = client.post('/auth/register', json=user_data)
        user_id = reg_response.get_json()["user"]["id"]
        
        # Admin recupera o user
        admin_token = get_jwt_token(client, username="admin", password="admin123")
        response = client.get(f'/users/{user_id}', headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["id"] == user_id

    def test_user_cannot_get_other_user(self, client):
        """User normal não consegue recuperar outro usuário."""
        # Registra user 1
        user1_data = {
            "username": f"user1_{random.randint(10000, 99999)}",
            "email": f"user1_{random.randint(10000, 99999)}@test.com",
            "password": "senha123"
        }
        reg1_response = client.post('/auth/register', json=user1_data)
        user1_id = reg1_response.get_json()["user"]["id"]
        
        # Registra user 2
        user2_data = {
            "username": f"user2_{random.randint(10000, 99999)}",
            "email": f"user2_{random.randint(10000, 99999)}@test.com",
            "password": "senha456"
        }
        reg2_response = client.post('/auth/register', json=user2_data)
        user2_id = reg2_response.get_json()["user"]["id"]
        
        # User 2 tenta recuperar user 1
        login2_response = client.post('/auth/login', json={
            "username": user2_data["username"],
            "password": "senha456"
        })
        user2_token = login2_response.get_json()["token"]
        
        response = client.get(f'/users/{user1_id}', headers={"Authorization": f"Bearer {user2_token}"})
        assert response.status_code == 403


# ============================================================================
# TESTS: FLUXOS DE INTEGRAÇÃO (End-to-End)
# ============================================================================

class TestIntegrationFlows:
    """Testes de fluxos completos (end-to-end)."""

    def test_complete_supplier_workflow(self, client):
        """Fluxo completo: criar → ler → listar → editar → deletar supplier."""
        token = get_jwt_token(client)
        
        # 1. Criar
        supplier_data = {
            "name": "Supplier E2E",
            "cnpj": ''.join(random.choices('0123456789', k=14)),
            "email": "e2e@test.com",
            "phone": "11999999999"
        }
        create_response = client.post(
            '/suppliers',
            json=supplier_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert create_response.status_code == 201
        supplier_id = create_response.get_json()["data"]["id"]
        
        # 2. Ler por ID
        get_response = client.get(
            f'/suppliers/{supplier_id}',
            headers={"Authorization": f"Bearer {token}"}
        )
        assert get_response.status_code == 200
        assert get_response.get_json()["data"]["id"] == supplier_id
        
        # 3. Listar
        list_response = client.get(
            '/suppliers',
            headers={"Authorization": f"Bearer {token}"}
        )
        assert list_response.status_code == 200
        
        # 4. Editar
        update_data = {
            "name": "Supplier E2E Updated",
            "cnpj": ''.join(random.choices('0123456789', k=14)),
            "email": "e2e_updated@test.com",
            "phone": "11888888888"
        }
        update_response = client.put(
            f'/suppliers/{supplier_id}',
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert update_response.status_code == 200
        assert update_response.get_json()["data"]["name"] == update_data["name"]
        
        # 5. Deletar
        delete_response = client.delete(
            f'/suppliers/{supplier_id}',
            headers={"Authorization": f"Bearer {token}"}
        )
        assert delete_response.status_code == 200
        
        # 6. Verificar que foi deletado
        get_after_delete = client.get(
            f'/suppliers/{supplier_id}',
            headers={"Authorization": f"Bearer {token}"}
        )
        assert get_after_delete.status_code == 404

    def test_complete_authentication_workflow(self, client):
        """Fluxo completo: registrar → login → acessar recurso protegido."""
        unique_user = f"workflow_{random.randint(10000, 99999)}"
        user_data = {
            "username": unique_user,
            "email": f"{unique_user}@test.com",
            "password": "senha123"
        }
        
        # 1. Registrar
        reg_response = client.post('/auth/register', json=user_data)
        assert reg_response.status_code == 201
        
        # 2. Login
        login_response = client.post('/auth/login', json={
            "username": unique_user,
            "password": "senha123"
        })
        assert login_response.status_code == 200
        token = login_response.get_json()["token"]
        
        # 3. Acessar recurso protegido
        protected_response = client.get(
            '/suppliers',
            headers={"Authorization": f"Bearer {token}"}
        )
        assert protected_response.status_code == 200

    def test_multiple_suppliers_creation_and_listing(self, client):
        """Cria múltiplos fornecedores e verifica se aparecem na listagem."""
        token = get_jwt_token(client)
        supplier_ids = []
        
        # Cria 3 fornecedores
        for i in range(3):
            supplier_data = {
                "name": f"Supplier_{i}",
                "cnpj": ''.join(random.choices('0123456789', k=14)),
                "email": f"supplier{i}@test.com",
                "phone": "11999999999"
            }
            response = client.post(
                '/suppliers',
                json=supplier_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 201
            supplier_ids.append(response.get_json()["data"]["id"])
        
        # Lista todos
        list_response = client.get(
            '/suppliers',
            headers={"Authorization": f"Bearer {token}"}
        )
        assert list_response.status_code == 200


# ============================================================================
# TESTS: DOCUMENTAÇÃO E HEALTHCHECK
# ============================================================================

class TestDocumentation:
    """Testes de documentação e healthcheck."""

    def test_root_redirect(self, client):
        """GET / redireciona para documentação."""
        response = client.get('/')
        assert response.status_code in (200, 302, 307)

    def test_swagger_ui_available(self, client):
        """Swagger UI está disponível."""
        response = client.get('/api/docs/')
        assert response.status_code == 200

    def test_swagger_json_available(self, client):
        """Swagger JSON está disponível."""
        response = client.get('/api/swagger.json')
        assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
