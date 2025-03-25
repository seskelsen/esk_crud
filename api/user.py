import json
import uuid
from pathlib import Path
import bcrypt
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class User:
    def __init__(self, db_path=None):
        if db_path:
            self.db_file = Path(db_path)
        else:
            self.db_file = Path(__file__).parent.parent / 'db' / 'users.json'
        self._init_db()

    def _init_db(self):
        if not self.db_file.exists():
            users = {}
            # Criar usuário admin padrão
            admin_user = {
                'username': 'admin',
                'email': 'admin@example.com',
                'password': self._hash_password('admin123'),
                'role': 'admin',
                'active': True
            }
            id = f'usr_{uuid.uuid4()}'
            users[id] = {'id': id, **admin_user}
            
            self.db_file.parent.mkdir(parents=True, exist_ok=True)
            self._write_db(users)

    def _hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def _check_password(self, password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def _read_db(self) -> Dict[str, Any]:
        try:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Arquivo de banco de dados de usuários não encontrado, criando novo...")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON de usuários: {e}")
            return {}

    def _write_db(self, data: Dict[str, Any]) -> None:
        try:
            self.db_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro ao escrever no banco de dados de usuários: {e}")
            raise

    def create(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        users = self._read_db()
        
        # Verificar se usuário já existe
        if any(u['username'] == data['username'] for u in users.values()):
            raise ValueError("Nome de usuário já cadastrado")
        if any(u['email'] == data['email'] for u in users.values()):
            raise ValueError("Email já cadastrado")
        
        # Hash da senha
        data['password'] = self._hash_password(data['password'])
        
        # Gerar ID único
        id = f'usr_{uuid.uuid4()}'
        users[id] = {'id': id, **data}
        
        self._write_db(users)
        return users[id]

    def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        users = self._read_db()
        for user in users.values():
            if user['username'] == username:
                return user
        return None

    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        users = self._read_db()
        for user in users.values():
            if user['email'] == email:
                return user
        return None

    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        user = self.get_by_username(username)
        if user and self._check_password(password, user['password']):
            return user
        return None

    def get_all(self) -> Dict[str, Any]:
        return self._read_db()

    def get(self, id: str) -> Optional[Dict[str, Any]]:
        users = self._read_db()
        return users.get(id)

    def update(self, id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        users = self._read_db()
        
        if id not in users:
            return None
            
        # Se estiver atualizando a senha, fazer o hash
        if 'password' in data:
            data['password'] = self._hash_password(data['password'])
            
        users[id].update(data)
        self._write_db(users)
        return users[id]

    def delete(self, id: str) -> bool:
        users = self._read_db()
        if id in users:
            del users[id]
            self._write_db(users)
            return True
        return False