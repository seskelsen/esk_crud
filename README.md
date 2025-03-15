# Sistema de Gestão de Fornecedores

Sistema web para gerenciamento de fornecedores com Frontend em HTML/CSS/JavaScript e Backend em Python/Flask.

## Funcionalidades

- Listagem de fornecedores com ordenação e busca
- Cadastro de novos fornecedores
- Edição de fornecedores existentes
- Exclusão de fornecedores
- Validação de dados (CNPJ, email, telefone)
- Interface responsiva
- Feedback visual para todas as operações

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

- Python 3.12 ou superior
- Navegador web moderno
- Conexão com internet (para carregar CDNs)

## Instalação

1. Clone o repositório:
```bash
git clone [url-do-repositorio]
cd esk_crud
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Executando o Sistema

1. Inicie o servidor backend:
```bash
cd api
python -m flask run --debug
```

2. Abra o arquivo `frontend/index.html` em um navegador web

O sistema estará disponível em `http://localhost:5000` (API) e você pode acessar o frontend diretamente pelo arquivo HTML.

## Estrutura do Projeto

```
esk_crud/
├── api/
│   ├── app.py            # Aplicação Flask principal
│   ├── supplier.py       # Classe de modelo para fornecedores
│   ├── test_app.py      # Testes da API
│   └── test_supplier.py # Testes da classe Supplier
├── frontend/
│   ├── index.html       # Página principal
│   ├── css/
│   │   └── styles.css   # Estilos customizados
│   └── js/
│       └── script.js    # JavaScript principal
├── db/
│   └── suppliers.json   # Banco de dados JSON
├── requirements.txt     # Dependências Python
└── README.md           # Esta documentação
```

## Desenvolvimento

- Backend: API RESTful com Flask
- Frontend: HTML5 + CSS3 + JavaScript puro
- Persistência: Arquivo JSON
- Documentação: Swagger UI disponível em `/swagger-ui`

## Testes

Execute os testes usando pytest:
```bash
cd api
python -m pytest
```

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Crie um Pull Request
