# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [1.3.0] - 2025-03-15

### Adicionado

* Arquivo `.env.example` com variáveis de ambiente necessárias
* Arquivo `CONTRIBUTING.md` com diretrizes de contribuição
* Arquivo `LICENSE` com a licença MIT
* Arquivo `CODE_OF_CONDUCT.md` com código de conduta para contribuidores

### Atualizado

* Atualização do copyright para 2025 ESKEL Consulting

## [1.2.0] - 2024-02-26

### Adicionado

* Formatação automática de CNPJ (XX.XXX.XXX/XXXX-XX)
* Formatação automática de telefone para números fixos (XX XXXX-XXXX) e celulares (XX XXXXX-XXXX)

### Melhorado

* Interface do usuário com máscaras de entrada para CNPJ e telefone
* Validação e formatação de dados antes do envio ao servidor

## [1.1.0] - 2024-02-25

### Adicionado

* Documentação OpenAPI (Swagger) para todas as rotas da API
* Interface Swagger UI para teste interativo da API
* Logs detalhados para operações de exclusão
* Tratamento aprimorado de IDs no backend

### Melhorado

* Sincronização entre chaves e IDs no armazenamento JSON
* Feedback visual no frontend para operações de CRUD
* Validação de dados no backend
* Mensagens de erro mais descritivas

## [1.0.0] - 2024-02-14

### Adicionado

* Implementação inicial do CRUD de fornecedores
* Backend em Python usando Flask e armazenamento em JSON
* Frontend em HTML/JS usando Bootstrap 5
* Testes unitários para backend usando pytest
* Funcionalidades:
  * Listagem de fornecedores
  * Cadastro de novo fornecedor
  * Edição de fornecedor existente
  * Exclusão de fornecedor
  * Validação de formulários
  * Confirmação de exclusão
  * Mensagens de feedback para o usuário

### Funcionalidades

* API RESTful para gerenciamento de fornecedores
* Interface responsiva com Bootstrap
* Armazenamento em arquivo JSON
* Testes automatizados
* CORS habilitado para desenvolvimento local

### Correções

* Ajuste no processo de exclusão de fornecedores
* Correção na geração de IDs únicos
* Melhorias no tratamento de erros e logging

## [1.1.0] - 2025-03-25

### Adicionado

- Autenticação JWT para login e registro de usuários.
- Controle de acesso baseado em funções (RBAC).
- Documentação da API com Swagger UI.
- Página de login no frontend.
- Redirecionamento da raiz do servidor para o frontend.
- Suporte para servir arquivos estáticos da pasta `frontend`.

### Alterado

- Atualização do `requirements.txt` para incluir `flask-swagger-ui`.
- Melhorias na estrutura do frontend para suportar autenticação.

### Corrigido

- Problemas de conflito de rotas no backend.
- Erro ao acessar o Swagger UI devido à falta do arquivo JSON.
