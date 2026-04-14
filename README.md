# Projeto Marketplace

## Tecnologias

- Python 3.12
- Django 6
- Django REST Framework
- PostgreSQL
- django-cors-headers
- python-decouple
- dj-database-url

## Estrutura

```text
projeto_marketPlace/
├── .env.example
├── CONTRIBUTING.md
├── README.md
├── requirements.txt
└── projeto_marketplace1/
    ├── core/
    ├── manage.py
    ├── projeto_marketplace1/
    └── template/
```

## Como rodar

1. Ative o ambiente virtual.
2. Instale as dependencias:

```bash
pip install -r requirements.txt
```

3. Crie o arquivo `.env` com base no `.env.example`.
4. Configure o PostgreSQL no `.env`.
5. Rode as migrations:

```bash
python projeto_marketplace1/manage.py migrate
```

6. Inicie o servidor:

```bash
python projeto_marketplace1/manage.py runserver
```

## Variaveis de ambiente

Exemplo em `.env.example`:

```env
SECRET_KEY=troque-esta-chave
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
TIME_ZONE=America/Sao_Paulo
DATABASE_URL=postgres://postgres:postgres@localhost:5432/projeto_marketplace
DB_CONN_MAX_AGE=60
DB_SSL_REQUIRE=False
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

## Endpoint inicial

Foi criado um endpoint de health-check:

```text
GET /api/health/
```

Resposta esperada:

```json
{
  "success": true,
  "data": {
    "service": "backend",
    "status": "ok"
  },
  "message": "API base pronta para o projeto."
}
```

Tambem existe uma rota raiz da API:

```text
GET /api/
```

## Sobre o sistema

O projeto e uma base de marketplace para pequenos empreendedores e compradores.
Hoje o sistema ja possui a estrutura inicial do backend em Django REST Framework e um frontend em templates Django para os fluxos de autenticacao e perfil.

O sistema trabalha com dois tipos de usuario:

- vendedor
- comprador

## O que ja esta funcionando

Backend:

- configuracao inicial do projeto com Django + DRF
- modelagem de `User`, `Vendedor` e `Comprador`
- cadastro de vendedor
- cadastro de comprador
- login com JWT
- consulta de perfil autenticado
- atualizacao de perfil autenticado
- recuperacao de senha com geracao de link
- resposta padronizada em JSON

Frontend:

- pagina inicial
- tela de cadastro com alternancia entre vendedor e comprador
- tela de login integrada com a API
- tela de recuperacao de senha
- tela de perfil protegida e editavel
- persistencia simples da sessao no navegador com JWT

## Como testar o sistema atual

1. Acesse `/api/front/cadastro/` e crie uma conta de vendedor ou comprador.
2. Depois do cadastro, o usuario sera autenticado e redirecionado para `/api/front/perfil/`.
3. Acesse `/api/front/login/` para entrar com uma conta existente.
4. Acesse `/api/front/perfil/` para consultar e editar os dados do usuario autenticado.
5. Acesse `/api/front/recuperar-senha/` para solicitar o link de redefinicao.
6. Use o `reset_link` retornado pela API para abrir a tela de nova senha no navegador.

## Frontend em templates

Rotas visuais disponiveis:

- `/`
- `/api/front/busca/`
- `/api/front/login/`
- `/api/front/cadastro/`
- `/api/front/recuperar-senha/`
- `/api/front/perfil/`
- `/api/front/loja/moda-solar/`
- `/api/front/produto/vestido-floral/`
- `/api/front/vendedor/`
- `/api/front/comprador/`

Rotas da autenticacao ja integradas ao front:

- `/api/auth/register/vendor/`
- `/api/auth/register/buyer/`
- `/api/auth/login/`
- `/api/auth/profile/`
- `/api/auth/password-reset/request/`
- `/api/auth/password-reset/confirm/`

## Documentos de apoio

- `CONTRIBUTING.md`
- `docs/DECISOES_TECNICAS.md`
