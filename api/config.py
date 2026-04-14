import os
from dotenv import load_dotenv

load_dotenv()

# Configuração de conexão com MongoDB para Flask
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://localhost:27017/eskcrud")
