from flask import Flask, request, jsonify, send_from_directory, redirect
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate, ValidationError
from api.supplier_mongo import Supplier
from api.user_mongo import User
from flask_pymongo import PyMongo
from api import config
from flask_wtf.csrf import CSRFProtect
from flask_swagger_ui import get_swaggerui_blueprint
import secrets
import logging
from datetime import timedelta
from functools import wraps
import os
import yaml
from api.validators import CNPJValidator

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Log handler para werkzeug
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.DEBUG)

logger.info("Inicializando aplicação Flask com MongoDB")

# Configurar Swagger
SWAGGER_URL = '/api/docs'
API_URL = '/api/swagger.json'

class SupplierSchema(Schema):
    name = fields.Str(required=True)
    cnpj = fields.Str(required=True, validate=CNPJValidator())
    email = fields.Email(required=True)
    phone = fields.Str(required=True)

CORS_ORIGINS = ["http://localhost:5000", "http://127.0.0.1:5000"]
app = Flask(__name__, static_folder='../frontend', static_url_path='/frontend')
app.config["MONGO_URI"] = config.MONGO_URI
mongo = PyMongo(app)

# Configuração do CORS - habilita para todas as origens
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Configurar Swagger UI
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Sistema de Gestão de Fornecedores"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Middleware para log de requisições
@app.before_request
def log_request_info():
    logger.debug('Request Headers: %s', request.headers)
    logger.debug('Request Body: %s', request.get_data())

# Middleware para log de respostas
@app.after_request
def log_response_info(response):
    logger.debug('Response Status: %s', response.status)
    # Não logamos o corpo da resposta para evitar dados sensíveis ou respostas muito grandes
    return response

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

# Instanciar modelos (agora ambos usam MongoDB)
supplier = Supplier(mongo)
user = User(mongo)

# Rotas de autenticação
@app.route('/auth/login', methods=['POST'])
def login():
    """Login de usuário"""
    try:
        logger.info("Iniciando processo de login")
        data = request.get_json()
        logger.debug(f"Dados recebidos: {data}")
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            logger.warning("Tentativa de login sem usuário ou senha")
            return {'success': False, 'message': 'Usuário e senha são obrigatórios'}, 400
        
        logger.info(f"Tentando autenticar usuário: {username}")
        user_data = user.authenticate(username, password)
        
        if not user_data:
            logger.warning(f"Autenticação falhou para usuário: {username}")
            return {'success': False, 'message': 'Credenciais inválidas'}, 401
            
        logger.info(f"Usuário autenticado com sucesso: {username}")
        access_token = create_access_token(
            identity=user_data['id'],
            additional_claims={'role': user_data.get('role', 'user')}
        )
        
        logger.debug("Token JWT criado com sucesso")
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
        logger.error(f"Erro no login: {str(e)}", exc_info=True)
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
        logger.info("Recebendo solicitação para listar fornecedores")
        data = supplier.get_all()
        logger.debug(f"Fornecedores recuperados: {len(data)} itens")
        logger.debug(f"Estrutura: {data.keys() if data else 'Nenhum dado'}")
        # Garantir que a resposta está no formato esperado pelo frontend
        return {'success': True, 'data': data}
    except Exception as e:
        logger.error(f"Erro ao listar fornecedores: {str(e)}", exc_info=True)
        return {'success': False, 'message': 'Erro ao listar fornecedores'}, 500

@app.route('/suppliers/<id>', methods=['GET'])
@jwt_required()
def get_one_supplier(id):
    """Obtém um fornecedor pelo ID."""
    try:
        data = supplier.get(id)
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
        schema = SupplierSchema()
        try:
            data = request.get_json()
            schema.load(data)
        except ValidationError as err:
            logger.warning(f"Erro de validação: {err.messages}")
            return {'success': False, 'message': f"Erro de validação: {err.messages}"}, 400
        logger.debug(f"Tentando criar fornecedor com dados: {data}")
        result = supplier.create(data)
        logger.info(f"Fornecedor criado com sucesso: {result}")
        logger.debug(f"Dados persistidos no MongoDB: {result}")
        return {'success': True, 'data': result}, 201
    except ValueError as e:
        logger.warning(f"Erro de validação ao criar fornecedor: {str(e)}")
        return {'success': False, 'message': str(e)}, 400
    except Exception as e:
        logger.error(f"Erro ao criar fornecedor: {str(e)}", exc_info=True)
        return {'success': False, 'message': f'Erro ao criar fornecedor: {str(e)}'}, 500

@app.route('/suppliers/<id>', methods=['PUT'])
@jwt_required()
def update_supplier(id):
    """Atualiza um fornecedor existente."""
    try:
        data = request.get_json()
        logger.debug(f"Tentando atualizar fornecedor {id} com dados: {data}")
        schema = SupplierSchema()
        try:
            schema.load(data)
        except ValidationError as err:
            logger.warning(f"Erro de validação: {err.messages}")
            return {'success': False, 'message': f"Erro de validação: {err.messages}"}, 400
        result = supplier.update(id, data)
        if result is None:
            logger.warning(f"Fornecedor não encontrado para atualização: {id}")
            return {'success': False, 'message': 'Fornecedor não encontrado'}, 404
        logger.info(f"Fornecedor {id} atualizado com sucesso")
        return {'success': True, 'data': result}
    except ValueError as e:
        logger.warning(f"Erro de validação ao atualizar fornecedor: {str(e)}")
        return {'success': False, 'message': str(e)}, 400
    except Exception as e:
        logger.error(f"Erro ao atualizar fornecedor {id}: {str(e)}", exc_info=True)
        return {'success': False, 'message': f'Erro ao atualizar fornecedor: {str(e)}'}, 500

@app.route('/suppliers/<id>', methods=['DELETE'])
@jwt_required()
def delete_supplier(id):
    """Remove um fornecedor pelo ID."""
    try:
        logger.debug(f"Tentando excluir fornecedor {id}")
        success = supplier.delete(id)
        if success:
            logger.info(f"Fornecedor {id} excluído com sucesso")
            return {'success': True, 'message': 'Fornecedor excluído com sucesso'}, 200
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