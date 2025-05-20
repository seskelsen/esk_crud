import logging
from bson import ObjectId

logger = logging.getLogger(__name__)

class Supplier:
    def __init__(self, mongo):
        self.mongo = mongo
        self.collection = self.mongo.db.suppliers

    def get_all(self):
        suppliers = list(self.collection.find())
        for s in suppliers:
            s['id'] = str(s['_id'])
            del s['_id']
        return {s['id']: s for s in suppliers}

    def get(self, id):
        supplier = self.collection.find_one({'_id': ObjectId(id)})
        if supplier:
            supplier['id'] = str(supplier['_id'])
            del supplier['_id']
        return supplier

    def create(self, data):
        # Verifica CNPJ duplicado
        if self.collection.find_one({'cnpj': data['cnpj']}):
            raise ValueError('CNPJ já cadastrado')
        result = self.collection.insert_one(data)
        supplier = self.get(str(result.inserted_id))
        logger.info(f"Fornecedor criado com ID: {supplier['id']}")
        return supplier

    def update(self, id, data):
        # Verifica CNPJ duplicado (exceto para o mesmo registro)
        if self.collection.find_one({'cnpj': data['cnpj'], '_id': {'$ne': ObjectId(id)}}):
            raise ValueError('CNPJ já cadastrado')
        self.collection.update_one({'_id': ObjectId(id)}, {'$set': data})
        return self.get(id)

    def delete(self, id):
        result = self.collection.delete_one({'_id': ObjectId(id)})
        return result.deleted_count > 0
