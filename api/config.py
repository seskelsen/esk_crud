import os
from dotenv import load_dotenv

load_dotenv()

# Configuração de conexão com MongoDB para Flask
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://localhost:27017/eskcrud")

# CORS: Configurar origens permitidas por ambiente
# DESENVOLVIMENTO: localhost:3000, localhost:5173 (Vite default)
# PRODUÇÃO: seu domínio real
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", 
    "http://localhost:3000,http://localhost:5173,http://localhost:5000"
).split(",")

# Converter para lista, removendo espaços
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS]
