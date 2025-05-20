import json
from pymongo import MongoClient
from bson import ObjectId
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
for supplier_id, supplier_data in suppliers.items():
    # Verificamos se o fornecedor já existe pelo CNPJ
    existing = collection.find_one({"cnpj": supplier_data["cnpj"]})
    if existing:
        print(f"Fornecedor {supplier_data['name']} já existe no MongoDB, atualizando...")
        # Atualizamos o documento existente com os dados originais
        # Mantemos o _id original do MongoDB
        # Armazenamos o id original com prefixo "sup_" para referência
        collection.update_one(
            {"_id": existing["_id"]},
            {"$set": {
                "name": supplier_data["name"],
                "email": supplier_data["email"],
                "phone": supplier_data["phone"],
                "original_id": supplier_data["id"]  # Armazenamos o ID original como referência
            }}
        )
    else:
        # Para novos fornecedores, removemos o campo 'id' (MongoDB usará _id)
        supplier_data_copy = supplier_data.copy()
        supplier_data_copy.pop("id", None)
        # Armazenamos o id original como referência
        supplier_data_copy["original_id"] = supplier_data["id"]
        insert_result = collection.insert_one(supplier_data_copy)
        print(f"Fornecedor {supplier_data['name']} migrado com ID: {insert_result.inserted_id}")

print("Migração de fornecedores concluída.")
print("Executando atualização final para verificar estrutura de dados...")

# Verificar e atualizar todos os documentos para garantir consistência
for doc in collection.find():
    if "original_id" not in doc:
        collection.update_one(
            {"_id": doc["_id"]},
            {"$set": {"original_id": f"sup_{str(doc['_id'])}"}},
        )
        print(f"Adicionado ID de referência para: {doc.get('name', 'desconhecido')}")

print("Processo finalizado com sucesso!")
