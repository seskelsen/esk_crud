import json
import os
import uuid
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class Supplier:
    def __init__(self, db_path=None):
        if db_path:
            self.db_file = Path(db_path)
        else:
            self.db_file = Path(__file__).parent.parent / 'db' / 'suppliers.json'
        self._init_db()

    def _init_db(self):
        if not self.db_file.exists():
            suppliers = {}
            for company in [
                {
                    'name': 'Empresa ABC Ltda',
                    'cnpj': '12345678000190',
                    'email': 'contato@abcltda.com.br',
                    'phone': '11934567890'
                },
                {
                    'name': 'Distribuidora XYZ',
                    'cnpj': '98765432000121',
                    'email': 'comercial@xyzltda.com.br',
                    'phone': '21923456789'
                },
                {
                    'name': 'Indústria 123 S.A.',
                    'cnpj': '45678901000123',
                    'email': 'vendas@123sa.com.br',
                    'phone': '31934567890'
                }
            ]:
                id = f'sup_{uuid.uuid4()}'
                suppliers[id] = {'id': id, **company}
            
            self.db_file.parent.mkdir(parents=True, exist_ok=True)
            self._write_db(suppliers)
        else:
            # Validar e corrigir dados existentes
            suppliers = self._read_db()
            self._write_db(suppliers)  # Reescreve para garantir consistência

    def _clean_data(self, data):
        """Remove caracteres especiais dos dados"""
        if isinstance(data, dict):
            cleaned = {}
            for key, value in data.items():
                if key in ['cnpj', 'phone']:
                    # Remove qualquer caractere não numérico
                    cleaned[key] = ''.join(filter(str.isdigit, str(value)))
                elif key == 'email':
                    # Remove espaços do email
                    cleaned[key] = str(value).strip()
                else:
                    cleaned[key] = value
            return cleaned
        return data

    def _read_db(self):
        try:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Corrige possíveis inconsistências entre chaves e IDs
                fixed_data = {}
                for key, value in data.items():
                    if not value:
                        logger.warning(f"Registro inválido encontrado para a chave {key}")
                        continue
                    
                    correct_id = value.get('id', key)
                    cleaned_value = self._clean_data(value)
                    fixed_data[correct_id] = {**cleaned_value, 'id': correct_id}
                return fixed_data
        except FileNotFoundError:
            logger.warning("Arquivo de banco de dados não encontrado, criando novo...")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON: {e}")
            return {}
        except Exception as e:
            logger.error(f"Erro ao ler banco de dados: {e}")
            return {}

    def _write_db(self, data):
        try:
            # Garantir que os IDs estejam sincronizados e dados limpos
            fixed_data = {}
            for key, value in data.items():
                if not value:
                    logger.warning(f"Tentativa de salvar registro inválido para a chave {key}")
                    continue
                    
                cleaned_value = self._clean_data(value)
                cleaned_value['id'] = key  # Garante que o ID interno seja igual à chave
                fixed_data[key] = cleaned_value
            
            # Criar diretório se não existir
            self.db_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(fixed_data, f, indent=4, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Erro ao escrever no banco de dados: {e}")
            raise

    def get_all(self):
        return self._read_db()

    def get(self, id):
        suppliers = self._read_db()
        return suppliers.get(id)

    def create(self, data):
        logger.debug(f"Criando novo fornecedor com dados: {data}")
        suppliers = self._read_db()
        
        # Limpar e validar dados
        cleaned_data = self._clean_data(data)
        
        # Verificar CNPJ duplicado
        cnpj = cleaned_data.get('cnpj')
        if any(s['cnpj'] == cnpj for s in suppliers.values()):
            raise ValueError("CNPJ já cadastrado")
        
        # Gerar ID único
        id = f'sup_{uuid.uuid4()}'
        suppliers[id] = {'id': id, **cleaned_data}
        
        self._write_db(suppliers)
        logger.info(f"Fornecedor criado com ID: {id}")
        return suppliers[id]

    def update(self, id, data):
        logger.debug(f"Atualizando fornecedor {id} com dados: {data}")
        suppliers = self._read_db()
        
        if id not in suppliers:
            logger.warning(f"Fornecedor {id} não encontrado para atualização")
            return None
            
        # Limpar e validar dados
        cleaned_data = self._clean_data(data)
        
        # Verificar CNPJ duplicado (exceto para o mesmo registro)
        cnpj = cleaned_data.get('cnpj')
        if any(s['cnpj'] == cnpj and s['id'] != id for s in suppliers.values()):
            raise ValueError("CNPJ já cadastrado")
            
        suppliers[id] = {**suppliers[id], **cleaned_data, 'id': id}
        self._write_db(suppliers)
        
        logger.info(f"Fornecedor {id} atualizado com sucesso")
        return suppliers[id]

    def delete(self, id):
        try:
            logger.debug(f"Tentando excluir fornecedor com ID: {id}")
            suppliers = self._read_db()
            
            if not id:
                logger.warning("ID fornecido está vazio")
                return False
                
            if id in suppliers:
                logger.info(f"Excluindo fornecedor {id}")
                del suppliers[id]
                self._write_db(suppliers)
                return True
            
            logger.warning(f"Fornecedor {id} não encontrado para exclusão")
            return False
            
        except Exception as e:
            logger.error(f"Erro ao excluir fornecedor: {str(e)}")
            raise