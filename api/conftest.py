"""
Configurações para pytest
Desabilita rate limiting durante testes automatizados
"""

import pytest
from api.app import app, limiter


@pytest.fixture(autouse=True)
def disable_limiter_for_tests():
    """Desabilita rate limiting para todos os testes."""
    if hasattr(limiter, 'enabled'):
        limiter.enabled = False
    else:
        # Se limiter tem método disable, usar
        if hasattr(limiter, 'reset'):
            limiter.reset()
    yield
    # Cleanup após teste
    if hasattr(limiter, 'enabled'):
        limiter.enabled = True


@pytest.fixture
def client():
    """Cria cliente de teste com app em modo TESTING e rate limiter desabilitado."""
    app.config['TESTING'] = True
    
    # Desabilitar rate limiter verificando se é instância real
    original_limit = None
    if hasattr(limiter, 'limit'):
        original_limit = limiter.limit
        # Substituir com uma função stub
        limiter.limit = lambda rule: lambda f: f
    
    with app.test_client() as test_client:
        yield test_client
    
    # Restaurar
    if original_limit:
        limiter.limit = original_limit
