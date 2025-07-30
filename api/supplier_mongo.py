import logging
from bson import ObjectId
from pymongo import ASCENDING # Importar ASCENDING
from datetime import datetime

logger = logging.getLogger(__name__)

class Supplier:
    def __init__(self, mongo):
        self.mongo = mongo
        self.collection = self.mongo.db.suppliers
        # Criar índice no campo 'name' se não existir
        self.collection.create_index([("name", ASCENDING)], name="idx_supplier_name")
        logger.info("Índice 'idx_supplier_name' garantido na coleção 'suppliers'.")

    def get_all(self):
        try:
            logger.debug("Buscando todos os fornecedores")
            suppliers = list(self.collection.find())
            suppliers_dict = {}
            for s in suppliers:
                # Transforma o _id em string e adiciona o prefixo "sup_"
                id_str = f"sup_{str(s['_id'])}"
                s['id'] = id_str
                del s['_id']
                suppliers_dict[id_str] = s
            logger.debug(f"Fornecedores encontrados: {len(suppliers_dict)}")
            return suppliers_dict
        except Exception as e:
            logger.error(f"Erro ao buscar fornecedores: {e}")
            return {}

    def get(self, id):
        # Remove o prefixo "sup_" se presente
        mongo_id = id.replace("sup_", "") if id.startswith("sup_") else id
        try:
            supplier = self.collection.find_one({'_id': ObjectId(mongo_id)})
            if supplier:
                supplier['id'] = f"sup_{str(supplier['_id'])}"
                del supplier['_id']
            return supplier
        except Exception as e:
            logger.error(f"Erro ao obter fornecedor: {e}")
            return None

    def create(self, data):
        try:
            # Adiciona timestamps de criação e atualização
            timestamp = datetime.utcnow()
            data['created_at'] = timestamp
            data['updated_at'] = timestamp
            result = self.collection.insert_one(data)
            supplier = self.get(str(result.inserted_id))
            return supplier
        except Exception as e:
            logger.error(f"Erro ao criar fornecedor: {e}")
            raise

    def update(self, id, data):
        # Remove o prefixo "sup_" se presente
        mongo_id = id.replace("sup_", "") if id.startswith("sup_") else id
        try:
            # Atualiza timestamp de atualização
            data['updated_at'] = datetime.utcnow()
            # Verifica CNPJ duplicado (exceto para o mesmo registro)
            if self.collection.find_one({'cnpj': data['cnpj'], '_id': {'$ne': ObjectId(mongo_id)}}):
                logger.warning(f"CNPJ duplicado detectado: {data['cnpj']}")
                raise ValueError('CNPJ já cadastrado')
            result = self.collection.update_one({'_id': ObjectId(mongo_id)}, {'$set': data})
            if result.matched_count == 0:
                logger.error(f"Fornecedor com ID {id} não encontrado para atualização.")
                return None
            logger.info(f"Fornecedor com ID {id} atualizado com sucesso.")
            return self.get(id)
        except Exception as e:
            logger.error(f"Erro ao atualizar fornecedor com ID {id}: {e}")
            return None

    def delete(self, id):
        # Remove o prefixo "sup_" se presente
        mongo_id = id.replace("sup_", "") if id.startswith("sup_") else id
        try:
            logger.debug(f"Excluindo fornecedor com ID Mongo: {mongo_id}")
            result = self.collection.delete_one({'_id': ObjectId(mongo_id)})
            if result.deleted_count == 0:
                logger.error(f"Fornecedor com ID {id} não encontrado para exclusão.")
                return False
            logger.info(f"Fornecedor com ID {id} excluído com sucesso.")
            return True
        except Exception as e:
            logger.error(f"Erro ao excluir fornecedor com ID {id}: {e}")
            return False
