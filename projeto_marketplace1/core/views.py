from django.shortcuts import render
from rest_framework.views import APIView

from .utils import api_response


class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return api_response(
            data={'service': 'backend', 'status': 'ok'},
            message='API base pronta para o projeto.',
        )


class ApiRootView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return api_response(
            data={
                'project': 'MultiLojas',
                'version': 'base-inicial',
                'endpoints': {
                    'health': '/api/health/',
                },
            },
            message='Backend inicial configurado com sucesso.',
        )


def home_page(request):
    context = {
        'featured_stores': [
            {'name': 'Moda Solar', 'slug': 'moda-solar', 'category': 'Moda feminina'},
            {'name': 'Casa Aurora', 'slug': 'casa-aurora', 'category': 'Decoracao'},
            {'name': 'Sabor da Vila', 'slug': 'sabor-da-vila', 'category': 'Alimentos'},
        ],
        'highlights': [
            {'name': 'Vestido Floral', 'store': 'Moda Solar', 'price': 'R$ 89,90'},
            {'name': 'Kit Velas Artesanais', 'store': 'Casa Aurora', 'price': 'R$ 49,90'},
            {'name': 'Cesta Gourmet', 'store': 'Sabor da Vila', 'price': 'R$ 129,90'},
        ],
        'steps': [
            'Visitante descobre lojas e produtos',
            'Comprador cria conta e entra na plataforma',
            'Vendedor gerencia catalogo e pedidos',
        ],
        'features': [
            'Busca unificada entre lojas',
            'Vitrine publica por vendedor',
            'Fluxo de autenticacao em templates',
            'Base pronta para consumo da API',
        ],
    }
    return render(request, 'pages/home.html', context)


def search_page(request):
    context = {
        'filters': ['Categoria', 'Faixa de preco', 'Loja'],
        'results': [
            {'name': 'Vestido Floral', 'store': 'Moda Solar', 'price': 'R$ 89,90', 'category': 'Moda'},
            {'name': 'Kit Velas Artesanais', 'store': 'Casa Aurora', 'price': 'R$ 49,90', 'category': 'Decoracao'},
            {'name': 'Cesta Gourmet', 'store': 'Sabor da Vila', 'price': 'R$ 129,90', 'category': 'Presentes'},
        ],
    }
    return render(request, 'pages/search.html', context)


def store_page(request, slug='loja-modelo'):
    context = {
        'store': {
            'name': 'Moda Solar',
            'slug': slug,
            'description': 'Loja rascunho para apresentar a vitrine publica do vendedor.',
            'contact': 'contato@modasolar.com',
            'city': 'Sao Paulo - SP',
            'categories': ['Vestidos', 'Blusas', 'Acessorios'],
        },
        'products': [
            {'name': 'Vestido Floral', 'price': 'R$ 89,90', 'badge': 'Destaque'},
            {'name': 'Blusa Linho', 'price': 'R$ 59,90', 'badge': 'Novo'},
            {'name': 'Bolsa Artesanal', 'price': 'R$ 119,90', 'badge': 'Limitado'},
        ],
    }
    return render(request, 'pages/store.html', context)


def product_page(request, slug='produto-modelo'):
    context = {
        'product': {
            'name': 'Vestido Floral',
            'slug': slug,
            'price': 'R$ 89,90',
            'description': 'Pagina de rascunho para mostrar fotos, variacoes, frete e avaliacoes.',
            'stock': 10,
            'store': 'Moda Solar',
            'variations': ['P', 'M', 'G'],
            'colors': ['Vermelho', 'Azul', 'Verde'],
        },
        'reviews': [
            {'author': 'Maria', 'rating': '5/5', 'comment': 'Muito bonito e chegou rapido.'},
            {'author': 'Joao', 'rating': '4/5', 'comment': 'Boa qualidade, embalagem caprichada.'},
        ],
    }
    return render(request, 'pages/product.html', context)


def seller_dashboard_page(request):
    context = {
        'stats': [
            {'label': 'Produtos ativos', 'value': '18'},
            {'label': 'Pedidos pendentes', 'value': '6'},
            {'label': 'Faturamento do mes', 'value': 'R$ 3.240'},
        ],
        'tasks': [
            'Cadastrar novos produtos',
            'Aprovar comprovantes PIX',
            'Atualizar estoque dos itens mais vendidos',
        ],
    }
    return render(request, 'pages/seller_dashboard.html', context)


def buyer_dashboard_page(request):
    context = {
        'orders': [
            {'code': '#1032', 'status': 'Aguardando aprovacao', 'total': 'R$ 129,90'},
            {'code': '#1018', 'status': 'Enviado', 'total': 'R$ 59,90'},
        ],
        'next_step': 'Enviar comprovante PIX ou acompanhar status do pedido.',
    }
    return render(request, 'pages/buyer_dashboard.html', context)


def login_page(request):
    return render(request, 'pages/login.html')


def register_page(request):
    context = {
        'profiles': [
            'Sou vendedor',
            'Sou comprador',
        ]
    }
    return render(request, 'pages/register.html', context)


def forgot_password_page(request):
    return render(request, 'pages/forgot_password.html')


def profile_page(request):
    context = {
        'sections': [
            {'title': 'Dados pessoais', 'description': 'Nome, e-mail, telefone e endereco principal.'},
            {'title': 'Seguranca', 'description': 'Troca de senha e revisao de acesso da conta.'},
            {'title': 'Preferencias', 'description': 'Tipo de perfil, notificacoes e dados da loja.'},
        ]
    }
    return render(request, 'pages/profile.html', context)
