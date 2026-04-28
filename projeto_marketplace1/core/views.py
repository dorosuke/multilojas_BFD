from django.db.models import Count, Q
from django.shortcuts import render
from rest_framework import permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.views import APIView

from .models import FotoProduto, Produto, User, VariacaoProduto, Vendedor
from .serializers import (
    CategoriaCreateUpdateSerializer,
    CategoriaSerializer,
    LoginSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    ProfileSerializer,
    ProfileUpdateSerializer,
    ProdutoCreateUpdateSerializer,
    ProdutoSerializer,
    RegistroCompradorSerializer,
    RegistroVendedorSerializer,
    SellerStoreSerializer,
    FotoProdutoSerializer,
    FotoProdutoUploadSerializer,
    VariacaoProdutoCreateUpdateSerializer,
    VariacaoProdutoSerializer,
    build_auth_payload,
)
from .utils import api_response


def ensure_vendor(user):
    return user.is_authenticated and user.tipo == User.UserType.VENDEDOR and hasattr(user, 'vendedor')


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
                'version': 'sprint-5',
                'endpoints': {
                    'health': '/api/health/',
                    'registro_vendedor': '/api/auth/register/vendor/',
                    'registro_comprador': '/api/auth/register/buyer/',
                    'login': '/api/auth/login/',
                    'perfil': '/api/auth/profile/',
                    'lojas_publicas': '/api/lojas/',
                    'loja_publica': '/api/lojas/<id>/',
                    'seller_categories': '/api/seller/categories/',
                    'seller_products': '/api/seller/products/',
                },
            },
            message='Backend inicial configurado com sucesso.',
        )


class RegistroVendedorView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = RegistroVendedorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return api_response(
            data=build_auth_payload(user),
            message='Vendedor cadastrado com sucesso.',
            status_code=status.HTTP_201_CREATED,
        )


class RegistroCompradorView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = RegistroCompradorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return api_response(
            data=build_auth_payload(user),
            message='Comprador cadastrado com sucesso.',
            status_code=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        return api_response(
            data=build_auth_payload(user),
            message='Login realizado com sucesso.',
        )


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return api_response(
            data=ProfileSerializer(request.user).data,
            message='Perfil carregado com sucesso.',
        )

    def put(self, request):
        serializer = ProfileUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(request.user, serializer.validated_data)
        return api_response(
            data=ProfileSerializer(request.user).data,
            message='Perfil atualizado com sucesso.',
        )


class PasswordResetRequestView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.save()
        message = 'Se o e-mail existir, um link de recuperação foi gerado.'
        return api_response(
            data=payload or {},
            message=message,
        )


class PasswordResetConfirmView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return api_response(
            message='Senha redefinida com sucesso.',
        )


class SellerStoreView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not ensure_vendor(request.user):
            return api_response(
                message='Apenas vendedores podem acessar esta área.',
                success=False,
                status_code=status.HTTP_403_FORBIDDEN,
            )

        return api_response(
            data=SellerStoreSerializer(request.user).data,
            message='Dados da loja carregados com sucesso.',
        )

    def put(self, request):
        if not ensure_vendor(request.user):
            return api_response(
                message='Apenas vendedores podem acessar esta área.',
                success=False,
                status_code=status.HTTP_403_FORBIDDEN,
            )

        serializer = ProfileUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(request.user, serializer.validated_data)
        return api_response(
            data=SellerStoreSerializer(request.user).data,
            message='Dados da loja atualizados com sucesso.',
        )


class VendorProductListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not ensure_vendor(request.user):
            return api_response(
                message='Apenas vendedores podem acessar esta área.',
                success=False,
                status_code=status.HTTP_403_FORBIDDEN,
            )

        produtos = (
            request.user.vendedor.produtos.all()
            .select_related('categoria')
            .prefetch_related('fotos', 'variacoes')
        )
        return api_response(
            data=ProdutoSerializer(produtos, many=True, context={'request': request}).data,
            message='Produtos carregados com sucesso.',
        )

    def post(self, request):
        if not ensure_vendor(request.user):
            return api_response(
                message='Apenas vendedores podem acessar esta área.',
                success=False,
                status_code=status.HTTP_403_FORBIDDEN,
            )

        serializer = ProdutoCreateUpdateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        produto = serializer.save(vendedor=request.user.vendedor)
        return api_response(
            data=ProdutoSerializer(produto, context={'request': request}).data,
            message='Produto cadastrado com sucesso.',
            status_code=status.HTTP_201_CREATED,
        )


class VendorProductDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, request, product_id):
        if not ensure_vendor(request.user):
            return None
        return (
            request.user.vendedor.produtos.filter(id=product_id)
            .select_related('categoria')
            .prefetch_related('fotos', 'variacoes')
            .first()
        )

    def get(self, request, product_id):
        produto = self.get_object(request, product_id)
        if not produto:
            return api_response(
                message='Produto não encontrado.',
                success=False,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return api_response(
            data=ProdutoSerializer(produto, context={'request': request}).data,
            message='Produto carregado com sucesso.',
        )

    def put(self, request, product_id):
        produto = self.get_object(request, product_id)
        if not produto:
            return api_response(
                message='Produto não encontrado.',
                success=False,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProdutoCreateUpdateSerializer(
            produto,
            data=request.data,
            partial=True,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return api_response(
            data=ProdutoSerializer(produto, context={'request': request}).data,
            message='Produto atualizado com sucesso.',
        )

    def delete(self, request, product_id):
        produto = self.get_object(request, product_id)
        if not produto:
            return api_response(
                message='Produto não encontrado.',
                success=False,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        produto.ativo = False
        produto.save(update_fields=['ativo'])
        return api_response(
            data=ProdutoSerializer(produto, context={'request': request}).data,
            message='Produto desativado com sucesso.',
        )


class VendorProductPhotoUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, product_id):
        if not ensure_vendor(request.user):
            return api_response(
                message='Apenas vendedores podem acessar esta área.',
                success=False,
                status_code=status.HTTP_403_FORBIDDEN,
            )

        produto = request.user.vendedor.produtos.filter(id=product_id).prefetch_related('fotos').first()
        if not produto:
            return api_response(
                message='Produto não encontrado.',
                success=False,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        serializer = FotoProdutoUploadSerializer(
            data={'fotos': request.FILES.getlist('fotos')}
        )
        serializer.is_valid(raise_exception=True)

        total_existente = produto.fotos.count()
        novas_fotos = serializer.validated_data['fotos']
        if total_existente + len(novas_fotos) > 5:
            return api_response(
                message='Cada produto pode ter no máximo 5 fotos.',
                success=False,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        criadas = []
        ordem_inicial = total_existente
        for indice, foto in enumerate(novas_fotos, start=1):
            criadas.append(
                FotoProduto.objects.create(
                    produto=produto,
                    imagem=foto,
                    ordem=ordem_inicial + indice,
                )
            )

        return api_response(
            data=FotoProdutoSerializer(criadas, many=True, context={'request': request}).data,
            message='Fotos enviadas com sucesso.',
            status_code=status.HTTP_201_CREATED,
        )


class VendorProductPhotoDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, photo_id):
        if not ensure_vendor(request.user):
            return api_response(
                message='Apenas vendedores podem acessar esta área.',
                success=False,
                status_code=status.HTTP_403_FORBIDDEN,
            )

        foto = FotoProduto.objects.filter(
            id=photo_id,
            produto__vendedor=request.user.vendedor,
        ).first()
        if not foto:
            return api_response(
                message='Foto não encontrada.',
                success=False,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        foto.delete()
        return api_response(message='Foto removida com sucesso.')


class VendorCategoryListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not ensure_vendor(request.user):
            return api_response(
                message='Apenas vendedores podem acessar esta área.',
                success=False,
                status_code=status.HTTP_403_FORBIDDEN,
            )

        categorias = request.user.vendedor.categorias.all().select_related('parent')
        return api_response(
            data=CategoriaSerializer(categorias, many=True).data,
            message='Categorias carregadas com sucesso.',
        )

    def post(self, request):
        if not ensure_vendor(request.user):
            return api_response(
                message='Apenas vendedores podem acessar esta área.',
                success=False,
                status_code=status.HTTP_403_FORBIDDEN,
            )

        serializer = CategoriaCreateUpdateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        categoria = serializer.save(vendedor=request.user.vendedor)
        return api_response(
            data=CategoriaSerializer(categoria).data,
            message='Categoria criada com sucesso.',
            status_code=status.HTTP_201_CREATED,
        )


class VendorCategoryDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, request, category_id):
        if not ensure_vendor(request.user):
            return None
        return request.user.vendedor.categorias.filter(id=category_id).select_related('parent').first()

    def get(self, request, category_id):
        categoria = self.get_object(request, category_id)
        if not categoria:
            return api_response(
                message='Categoria não encontrada.',
                success=False,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return api_response(
            data=CategoriaSerializer(categoria).data,
            message='Categoria carregada com sucesso.',
        )

    def put(self, request, category_id):
        categoria = self.get_object(request, category_id)
        if not categoria:
            return api_response(
                message='Categoria não encontrada.',
                success=False,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        serializer = CategoriaCreateUpdateSerializer(
            categoria,
            data=request.data,
            partial=True,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return api_response(
            data=CategoriaSerializer(categoria).data,
            message='Categoria atualizada com sucesso.',
        )

    def delete(self, request, category_id):
        categoria = self.get_object(request, category_id)
        if not categoria:
            return api_response(
                message='Categoria não encontrada.',
                success=False,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        categoria.ativo = False
        categoria.save(update_fields=['ativo'])
        return api_response(
            data=CategoriaSerializer(categoria).data,
            message='Categoria desativada com sucesso.',
        )


class VendorProductVariationListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_produto(self, request, product_id):
        if not ensure_vendor(request.user):
            return None
        return request.user.vendedor.produtos.filter(id=product_id).first()

    def get(self, request, product_id):
        produto = self.get_produto(request, product_id)
        if not produto:
            return api_response(
                message='Produto não encontrado.',
                success=False,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return api_response(
            data=VariacaoProdutoSerializer(produto.variacoes.all(), many=True).data,
            message='Variações carregadas com sucesso.',
        )

    def post(self, request, product_id):
        produto = self.get_produto(request, product_id)
        if not produto:
            return api_response(
                message='Produto não encontrado.',
                success=False,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        serializer = VariacaoProdutoCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        variacao = serializer.save(produto=produto)
        return api_response(
            data=VariacaoProdutoSerializer(variacao).data,
            message='Variação criada com sucesso.',
            status_code=status.HTTP_201_CREATED,
        )


class VendorProductVariationDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, request, variation_id):
        if not ensure_vendor(request.user):
            return None
        return VariacaoProduto.objects.filter(
            id=variation_id,
            produto__vendedor=request.user.vendedor,
        ).first()

    def put(self, request, variation_id):
        variacao = self.get_object(request, variation_id)
        if not variacao:
            return api_response(
                message='Variação não encontrada.',
                success=False,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        serializer = VariacaoProdutoCreateUpdateSerializer(variacao, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return api_response(
            data=VariacaoProdutoSerializer(variacao).data,
            message='Variação atualizada com sucesso.',
        )

    def delete(self, request, variation_id):
        variacao = self.get_object(request, variation_id)
        if not variacao:
            return api_response(
                message='Variação não encontrada.',
                success=False,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        variacao.delete()
        return api_response(message='Variação removida com sucesso.')


class PublicStoreListView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        lojas = (
            Vendedor.objects.filter(user__is_active=True)
            .annotate(total_produtos_ativos=Count('produtos', filter=Q(produtos__ativo=True)))
            .filter(total_produtos_ativos__gt=0)
            .order_by('-total_produtos_ativos', 'nome_loja')
        )

        data = []
        for loja in lojas:
            data.append({
                'id': loja.id,
                'nome_loja': loja.nome_loja,
                'logo_url': loja.logo_url,
                'descricao_resumida': (loja.descricao_loja or '')[:160],
                'total_produtos_ativos': loja.total_produtos_ativos,
            })

        return api_response(
            data=data,
            message='Lojas carregadas com sucesso.',
        )


class PublicStoreDetailView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, store_id):
        loja = Vendedor.objects.filter(id=store_id, user__is_active=True).first()
        if not loja:
            return api_response(
                message='Loja não encontrada.',
                success=False,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        page = int(request.query_params.get('page', 1) or 1)
        page_size = int(request.query_params.get('page_size', 12) or 12)
        page_size = max(1, min(page_size, 50))
        offset = (max(page, 1) - 1) * page_size

        produtos_qs = (
            loja.produtos.filter(ativo=True, estoque__gt=0)
            .select_related('categoria')
            .prefetch_related('fotos', 'variacoes')
        )
        total = produtos_qs.count()
        itens = produtos_qs[offset:offset + page_size]

        return api_response(
            data={
                'loja': {
                    'id': loja.id,
                    'nome_loja': loja.nome_loja,
                    'descricao_loja': loja.descricao_loja,
                    'logo_url': loja.logo_url,
                },
                'produtos': ProdutoSerializer(itens, many=True, context={'request': request}).data,
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total': total,
                },
            },
            message='Loja carregada com sucesso.',
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
    return render(request, 'pages/seller_dashboard.html')


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
    context = {
        'uid': request.GET.get('uid', ''),
        'token': request.GET.get('token', ''),
    }
    return render(request, 'pages/forgot_password.html', context)


def profile_page(request):
    return render(request, 'pages/profile.html')


def seller_store_page(request):
    return render(request, 'pages/my_store.html')


def seller_products_page(request):
    return render(request, 'pages/my_products.html')
