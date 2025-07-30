# Sistema de Gestão de Fornecedores e Usuários

-## Visão Geral
- Este é um sistema de gestão de fornecedores e usuários que permite:
- - Gerenciar fornecedores (CRUD completo)
- - Gerenciar usuários (CRUD completo, apenas administradores)
- Autenticação e autorização com JWT
- Controle de acesso baseado em funções (RBAC)
- Documentação da API com Swagger

## Funcionalidades
- **Autenticação JWT**: Login e registro de usuários com tokens JWT.
- **Controle de Acesso**: Apenas administradores podem gerenciar usuários.
- **Gestão de Fornecedores**: CRUD completo para fornecedores.
- **Gestão de Usuários**: CRUD completo para usuários, acessível apenas a administradores.
- **Swagger UI**: Documentação interativa da API.
- **Frontend**: Interface web para gerenciar fornecedores e usuários.

## Tecnologias Utilizadas

### Frontend
- HTML5
- CSS3
- JavaScript (ES6+)
- Bootstrap 5.3
- SweetAlert2
- Bootstrap Icons

### Backend
- Python 3.12+
- Flask 3.0
- Flask-CORS
- Flask-APISpec
- Marshmallow
- PyYAML

## Requisitos
- Python 3.12+
- Node.js (opcional, para desenvolvimento do frontend)

## Instalação
1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/sistema-gestao-fornecedores.git
   cd sistema-gestao-fornecedores
   ```

2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate    # Windows
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```



4. Configure a URI do MongoDB em `api/config.py` (já configurado para Atlas por padrão):
   ```python
   MONGO_URI = "mongodb+srv://<usuario>:<senha>@<cluster>.mongodb.net/eskcrud?retryWrites=true&w=majority&appName=Cluster0"
   ```

   **Como obter a URI do MongoDB Atlas:**
   1. Crie uma conta gratuita em https://www.mongodb.com/cloud/atlas
   2. Crie um novo cluster (pode ser gratuito - M0 Sandbox).
   3. Crie um usuário de banco de dados e defina uma senha forte.
   4. Libere o acesso à sua faixa de IP (ou 0.0.0.0/0 para testes).
   5. No painel do Atlas, clique em "Connect" > "Connect your application" e copie a URI sugerida.
   6. Substitua `<usuario>`, `<senha>` e `<cluster>` na string acima pelos dados do seu cluster.

   Exemplo de URI:
   ```python
   MONGO_URI = "mongodb+srv://meuusuario:minhasenha@cluster0.abcde.mongodb.net/eskcrud?retryWrites=true&w=majority&appName=Cluster0"
   ```

   > **Dica:** Para produção, use variáveis de ambiente para armazenar a URI e segredos.

5. Inicie o servidor:
   ```bash
   python server.py
   ```

5. Acesse o sistema no navegador:
   - Frontend: [http://localhost:5000](http://localhost:5000)
   - Swagger UI: [http://localhost:5000/api/docs](http://localhost:5000/api/docs)

## Estrutura do Projeto
```
.
├── api/
│   ├── app.py               # Configuração principal do Flask
│   ├── openapi.yaml         # Especificação OpenAPI
│   ├── supplier_mongo.py    # Lógica de fornecedores (MongoDB)
│   ├── user_mongo.py        # Lógica de usuários (MongoDB)
│   ├── test_app.py          # Testes para app.py
│   ├── test_supplier.py     # Testes para supplier.py (legado)
│   └── __pycache__/         # Arquivos compilados
├── db/
│   ├── suppliers.json         # (Legado) Dados antigos de fornecedores (não mais utilizado)
│   ├── users.json             # (Legado) Dados antigos de usuários (não mais utilizado)
│   ├── migrar_fornecedores.py # Script de migração de fornecedores para MongoDB
│   └── migrar_usuarios.py     # Script de migração de usuários para MongoDB
├── frontend/
│   ├── index.html           # Página principal
│   ├── login.html           # Página de login
│   ├── css/
│   │   └── styles.css       # Estilos personalizados
│   └── js/
│       ├── auth.js          # Lógica de autenticação
│       └── script.js        # Lógica principal do frontend
├── requirements.txt         # Dependências do Python
├── server.py                # Inicia o servidor Flask
└── README.md                # Documentação do sistema
```

## Desenvolvimento

- Backend: API RESTful com Flask
- Frontend: HTML5 + CSS3 + JavaScript puro
- Persistência: MongoDB Atlas (NoSQL) — todos os dados de fornecedores e usuários são salvos no banco, não mais em arquivos JSON.
- Documentação: Swagger UI disponível em `/api/docs`

## Testes

Para rodar os testes automatizados:
```bash
pytest
```


### Cobertura e Estratégia de Testes (2025)
O projeto conta com uma suíte robusta de testes automatizados para backend, incluindo:
- Testes de autenticação (registro, login, JWT, permissões de admin e usuário comum)
- Testes de CRUD de fornecedores (criação, leitura, atualização, exclusão)
- Testes de proteção de rotas e casos de erro (validação, autenticação inválida, permissões)

**Insights:**
- A cobertura de testes é fundamental para garantir a segurança e a evolução do sistema.
- Recomenda-se expandir para testes de integração, E2E (Cypress/Selenium) e frontend.
- Automatize a execução dos testes no pipeline de CI/CD.

**Exemplo de execução:**
```bash
pytest api/test_basic.py --disable-warnings -v
```

## Contribuição
Contribuições são bem-vindas! Leia o arquivo `CONTRIBUTING.md` para mais informações.

## Ideias e Próximos Passos

- (Concluído) Backend agora utiliza MongoDB Atlas para persistência (NoSQL).
- Implementar cache (Redis) para escalabilidade.
- Adotar Docker e CI/CD para facilitar deploy e testes automatizados.
- Melhorar a interface do frontend, considerando frameworks modernos (React, Vue.js) e acessibilidade.
- Expandir a documentação técnica e de onboarding.
- Adicionar testes automatizados para novas funcionalidades e para o frontend.

Consulte o arquivo TODO.md para o roadmap detalhado e prioridades.

## Observações
- Os arquivos `db/suppliers.json` e `db/users.json` são mantidos apenas para histórico/backup. Toda a persistência real ocorre no MongoDB.
- Scripts de migração estão disponíveis em `db/` para transferir dados antigos para o banco.
- Para ambiente de produção, recomenda-se configurar variáveis de ambiente para a URI do MongoDB e segredos.

### Sobre o MongoDB Atlas

- O MongoDB Atlas é um serviço de banco de dados na nuvem, gerenciado pela MongoDB Inc., que oferece alta disponibilidade, backups automáticos e escalabilidade.
- O projeto utiliza a string de conexão padrão do Atlas, com autenticação por usuário e senha.
- Todos os dados de fornecedores e usuários são persistidos na coleção do banco `eskcrud` no cluster Atlas.
- Para acessar o banco via interface web, use o painel do Atlas. Para acesso local, utilize ferramentas como MongoDB Compass ou a CLI `mongosh`.
- O acesso à base pode ser restrito por IP e usuário, aumentando a segurança.

- Os arquivos `db/suppliers.json` e `db/users.json` são mantidos apenas para histórico/backup. Toda a persistência real ocorre no MongoDB.
- Scripts de migração estão disponíveis em `db/` para transferir dados antigos para o banco.
- Para ambiente de produção, recomenda-se configurar variáveis de ambiente para a URI do MongoDB e segredos.

## Licença
Este projeto está licenciado sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
