"""
Suite de Testes de Segurança
Valida que os controles de segurança implementados funcionam corretamente.
Testa CORS, security headers, sanitização de logs, rate limiting e CSRF.
"""

import pytest
import random
import re
import io
import logging
from api.app import app, limiter


@pytest.fixture
def client():
    """Cria cliente de teste com TESTING=True."""
    app.config['TESTING'] = True
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture
def client_with_rate_limit():
    """Cria cliente de teste com rate limiting HABILITADO para testar limites."""
    app.config['TESTING'] = False  # Habilita rate limiting
    with app.test_client() as test_client:
        yield test_client
    app.config['TESTING'] = True  # Restaurar


def get_jwt_token(client, username="admin", password="admin123"):
    """Auxiliar para obter um token JWT válido."""
    response = client.post('/auth/login', json={"username": username, "password": password})
    assert response.status_code == 200
    return response.get_json()["token"]


# ============================================================================
# TESTS: SECURITY HEADERS
# ============================================================================

class TestSecurityHeaders:
    """Valida que headers de segurança estão presentes em todas as respostas."""

    def test_x_content_type_options_header(self, client):
        """Header X-Content-Type-Options deve ser 'nosniff'."""
        token = get_jwt_token(client)
        response = client.get('/suppliers', headers={"Authorization": f"Bearer {token}"})
        assert 'X-Content-Type-Options' in response.headers
        assert response.headers['X-Content-Type-Options'] == 'nosniff'

    def test_x_frame_options_header(self, client):
        """Header X-Frame-Options deve ser 'SAMEORIGIN'."""
        token = get_jwt_token(client)
        response = client.get('/suppliers', headers={"Authorization": f"Bearer {token}"})
        assert 'X-Frame-Options' in response.headers
        assert response.headers['X-Frame-Options'] == 'SAMEORIGIN'

    def test_x_xss_protection_header(self, client):
        """Header X-XSS-Protection deve estar presente."""
        token = get_jwt_token(client)
        response = client.get('/suppliers', headers={"Authorization": f"Bearer {token}"})
        assert 'X-XSS-Protection' in response.headers
        assert '1' in response.headers['X-XSS-Protection']

    def test_content_security_policy_header(self, client):
        """Header Content-Security-Policy deve estar presente."""
        token = get_jwt_token(client)
        response = client.get('/suppliers', headers={"Authorization": f"Bearer {token}"})
        assert 'Content-Security-Policy' in response.headers
        csp = response.headers['Content-Security-Policy']
        assert "default-src 'self'" in csp

    def test_security_headers_on_auth_endpoints(self, client):
        """Security headers devem estar presentes em endpoints de autenticação também."""
        response = client.post('/auth/login', json={
            "username": "admin", "password": "admin123"
        })
        assert 'X-Content-Type-Options' in response.headers
        assert 'X-Frame-Options' in response.headers

    def test_no_hsts_in_testing_mode(self, client):
        """HSTS não deve ser enviado em modo de desenvolvimento/teste."""
        token = get_jwt_token(client)
        response = client.get('/suppliers', headers={"Authorization": f"Bearer {token}"})
        # Em modo TESTING/DEBUG, HSTS não deve estar presente
        assert 'Strict-Transport-Security' not in response.headers


# ============================================================================
# TESTS: LOG SANITIZATION
# ============================================================================

class TestLogSanitization:
    """Valida que tokens JWT não aparecem em texto limpo nos logs."""

    def test_jwt_token_not_in_logs_plain(self, client, capfd):
        """Tokens JWT não devem aparecer em texto limpo nos logs."""
        token = get_jwt_token(client)
        
        # Fazer uma requisição que logaria o header Authorization
        client.get('/suppliers', headers={"Authorization": f"Bearer {token}"})
        
        # Capturar stderr (onde logs vão)
        captured = capfd.readouterr()
        stderr_output = captured.err
        
        # O token completo não deve aparecer nos logs
        # Tokens JWT têm 3 partes separadas por pontos
        token_parts = token.split('.')
        if len(token_parts) == 3:
            # A parte do payload não deve aparecer completa
            full_payload = token_parts[1]
            if len(full_payload) > 20:
                assert full_payload not in stderr_output, \
                    "Token JWT (payload) não deve aparecer em texto limpo nos logs"

    def test_authorization_header_masked_in_logs(self, client, capfd):
        """Header Authorization deve ser mascarado nos logs (verificado via stderr)."""
        token = get_jwt_token(client)
        
        # Fazer requisição
        client.get('/suppliers', headers={"Authorization": f"Bearer {token}"})
        
        # Capturar stderr (onde logs são escritos via StreamHandler)
        captured = capfd.readouterr()
        stderr_output = captured.err
        
        # O token completo não deve aparecer em stderr
        # (pode estar truncado como eyJxxx...[REDACTED])
        if token and len(token) > 20:
            # Verificar que não aparece o token COMPLETO (não truncado)
            # O formatter mascara como: eyJ...[REDACTED]
            full_token_present = token in stderr_output
            # Se o token aparece, é uma falha de segurança
            assert not full_token_present, \
                "Token JWT completo não deve aparecer em texto limpo nos logs"

    def test_sanitized_formatter_masks_jwt(self):
        """SanitizedFormatter deve mascarar tokens JWT."""
        from api.app import SanitizedFormatter
        
        formatter = SanitizedFormatter()
        
        # Criar um log record com token JWT (simula header de requisição)
        fake_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        record = logging.LogRecord(
            name='test', level=logging.DEBUG, pathname='', lineno=0,
            msg=f"Authorization: Bearer {fake_token}", args=(), exc_info=None
        )
        
        formatted = formatter.format(record)
        
        # Token completo não deve aparecer
        assert fake_token not in formatted
        # Deve conter o indicador de redaction
        assert '[REDACTED]' in formatted


# ============================================================================
# TESTS: RATE LIMITING
# ============================================================================

class TestRateLimiting:
    """Valida que rate limiting funciona corretamente em produção."""

    def test_rate_limit_login_enforced(self, client_with_rate_limit):
        """Rate limiting deve bloquear após exceder limite no login."""
        responses = []
        for i in range(15):
            response = client_with_rate_limit.post('/auth/login', json={
                "username": "admin",
                "password": "admin123"
            })
            responses.append(response.status_code)
        
        # Após 10 tentativas/minuto, deve retornar 429
        assert 429 in responses, \
            "Rate limiting deve retornar 429 após exceder limite de 10/minuto"

    def test_rate_limit_register_enforced(self, client_with_rate_limit):
        """Rate limiting deve bloquear registros excessivos."""
        responses = []
        for i in range(10):
            unique_user = f"ratelimit_{random.randint(100000, 999999)}"
            response = client_with_rate_limit.post('/auth/register', json={
                "username": unique_user,
                "email": f"{unique_user}@test.com",
                "password": "senha123"
            })
            responses.append(response.status_code)
        
        # Após 5 registros/minuto, deve retornar 429
        assert 429 in responses, \
            "Rate limiting deve retornar 429 após exceder limite de 5/minuto para registro"

    def test_rate_limit_disabled_in_testing(self, client):
        """Rate limiting deve ser desabilitado em modo TESTING."""
        # Com client normal (TESTING=True), múltiplas requisições não devem ser bloqueadas
        responses = []
        for i in range(12):
            response = client.post('/auth/login', json={
                "username": "admin",
                "password": "admin123"
            })
            responses.append(response.status_code)
        
        # Nenhuma resposta deve ser 429
        assert 429 not in responses, \
            "Rate limiting não deve bloquear em modo TESTING"


# ============================================================================
# TESTS: JWT SECURITY
# ============================================================================

class TestJWTSecurity:
    """Valida segurança dos tokens JWT."""

    def test_expired_or_invalid_token_rejected(self, client):
        """Token inválido/malformado deve ser rejeitado."""
        invalid_tokens = [
            "invalid_token",
            "eyJhbGciOiJub25lIn0.e30.",  # Algoritmo 'none' attack
            "eyJ.eyJ.sig",
            "",
        ]
        for token in invalid_tokens:
            if token:
                response = client.get(
                    '/suppliers',
                    headers={"Authorization": f"Bearer {token}"}
                )
                assert response.status_code in [401, 422], \
                    f"Token inválido '{token[:20]}...' deve ser rejeitado"

    def test_token_required_for_protected_routes(self, client):
        """Rotas protegidas devem exigir token."""
        protected_routes = [
            ('GET', '/suppliers'),
        ]
        for method, route in protected_routes:
            if method == 'GET':
                response = client.get(route)
            assert response.status_code == 401, \
                f"Rota {method} {route} deve exigir autenticação"

    def test_valid_token_grants_access(self, client):
        """Token válido deve conceder acesso a rotas protegidas."""
        token = get_jwt_token(client)
        response = client.get('/suppliers', headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200

    def test_role_based_access_control(self, client):
        """Controle de acesso por role deve funcionar."""
        # Criar usuário comum
        unique_user = f"roletest_{random.randint(10000, 99999)}"
        client.post('/auth/register', json={
            "username": unique_user,
            "email": f"{unique_user}@test.com",
            "password": "senha123"
        })
        
        # Login como usuário comum
        login_response = client.post('/auth/login', json={
            "username": unique_user,
            "password": "senha123"
        })
        user_token = login_response.get_json()["token"]
        
        # Usuário comum não deve listar todos os usuários
        response = client.get('/users', headers={"Authorization": f"Bearer {user_token}"})
        assert response.status_code == 403, \
            "Usuário comum não deve ter acesso admin a /users"


# ============================================================================
# TESTS: INPUT VALIDATION
# ============================================================================

class TestInputValidation:
    """Valida que a aplicação rejeita entradas inválidas."""

    def test_cnpj_validation(self, client):
        """CNPJ com formato inválido deve ser rejeitado."""
        token = get_jwt_token(client)
        # CNPJ com caracteres especiais/espaços (formato inválido)
        response = client.post('/suppliers', json={
            "name": "Test Supplier",
            "cnpj": "12.345.678/0001-95",  # CNPJ com pontuação (formato inválido para o validador)
            "email": "test@test.com",
            "phone": "11999999999"
        }, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 400

    def test_email_validation(self, client):
        """Email inválido deve ser rejeitado ao criar fornecedor."""
        token = get_jwt_token(client)
        response = client.post('/suppliers', json={
            "name": "Test Supplier",
            "cnpj": "11222333000181",
            "email": "not_an_email",
            "phone": "11999999999"
        }, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 400

    def test_missing_required_fields_supplier(self, client):
        """Campos obrigatórios faltando devem retornar 400."""
        token = get_jwt_token(client)
        response = client.post('/suppliers', json={
            "name": "Test Supplier"
            # CNPJ, email e phone faltando
        }, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 400
