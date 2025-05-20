import json
from pymongo import MongoClient
from pathlib import Path

# Configuração da URI do MongoDB Atlas
target_uri = "mongodb+srv://eskcrud:Zlw4D0vPDFIdyK5n@cluster0.bkriwyh.mongodb.net/eskcrud?retryWrites=true&w=majority&appName=Cluster0"

# Caminho do arquivo JSON de fornecedores
json_path = Path("db/suppliers.json")

# Conectar ao MongoDB
client = MongoClient(target_uri)
db = client["eskcrud"]
collection = db["suppliers"]

# Carregar fornecedores do JSON
with open(json_path, "r", encoding="utf-8") as f:
    suppliers = json.load(f)

# Migrar cada fornecedor
for supplier in suppliers.values():
    # Remove o campo 'id' (MongoDB usará _id)
    supplier.pop("id", None)
    # Evita duplicidade por CNPJ
    if not collection.find_one({"cnpj": supplier["cnpj"]}):
        collection.insert_one(supplier)
        print(f"Fornecedor {supplier['name']} migrado.")
    else:
        print(f"Fornecedor {supplier['name']} já existe no MongoDB, ignorado.")

print("Migração de fornecedores concluída.")
