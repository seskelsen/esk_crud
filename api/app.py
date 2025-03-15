from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from supplier import Supplier
from flask_apispec import FlaskApiSpec, use_kwargs, marshal_with, doc
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from marshmallow import Schema, fields, ValidationError
import yaml
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

supplier = Supplier()

# Schemas para documentação e validação
class SupplierSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True, error_messages={'required': 'Nome é obrigatório'})
    cnpj = fields.Str(required=True, error_messages={'required': 'CNPJ é obrigatório'})
    email = fields.Email(required=True, error_messages={
        'required': 'Email é obrigatório',
        'invalid': 'Email inválido'
    })
    phone = fields.Str(required=True, error_messages={'required': 'Telefone é obrigatório'})

class SupplierResponseSchema(Schema):
    success = fields.Bool()
    data = fields.Nested(SupplierSchema, allow_none=True)
    message = fields.Str()

class SupplierListResponseSchema(Schema):
    success = fields.Bool()
    data = fields.Dict(keys=fields.Str(), values=fields.Nested(SupplierSchema))
    message = fields.Str()

class DeleteResponseSchema(Schema):
    success = fields.Bool()
    message = fields.Str()

# Configuração do Swagger UI
app.config.update({
    'APISPEC_SPEC': APISpec(
        title='API de Fornecedores',
        version='v1',
        plugins=[MarshmallowPlugin()],
        openapi_version='3.0.3'
    ),
    'APISPEC_SWAGGER_URL': '/swagger/',
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'
})
docs = FlaskApiSpec(app)

@app.route('/openapi.yaml')
def serve_openapi():
    with open('openapi.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

@app.route('/', methods=['GET'])
@doc(tags=['Fornecedores'], description='Lista todos os fornecedores cadastrados')
@marshal_with(SupplierListResponseSchema)
def get_all():
    """Lista todos os fornecedores."""
    try:
        # Usar a instância de teste se estiver em modo de teste
        supplier_instance = app.config.get('supplier', supplier)
        data = supplier_instance.get_all()
        return {'success': True, 'data': data}
    except Exception as e:
        logger.error(f"Erro ao listar fornecedores: {str(e)}")
        return {'success': False, 'message': 'Erro ao listar fornecedores'}, 500

@app.route('/<id>', methods=['GET'])
@doc(tags=['Fornecedores'], description='Obtém um fornecedor específico')
@marshal_with(SupplierResponseSchema)
def get_one(id):
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

@app.route('/', methods=['POST'])
@doc(tags=['Fornecedores'], description='Cria um novo fornecedor')
@marshal_with(SupplierResponseSchema)
def create():
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
        return {'success': True, 'data': result}
        
    except Exception as e:
        logger.error(f"Erro ao criar fornecedor: {str(e)}")
        return {'success': False, 'message': f'Erro ao criar fornecedor: {str(e)}'}, 500

@app.route('/<id>', methods=['PUT'])
@doc(tags=['Fornecedores'], description='Atualiza um fornecedor existente')
@marshal_with(SupplierResponseSchema)
def update(id):
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

@app.route('/<id>', methods=['DELETE'])
@doc(tags=['Fornecedores'], description='Remove um fornecedor')
@marshal_with(DeleteResponseSchema)
def delete(id):
    """Remove um fornecedor pelo ID."""
    try:
        logger.debug(f"Tentando excluir fornecedor {id}")
        supplier_instance = app.config.get('supplier', supplier)
        success = supplier_instance.delete(id)
        
        if success:
            logger.info(f"Fornecedor {id} excluído com sucesso")
            return {'success': True, 'message': 'Fornecedor excluído com sucesso'}
        else:
            logger.warning(f"Fornecedor {id} não encontrado para exclusão")
            return {'success': False, 'message': 'Fornecedor não encontrado'}, 404
            
    except Exception as e:
        logger.error(f"Erro ao excluir fornecedor {id}: {str(e)}")
        return {'success': False, 'message': f'Erro ao excluir fornecedor: {str(e)}'}, 500

# Registrando as rotas na documentação
docs.register(get_all)
docs.register(get_one)
docs.register(create)
docs.register(update)
docs.register(delete)

if __name__ == '__main__':
    app.run(port=5000)