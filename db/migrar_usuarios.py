import json
import os
from pymongo import MongoClient
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Configuração da URI do MongoDB Atlas
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://localhost:27017/eskcrud")

# Caminho do arquivo JSON de usuários
json_path = Path("db/users.json")

# Conectar ao MongoDB
client = MongoClient(MONGO_URI)
db = client["eskcrud"]
collection = db["users"]

# Carregar usuários do JSON
with open(json_path, "r", encoding="utf-8") as f:
    users = json.load(f)

# Migrar cada usuário
for user in users.values():
    # Remove o campo 'id' (MongoDB usará _id)
    user.pop("id", None)
    # Evita duplicidade por username/email
    if not collection.find_one({"username": user["username"]}):
        collection.insert_one(user)
        print(f"Usuário {user['username']} migrado.")
    else:
        print(f"Usuário {user['username']} já existe no MongoDB, ignorado.")

print("Migração concluída.")