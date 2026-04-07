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

## Documentos de apoio

- `CONTRIBUTING.md`
- `docs/DECISOES_TECNICAS.md`
