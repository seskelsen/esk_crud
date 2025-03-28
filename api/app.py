from flask import Flask, request, jsonify, send_from_directory, redirect
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate, ValidationError
from api.supplier import Supplier
from api.user import User
from flask_wtf.csrf import CSRFProtect
from flask_swagger_ui import get_swaggerui_blueprint
import secrets
import logging
from datetime import timedelta
from functools import wraps
import os
import yaml

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configurar Swagger
SWAGGER_URL = '/api/docs'
API_URL = '/api/swagger.json'

class SupplierSchema(Schema):
    name = fields.Str(required=True)
    cnpj = fields.Str(required=True, validate=validate.Length(equal=14))
    email = fields.Email(required=True)
    phone = fields.Str(required=True)

app = Flask(__name__, static_folder='../frontend', static_url_path='/frontend')
CORS(app)

# Configurar Swagger UI
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Sistema de Gestão de Fornecedores"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Rota para servir o arquivo swagger.json
@app.route('/api/swagger.json')
def serve_swagger_spec():
    with open('api/openapi.yaml', 'r', encoding='utf-8') as f:
        spec = yaml.safe_load(f)
    return jsonify(spec)

# Configuração de segurança
app.config['JWT_SECRET_KEY'] = secrets.token_hex(32)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['WTF_CSRF_SECRET_KEY'] = secrets.token_hex(32)
app.config['WTF_CSRF_ENABLED'] = False  # Desabilitado temporariamente para testes

# Inicializar extensões
jwt = JWTManager(app)
csrf = CSRFProtect(app)

# Instanciar modelos
supplier = Supplier()
user = User()

# Rotas de autenticação
@app.route('/auth/login', methods=['POST'])
def login():
    """Login de usuário"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return {'success': False, 'message': 'Usuário e senha são obrigatórios'}, 400
            
        user_data = user.authenticate(username, password)
        if not user_data:
            return {'success': False, 'message': 'Credenciais inválidas'}, 401
            
        access_token = create_access_token(
            identity=user_data['id'],
            additional_claims={'role': user_data.get('role', 'user')}
        )
        
        return {
            'success': True,
            'token': access_token,
            'user': {
                'id': user_data['id'],
                'username': user_data['username'],
                'email': user_data['email'],
                'role': user_data.get('role', 'user')
            }
        }
        
    except Exception as e:
        logger.error(f"Erro no login: {str(e)}")
        return {'success': False, 'message': 'Erro interno no servidor'}, 500

@app.route('/auth/register', methods=['POST'])
def register():
    """Registro de novo usuário"""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        required = ['username', 'email', 'password']
        if not all(field in data for field in required):
            return {'success': False, 'message': 'Dados incompletos'}, 400
            
        # Por padrão, novos usuários têm role 'user'
        data['role'] = 'user'
        data['active'] = True
        
        try:
            user_data = user.create(data)
        except ValueError as e:
            return {'success': False, 'message': str(e)}, 400
            
        return {
            'success': True,
            'user': {
                'id': user_data['id'],
                'username': user_data['username'],
                'email': user_data['email'],
                'role': user_data['role']
            }
        }, 201
        
    except Exception as e:
        logger.error(f"Erro no registro: {str(e)}")
        return {'success': False, 'message': 'Erro interno no servidor'}, 500

# Middleware para verificar role
def admin_required(fn):
    @jwt_required()
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        current_user = user.get(current_user_id)
        
        if not current_user or current_user.get('role') != 'admin':
            return {'success': False, 'message': 'Acesso negado'}, 403
            
        return fn(*args, **kwargs)
    return wrapper

# Rotas protegidas de usuários (apenas admin)
@app.route('/users', methods=['GET'])
@admin_required
def get_users():
    """Lista todos os usuários (requer admin)"""
    try:
        users = user.get_all()
        # Remover senhas da resposta
        for u in users.values():
            u.pop('password', None)
        return {'success': True, 'data': users}
    except Exception as e:
        logger.error(f"Erro ao listar usuários: {str(e)}")
        return {'success': False, 'message': 'Erro interno no servidor'}, 500

@app.route('/users/<id>', methods=['GET'])
@admin_required
def get_user(id):
    """Obtém um usuário específico (requer admin)"""
    try:
        user_data = user.get(id)
        if user_data is None:
            return {'success': False, 'message': 'Usuário não encontrado'}, 404
        user_data.pop('password', None)
        return {'success': True, 'data': user_data}
    except Exception as e:
        logger.error(f"Erro ao buscar usuário {id}: {str(e)}")
        return {'success': False, 'message': 'Erro interno no servidor'}, 500

@app.route('/users/<id>', methods=['PUT'])
@admin_required
def update_user(id):
    """Atualiza um usuário (requer admin)"""
    try:
        data = request.get_json()
        user_data = user.update(id, data)
        if user_data is None:
            return {'success': False, 'message': 'Usuário não encontrado'}, 404
        user_data.pop('password', None)
        return {'success': True, 'data': user_data}
    except Exception as e:
        logger.error(f"Erro ao atualizar usuário {id}: {str(e)}")
        return {'success': False, 'message': 'Erro interno no servidor'}, 500

@app.route('/users/<id>', methods=['DELETE'])
@admin_required
def delete_user(id):
    """Remove um usuário (requer admin)"""
    try:
        if user.delete(id):
            return {'success': True, 'message': 'Usuário removido com sucesso'}
        return {'success': False, 'message': 'Usuário não encontrado'}, 404
    except Exception as e:
        logger.error(f"Erro ao excluir usuário {id}: {str(e)}")
        return {'success': False, 'message': 'Erro interno no servidor'}, 500

# Proteger todas as rotas de fornecedores com autenticação
@app.route('/suppliers', methods=['GET'])
@jwt_required()
def get_all_suppliers():
    """Lista todos os fornecedores."""
    try:
        # Usar a instância de teste se estiver em modo de teste
        supplier_instance = app.config.get('supplier', supplier)
        data = supplier_instance.get_all()
        return {'success': True, 'data': data}
    except Exception as e:
        logger.error(f"Erro ao listar fornecedores: {str(e)}")
        return {'success': False, 'message': 'Erro ao listar fornecedores'}, 500

@app.route('/suppliers/<id>', methods=['GET'])
@jwt_required()
def get_one_supplier(id):
    """Obtém um fornecedor pelo ID."""
    try:
        supplier_instance = app.config.get('supplier', supplier)
        data = supplier_instance.get(id)
        if data is None:
            return {'success': False, 'message': 'Fornecedor não encontrado'}, 404
        return {'success': True, 'data': data}
    except Exception as e:
        logger.error(f"Erro ao buscar fornecedor {id}: {str(e)}")
        return {'success': False, 'message': 'Erro ao buscar fornecedor'}, 500

@app.route('/suppliers', methods=['POST'])
@jwt_required()
def create_supplier():
    """Cria um novo fornecedor."""
    try:
        # Validar dados usando o schema
        schema = SupplierSchema()
        try:
            data = request.get_json()
            # Validar dados
            schema.load(data)
        except ValidationError as err:
            logger.warning(f"Erro de validação: {err.messages}")
            return {'success': False, 'message': f"Erro de validação: {err.messages}"}, 400
            
        logger.debug(f"Tentando criar fornecedor com dados: {data}")
        supplier_instance = app.config.get('supplier', supplier)
            
        # Criar fornecedor
        result = supplier_instance.create(data)
        logger.info(f"Fornecedor criado com sucesso: {result}")
        return {'success': True, 'data': result}, 201
        
    except Exception as e:
        logger.error(f"Erro ao criar fornecedor: {str(e)}")
        return {'success': False, 'message': f'Erro ao criar fornecedor: {str(e)}'}, 500

@app.route('/suppliers/<id>', methods=['PUT'])
@jwt_required()
def update_supplier(id):
    """Atualiza um fornecedor existente."""
    try:
        data = request.get_json()
        logger.debug(f"Tentando atualizar fornecedor {id} com dados: {data}")
        supplier_instance = app.config.get('supplier', supplier)
        
        # Validar dados usando o schema
        schema = SupplierSchema()
        try:
            # Validar dados
            schema.load(data)
        except ValidationError as err:
            logger.warning(f"Erro de validação: {err.messages}")
            return {'success': False, 'message': f"Erro de validação: {err.messages}"}, 400
            
        result = supplier_instance.update(id, data)
        if result is None:
            return {'success': False, 'message': 'Fornecedor não encontrado'}, 404
            
        logger.info(f"Fornecedor {id} atualizado com sucesso")
        return {'success': True, 'data': result}
        
    except Exception as e:
        logger.error(f"Erro ao atualizar fornecedor {id}: {str(e)}")
        return {'success': False, 'message': f'Erro ao atualizar fornecedor: {str(e)}'}, 500

@app.route('/suppliers/<id>', methods=['DELETE'])
@jwt_required()
def delete_supplier(id):
    """Remove um fornecedor pelo ID."""
    try:
        logger.debug(f"Tentando excluir fornecedor {id}")
        supplier_instance = app.config.get('supplier', supplier)
        success = supplier_instance.delete(id)
        
        if success:
            logger.info(f"Fornecedor {id} excluído com sucesso")
            return {'success': True, 'message': 'Fornecedor excluído com sucesso'}, 204
        else:
            logger.warning(f"Fornecedor {id} não encontrado para exclusão")
            return {'success': False, 'message': 'Fornecedor não encontrado'}, 404
            
    except Exception as e:
        logger.error(f"Erro ao excluir fornecedor {id}: {str(e)}")
        return {'success': False, 'message': f'Erro ao excluir fornecedor: {str(e)}'}, 500

# Redirecionar a raiz para o frontend
@app.route('/')
def root():
    return redirect('/frontend/index.html')

if __name__ == '__main__':
    app.run(port=5000)