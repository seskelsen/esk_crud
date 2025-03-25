# Sistema de Gestão de Fornecedores

## Visão Geral
Este é um sistema de gestão de fornecedores que permite:
- Gerenciar fornecedores (CRUD completo)
- Autenticação e autorização com JWT
- Controle de acesso baseado em funções (RBAC)
- Documentação da API com Swagger

## Funcionalidades
- **Autenticação JWT**: Login e registro de usuários com tokens JWT.
- **Controle de Acesso**: Apenas administradores podem gerenciar usuários.
- **Gestão de Fornecedores**: CRUD completo para fornecedores.
- **Swagger UI**: Documentação interativa da API.
- **Frontend**: Interface web para gerenciar fornecedores.

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

4. Inicie o servidor:
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
│   ├── supplier.py          # Lógica de fornecedores
│   ├── user.py              # Lógica de usuários
│   ├── test_app.py          # Testes para app.py
│   ├── test_supplier.py     # Testes para supplier.py
│   └── __pycache__/         # Arquivos compilados
├── db/
│   ├── suppliers.json       # Banco de dados de fornecedores
│   └── users.json           # Banco de dados de usuários
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
- Persistência: Arquivo JSON
- Documentação: Swagger UI disponível em `/swagger-ui`

## Testes
Para rodar os testes automatizados:
```bash
pytest
```

## Contribuição
Contribuições são bem-vindas! Leia o arquivo `CONTRIBUTING.md` para mais informações.

## Licença
Este projeto está licenciado sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
