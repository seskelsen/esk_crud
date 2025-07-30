import logging
from bson import ObjectId
import bcrypt
from datetime import datetime

logger = logging.getLogger(__name__)

class User:
    def __init__(self, mongo):
        self.mongo = mongo
        self.collection = self.mongo.db.users

    def create(self, data):
        # Verifica se username ou email já existem
        if self.collection.find_one({'username': data['username']}):
            raise ValueError('Nome de usuário já cadastrado')
        if self.collection.find_one({'email': data['email']}):
            raise ValueError('Email já cadastrado')
        # Hash da senha
        data['password'] = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        # Adiciona timestamps de criação e atualização
        timestamp = datetime.utcnow()
        data['created_at'] = timestamp
        data['updated_at'] = timestamp
        result = self.collection.insert_one(data)
        user = self.get(str(result.inserted_id))
        logger.info(f"Usuário criado com ID: {user['id']}")
        return user

    def get_by_username(self, username):
        user = self.collection.find_one({'username': username})
        if user:
            user['id'] = str(user['_id'])
            del user['_id']
        return user

    def get_by_email(self, email):
        user = self.collection.find_one({'email': email})
        if user:
            user['id'] = str(user['_id'])
            del user['_id']
        return user

    def authenticate(self, username, password):
        user = self.get_by_username(username)
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return user
        return None

    def get_all(self):
        users = list(self.collection.find())
        for u in users:
            u['id'] = str(u['_id'])
            del u['_id']
        return {u['id']: u for u in users}

    def get(self, id):
        user = self.collection.find_one({'_id': ObjectId(id)})
        if user:
            user['id'] = str(user['_id'])
            del user['_id']
        return user

    def update(self, id, data):
        # Atualiza timestamp de atualização
        data['updated_at'] = datetime.utcnow()
        self.collection.update_one({'_id': ObjectId(id)}, {'$set': data})
        return self.get(id)

    def delete(self, id):
        result = self.collection.delete_one({'_id': ObjectId(id)})
        return result.deleted_count > 0
