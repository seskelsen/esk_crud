import logging
from bson import ObjectId
from pymongo import ASCENDING # Importar ASCENDING

logger = logging.getLogger(__name__)

class Supplier:
    def __init__(self, mongo):
        self.mongo = mongo
        self.collection = self.mongo.db.suppliers
        # Criar índice no campo 'name' se não existir
        self.collection.create_index([("name", ASCENDING)], name="idx_supplier_name")
        logger.info("Índice 'idx_supplier_name' garantido na coleção 'suppliers'.")

    def get_all(self):
        suppliers = list(self.collection.find())
        suppliers_dict = {}
        for s in suppliers:
            # Transforma o _id em string e adiciona o prefixo "sup_"
            id_str = f"sup_{str(s['_id'])}"
            s['id'] = id_str
            del s['_id']
            # Armazena no dicionário com a chave sendo o ID formatado
            suppliers_dict[id_str] = s
        return suppliers_dict

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
        # Verifica CNPJ duplicado
        if self.collection.find_one({'cnpj': data['cnpj']}):
            raise ValueError('CNPJ já cadastrado')
        result = self.collection.insert_one(data)
        supplier = self.get(str(result.inserted_id))
        logger.info(f"Fornecedor criado com ID: {supplier['id']}")
        return supplier

    def update(self, id, data):
        # Remove o prefixo "sup_" se presente
        mongo_id = id.replace("sup_", "") if id.startswith("sup_") else id
        # Verifica CNPJ duplicado (exceto para o mesmo registro)
        if self.collection.find_one({'cnpj': data['cnpj'], '_id': {'$ne': ObjectId(mongo_id)}}):
            raise ValueError('CNPJ já cadastrado')
        self.collection.update_one({'_id': ObjectId(mongo_id)}, {'$set': data})
        return self.get(id)

    def delete(self, id):
        # Remove o prefixo "sup_" se presente
        mongo_id = id.replace("sup_", "") if id.startswith("sup_") else id
        result = self.collection.delete_one({'_id': ObjectId(mongo_id)})
        return result.deleted_count > 0
