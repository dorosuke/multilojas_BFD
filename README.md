# Projeto Marketplace MultiLojas

Marketplace acadêmico com vitrine pública, painel de vendedor, carrinho por loja, frete por CEP, pagamento PIX com comprovante e aprovação do pedido pelo vendedor.

## Visão Geral

O sistema organiza várias lojas em uma única plataforma.
O comprador navega sem precisar fazer login para ver vitrines, categorias e produtos.
O vendedor gerencia loja, produtos, pedidos, comprovantes e rastreio.

## Tecnologias

- Python 3.12
- Django
- Django REST Framework
- SQLite no desenvolvimento local
- PostgreSQL com configuração via `.env`
- django-cors-headers
- python-decouple
- dj-database-url
- Pillow
- ReportLab

## Estrutura

```text
projeto_marketPlace/
├── README.md
├── docs/
│   ├── ACOMPANHAMENTO_DAS_SPRINTS.md
│   └── DECISOES_TECNICAS.md
└── projeto_marketplace1/
    ├── core/
    ├── manage.py
    ├── media/
    └── template/
```

## Como executar

> Se `python` não funcionar, use `.venv/bin/python` ou ative o ambiente virtual.

1. Crie e ative o ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Configure o ambiente:

```bash
cp .env.example .env
```

4. Rode as migrations:

```bash
python projeto_marketplace1/manage.py migrate
```

5. Carregue os dados de demonstração:

```bash
python projeto_marketplace1/manage.py seed_demo_data
```

6. Inicie o sistema:

```bash
python projeto_marketplace1/manage.py runserver
```

## Acessos de teste

- Admin: `admin@multilojas.local` / `Admin@12345`
- Comprador demo: `comprador@demo.com` / `Comprador@12345`
- Vendedor demo: `modasolar@demo.com` / `Moda@12345`
- Vendedor demo: `casaaurora@demo.com` / `Casa@12345`
- Vendedor demo: `sabordavila@demo.com` / `Sabor@12345`
- Vendedor demo: `techprime@demo.com` / `Tech@12345`
- Vendedor demo: `atelierrosa@demo.com` / `Atelie@12345`

## Endereços de teste

Use qualquer um destes no carrinho:

- CEP `01001000` e endereço `Praça da Sé, 100, Sé, São Paulo - SP`
- CEP `01310000` e endereço `Avenida Paulista, 1000, Bela Vista, São Paulo - SP`

O carrinho já tem botões para preencher esses endereços automaticamente. Ao finalizar, o sistema cria o pedido, baixa o estoque vendido e redireciona para a página PIX.

## Funcionalidades principais

- Home com carrossel de lojas em destaque e produtos
- Busca com filtros por termo, loja, categoria e faixa de preço
- Páginas públicas de loja, produto e categorias
- Carrinho salvo no navegador, agrupado por loja
- Frete calculado por CEP usando BrasilAPI/ViaCEP como apoio, sem Correios
- Finalização de pedido com endereço e resumo
- Página PIX com QR Code e upload de comprovante
- Aprovação/rejeição de pedido pelo vendedor
- Código de rastreio e etiqueta PDF
- Avaliação de produtos após entrega
- Painel de vendedor, perfil, recuperação de senha e painel admin

## Rotas úteis

### Frontend em templates

- `/`
- `/api/front/busca/`
- `/api/front/categorias/`
- `/api/front/carrinho/`
- `/api/front/pagamento-pix/`
- `/api/front/pedidos/`
- `/api/front/login/`
- `/api/front/cadastro/`
- `/api/front/recuperar-senha/`
- `/api/front/perfil/`
- `/api/front/vendedor/`
- `/api/front/vendedor/pedidos/`
- `/api/front/minha-loja/`
- `/api/front/meus-produtos/`

### APIs principais

- `GET /api/health/`
- `POST /api/auth/register/vendor/`
- `POST /api/auth/register/buyer/`
- `POST /api/auth/login/`
- `GET/PUT /api/auth/profile/`
- `GET /api/lojas/`
- `GET /api/lojas/<id>/`
- `GET /api/lojas/<id>/produtos/`
- `GET /api/produtos/<id>/`
- `GET/POST /api/produtos/<id>/avaliacoes/`
- `GET /api/busca/`
- `GET /api/busca/filtros/`
- `POST /api/shipping/quote/`
- `POST /api/orders/`
- `POST /api/orders/<id>/payment-proof/`
- `GET /api/buyer/orders/`
- `GET /api/vendedor/pedidos/`
- `PUT /api/vendedor/pedidos/<id>/aprovar/`
- `PUT /api/vendedor/pedidos/<id>/rejeitar/`
- `PUT /api/vendedor/pedidos/<id>/enviar/`
- `PUT /api/vendedor/pedidos/<id>/entregar/`
- `GET /api/vendedor/pedidos/<id>/label/`

## Observações para apresentação

- O projeto já sobe com dados demo para a home não ficar vazia.
- O frete usa CEP e fallback por região/estado.
- O fluxo PIX pede o comprovante e muda o status do pedido para aprovação do vendedor.
- O carrinho é por loja, para manter a lógica do marketplace organizada.

## Admin

Painel Django:

```text
/admin/
```

## Documentação do projeto

- `docs/ACOMPANHAMENTO_DAS_SPRINTS.md`
- `docs/DECISOES_TECNICAS.md`
