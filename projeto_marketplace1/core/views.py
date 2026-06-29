from django.db import models, transaction
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from reportlab.lib.pagesizes import A6
from reportlab.pdfgen import canvas
import io
from rest_framework import permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.views import APIView
from decimal import Decimal

from .models import AvaliacaoProduto, Categoria, FotoProduto, Pedido, PedidoItem, Produto, User, VariacaoProduto, Vendedor, get_or_create_vendedor_for_user
from .serializers import (
    CategoriaCreateUpdateSerializer,
    CategoriaSerializer,
    AvaliacaoProdutoCreateSerializer,
    AvaliacaoProdutoSerializer,
    OrderRejectSerializer,
    OrderShipSerializer,
    PaymentProofUploadSerializer,
    LoginSerializer,
    OrderCreateSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    PedidoSerializer,
    ProfileSerializer,
    ProfileUpdateSerializer,
    PublicProductCardSerializer,
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
from .notifications import notify_order_approved, notify_order_rejected, notify_order_shipped
from .shipping import calculate_shipping_quote


def ensure_vendor(user):
    if not user.is_authenticated:
        return False
    if user.tipo == User.UserType.VENDEDOR and hasattr(user, 'vendedor'):
        return True
    return get_or_create_vendedor_for_user(user) is not None


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
                    'version': 'sprint-final',
                    'endpoints': {
                        'health': '/api/health/',
                        'registro_vendedor': '/api/auth/register/vendor/',
                        'registro_comprador': '/api/auth/register/buyer/',
                        'login': '/api/auth/login/',
                        'perfil': '/api/auth/profile/',
                        'lojas_publicas': '/api/lojas/',
                        'loja_publica': '/api/lojas/<id>/',
                        'loja_produtos': '/api/lojas/<id>/produtos/?category=<id>&sort=price_asc',
                        'busca': '/api/busca/?q=termo',
                        'busca_filtros': '/api/busca/filtros/?q=termo',
                        'seller_categories': '/api/seller/categories/',
                        'seller_products': '/api/seller/products/',
                        'orders_create': '/api/orders/',
                        'shipping_quote': '/api/shipping/quote/',
                        'buyer_orders': '/api/buyer/orders/',
                        'seller_orders': '/api/vendedor/pedidos/',
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

        vendedor = get_or_create_vendedor_for_user(request.user)
        produtos = (
            vendedor.produtos.all()
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
        vendedor = get_or_create_vendedor_for_user(request.user)
        produto = serializer.save(vendedor=vendedor)
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
        vendedor = get_or_create_vendedor_for_user(request.user)
        return (
            vendedor.produtos.filter(id=product_id)
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

        vendedor = get_or_create_vendedor_for_user(request.user)
        produto = vendedor.produtos.filter(id=product_id).prefetch_related('fotos').first()
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

        vendedor = get_or_create_vendedor_for_user(request.user)
        foto = FotoProduto.objects.filter(id=photo_id, produto__vendedor=vendedor).first()
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

        vendedor = get_or_create_vendedor_for_user(request.user)
        categorias = vendedor.categorias.all().select_related('parent')
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
        vendedor = get_or_create_vendedor_for_user(request.user)
        categoria = serializer.save(vendedor=vendedor)
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
        vendedor = get_or_create_vendedor_for_user(request.user)
        return vendedor.categorias.filter(id=category_id).select_related('parent').first()

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
        vendedor = get_or_create_vendedor_for_user(request.user)
        return vendedor.produtos.filter(id=product_id).first()

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
        vendedor = get_or_create_vendedor_for_user(request.user)
        return VariacaoProduto.objects.filter(
            id=variation_id,
            produto__vendedor=vendedor,
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
            produtos_preview = []
            produtos = (
                Produto.objects.filter(vendedor=loja, ativo=True, estoque__gt=0)
                .prefetch_related('fotos')
                .order_by('-destaque', '-data_cadastro', 'id')[:3]
            )
            for produto in produtos:
                foto = produto.fotos.first()
                produtos_preview.append({
                    'id': produto.id,
                    'nome': produto.nome,
                    'preco': produto.preco,
                    'imagem_url': request.build_absolute_uri(foto.imagem.url) if foto else '',
                    'estoque': produto.estoque,
                })

            data.append({
                'id': loja.id,
                'nome_loja': loja.nome_loja,
                'logo_url': loja.logo_url,
                'descricao_resumida': (loja.descricao_loja or '')[:160],
                'total_produtos_ativos': loja.total_produtos_ativos,
                'produtos_preview': produtos_preview,
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


class PublicStoreProductsView(APIView):
    """
    Sprint 7: lista pública de produtos da loja, com filtros básicos.
    """

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

        category_id = (request.query_params.get('category') or '').strip()
        sort = (request.query_params.get('sort') or '').strip()

        page = int(request.query_params.get('page', 1) or 1)
        page_size = int(request.query_params.get('page_size', 12) or 12)
        page_size = max(1, min(page_size, 50))
        offset = (max(page, 1) - 1) * page_size

        qs = (
            loja.produtos.filter(ativo=True, estoque__gt=0)
            .select_related('categoria')
            .prefetch_related('fotos', 'variacoes')
        )

        if category_id and category_id.isdigit():
            qs = qs.filter(categoria_id=int(category_id))

        if sort == 'price_asc':
            qs = qs.order_by('preco', '-destaque', '-data_cadastro', 'id')
        elif sort == 'price_desc':
            qs = qs.order_by('-preco', '-destaque', '-data_cadastro', 'id')
        else:
            qs = qs.order_by('-destaque', '-data_cadastro', 'id')

        total = qs.count()
        itens = qs[offset:offset + page_size]

        categories = (
            qs.exclude(categoria_id=None)
            .values('categoria_id', 'categoria__nome')
            .annotate(total=Count('id'))
            .order_by('-total', 'categoria__nome')
        )

        return api_response(
            data={
                'loja': {
                    'id': loja.id,
                    'nome_loja': loja.nome_loja,
                    'logo_url': loja.logo_url,
                },
                'produtos': ProdutoSerializer(itens, many=True, context={'request': request}).data,
                'categories': [{'id': c['categoria_id'], 'nome': c['categoria__nome'], 'total': c['total']} for c in categories],
                'pagination': {'page': page, 'page_size': page_size, 'total': total},
            },
            message='Produtos da loja carregados com sucesso.',
        )


class PublicProductDetailView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, product_id):
        produto = (
            Produto.objects.filter(id=product_id, ativo=True, estoque__gt=0)
            .select_related('categoria', 'vendedor')
            .prefetch_related('fotos', 'variacoes')
            .first()
        )
        if not produto:
            return api_response(
                message='Produto não encontrado.',
                success=False,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        reviews = produto.avaliacoes.select_related('comprador').order_by('-data_avaliacao', '-id')[:8]
        stats = produto.avaliacoes.aggregate(avg=models.Avg('nota'), total=Count('id'))
        can_review = False
        if request.user.is_authenticated and request.user.tipo == User.UserType.COMPRADOR:
            can_review = Pedido.objects.filter(
                comprador=request.user,
                status=Pedido.Status.ENTREGUE,
                itens__produto=produto,
            ).exists()

        return api_response(
            data={
                'produto': ProdutoSerializer(produto, context={'request': request}).data,
                'loja': {
                    'id': produto.vendedor_id,
                    'nome_loja': produto.vendedor.nome_loja,
                    'logo_url': produto.vendedor.logo_url,
                    'chave_pix': produto.vendedor.chave_pix,
                },
                'reviews': AvaliacaoProdutoSerializer(reviews, many=True).data,
                'review_stats': {
                    'average': round(float(stats['avg'] or 0), 1),
                    'total': stats['total'],
                },
                'can_review': can_review,
            },
            message='Produto carregado com sucesso.',
        )


class PublicProductReviewView(APIView):
    permission_classes = [permissions.AllowAny]

    def get_product(self, product_id):
        return Produto.objects.filter(id=product_id, ativo=True).first()

    def get(self, request, product_id):
        produto = self.get_product(product_id)
        if not produto:
            return api_response(
                message='Produto não encontrado.',
                success=False,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        avaliacoes = produto.avaliacoes.select_related('comprador').order_by('-data_avaliacao', '-id')[:30]
        stats = produto.avaliacoes.aggregate(avg=models.Avg('nota'), total=Count('id'))
        return api_response(
            data={
                'stats': {
                    'average': round(float(stats['avg'] or 0), 1),
                    'total': stats['total'],
                },
                'reviews': AvaliacaoProdutoSerializer(avaliacoes, many=True).data,
            },
            message='Avaliações carregadas com sucesso.',
        )

    def post(self, request, product_id):
        if not request.user.is_authenticated:
            return api_response(
                message='Faça login como comprador para avaliar o produto.',
                success=False,
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        if request.user.tipo != User.UserType.COMPRADOR:
            return api_response(
                message='Apenas compradores podem avaliar produtos.',
                success=False,
                status_code=status.HTTP_403_FORBIDDEN,
            )

        produto = self.get_product(product_id)
        if not produto:
            return api_response(
                message='Produto não encontrado.',
                success=False,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        has_delivered_order = Pedido.objects.filter(
            comprador=request.user,
            status=Pedido.Status.ENTREGUE,
            itens__produto=produto,
        ).exists()
        if not has_delivered_order:
            return api_response(
                message='Você só pode avaliar após receber o pedido com esse produto.',
                success=False,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AvaliacaoProdutoCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pedido = (
            Pedido.objects.filter(comprador=request.user, status=Pedido.Status.ENTREGUE, itens__produto=produto)
            .order_by('-created_at')
            .first()
        )
        avaliacao, _ = AvaliacaoProduto.objects.update_or_create(
            comprador=request.user,
            produto=produto,
            pedido=pedido,
            defaults={
                'nota': serializer.validated_data['nota'],
                'comentario': serializer.validated_data.get('comentario', ''),
            },
        )
        return api_response(
            data=AvaliacaoProdutoSerializer(avaliacao).data,
            message='Avaliação registrada com sucesso.',
            status_code=status.HTTP_201_CREATED,
        )


class PublicShowcaseView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        per_store = int(request.query_params.get('per_store', 8) or 8)
        per_store = max(1, min(per_store, 20))

        lojas = (
            Vendedor.objects.filter(user__is_active=True)
            .annotate(total_produtos_ativos=Count('produtos', filter=Q(produtos__ativo=True)))
            .filter(total_produtos_ativos__gt=0)
            .order_by('-total_produtos_ativos', 'nome_loja')
        )

        produtos = (
            Produto.objects.filter(ativo=True, estoque__gt=0, vendedor__in=lojas)
            .select_related('categoria', 'vendedor')
            .prefetch_related('fotos', 'variacoes')
            .order_by('-destaque', '-data_cadastro', 'id')
        )

        por_loja = {}
        for produto in produtos:
            bucket = por_loja.setdefault(produto.vendedor_id, [])
            if len(bucket) >= per_store:
                continue
            bucket.append(ProdutoSerializer(produto, context={'request': request}).data)

        data = []
        for loja in lojas:
            itens = por_loja.get(loja.id, [])
            if not itens:
                continue
            data.append({
                'loja': {
                    'id': loja.id,
                    'nome_loja': loja.nome_loja,
                    'logo_url': loja.logo_url,
                    'descricao_resumida': (loja.descricao_loja or '')[:160],
                },
                'produtos': itens,
            })

        return api_response(
            data=data,
            message='Vitrine carregada com sucesso.',
        )


class PublicSearchView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        q = (request.query_params.get('q') or '').strip()
        sort = (request.query_params.get('sort') or 'relevance').strip()
        category_ids = (request.query_params.get('categories') or '').strip()
        store_ids = (request.query_params.get('stores') or '').strip()
        min_price = (request.query_params.get('min_price') or '').strip()
        max_price = (request.query_params.get('max_price') or '').strip()

        page = int(request.query_params.get('page', 1) or 1)
        page_size = int(request.query_params.get('page_size', 24) or 24)
        page_size = max(1, min(page_size, 60))
        page = max(page, 1)
        offset = (page - 1) * page_size

        qs = (
            Produto.objects.filter(ativo=True, estoque__gt=0, vendedor__user__is_active=True)
            .select_related('vendedor', 'categoria')
            .prefetch_related('fotos')
        )

        if q:
            qs = qs.filter(
                Q(nome__icontains=q)
                | Q(descricao__icontains=q)
                | Q(vendedor__nome_loja__icontains=q)
                | Q(categoria__nome__icontains=q)
            )

        if category_ids:
            ids = [int(x) for x in category_ids.split(',') if x.strip().isdigit()]
            if ids:
                qs = qs.filter(categoria_id__in=ids)

        if store_ids:
            ids = [int(x) for x in store_ids.split(',') if x.strip().isdigit()]
            if ids:
                qs = qs.filter(vendedor_id__in=ids)

        if min_price:
            try:
                qs = qs.filter(preco__gte=min_price)
            except Exception:
                pass

        if max_price:
            try:
                qs = qs.filter(preco__lte=max_price)
            except Exception:
                pass

        if sort == 'price_asc':
            qs = qs.order_by('preco', '-destaque', '-data_cadastro', 'id')
        elif sort == 'price_desc':
            qs = qs.order_by('-preco', '-destaque', '-data_cadastro', 'id')
        else:
            if q:
                score = (
                    models.Case(models.When(nome__icontains=q, then=models.Value(3)), default=models.Value(0), output_field=models.IntegerField())
                    + models.Case(models.When(vendedor__nome_loja__icontains=q, then=models.Value(2)), default=models.Value(0), output_field=models.IntegerField())
                    + models.Case(models.When(descricao__icontains=q, then=models.Value(1)), default=models.Value(0), output_field=models.IntegerField())
                    + models.Case(models.When(categoria__nome__icontains=q, then=models.Value(1)), default=models.Value(0), output_field=models.IntegerField())
                )
                qs = qs.annotate(_score=score).order_by('-_score', '-destaque', '-data_cadastro', 'id')
            else:
                qs = qs.order_by('-destaque', '-data_cadastro', 'id')

        total = qs.count()
        items = qs[offset:offset + page_size]

        return api_response(
            data={
                'results': PublicProductCardSerializer(items, many=True, context={'request': request}).data,
                'pagination': {'page': page, 'page_size': page_size, 'total': total},
            },
            message='Busca carregada com sucesso.',
        )


class PublicSearchFiltersView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        q = (request.query_params.get('q') or '').strip()

        qs = Produto.objects.filter(ativo=True, estoque__gt=0, vendedor__user__is_active=True).select_related('vendedor', 'categoria')
        if q:
            qs = qs.filter(
                Q(nome__icontains=q)
                | Q(descricao__icontains=q)
                | Q(vendedor__nome_loja__icontains=q)
                | Q(categoria__nome__icontains=q)
            )

        stores = (
            qs.values('vendedor_id', 'vendedor__nome_loja', 'vendedor__logo_url')
            .annotate(total=Count('id'))
            .order_by('-total', 'vendedor__nome_loja')
        )
        categories = (
            qs.exclude(categoria_id=None)
            .values('categoria_id', 'categoria__nome')
            .annotate(total=Count('id'))
            .order_by('-total', 'categoria__nome')
        )

        price = qs.aggregate(min=models.Min('preco'), max=models.Max('preco'))

        return api_response(
            data={
                'stores': [
                    {'id': s['vendedor_id'], 'nome_loja': s['vendedor__nome_loja'], 'logo_url': s['vendedor__logo_url'], 'total': s['total']}
                    for s in stores
                ],
                'categories': [
                    {'id': c['categoria_id'], 'nome': c['categoria__nome'], 'total': c['total']}
                    for c in categories
                ],
                'price': {'min': price['min'], 'max': price['max']},
            },
            message='Filtros carregados com sucesso.',
        )


class AdminDashboardView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        total_users = User.objects.count()
        total_sellers = User.objects.filter(tipo=User.UserType.VENDEDOR).count()
        total_buyers = User.objects.filter(tipo=User.UserType.COMPRADOR).count()
        total_stores = Vendedor.objects.count()
        total_categories = Categoria.objects.count()

        total_products = Produto.objects.count()
        active_products = Produto.objects.filter(ativo=True).count()
        public_products = Produto.objects.filter(ativo=True, estoque__gt=0).count()
        out_of_stock = Produto.objects.filter(ativo=True, estoque=0).count()
        low_stock = Produto.objects.filter(ativo=True, estoque__gt=0, estoque__lt=5).count()

        low_stock_items = (
            Produto.objects.filter(ativo=True, estoque__gt=0, estoque__lt=5)
            .select_related('vendedor')
            .order_by('estoque', '-data_cadastro')[:10]
        )

        recent_products = (
            Produto.objects.select_related('vendedor', 'categoria')
            .order_by('-data_cadastro', '-id')[:12]
        )

        users = (
            User.objects.order_by('-is_superuser', '-is_staff', 'tipo', 'nome', 'email')[:50]
        )

        return api_response(
            data={
                'stats': {
                    'users': total_users,
                    'sellers': total_sellers,
                    'buyers': total_buyers,
                    'stores': total_stores,
                    'categories': total_categories,
                    'products': total_products,
                    'products_active': active_products,
                    'products_public': public_products,
                    'products_low_stock': low_stock,
                    'products_out_of_stock': out_of_stock,
                },
                'users': [
                    {
                        'id': user.id,
                        'nome': user.nome,
                        'email': user.email,
                        'telefone': user.telefone,
                        'tipo': user.tipo,
                        'is_active': user.is_active,
                        'is_staff': user.is_staff,
                        'is_superuser': user.is_superuser,
                    }
                    for user in users
                ],
                'low_stock': [
                    {
                        'id': produto.id,
                        'nome': produto.nome,
                        'preco': produto.preco,
                        'estoque': produto.estoque,
                        'ativo': produto.ativo,
                        'loja': {
                            'id': produto.vendedor_id,
                            'nome_loja': produto.vendedor.nome_loja,
                        },
                    }
                    for produto in low_stock_items
                ],
                'recent_products': [
                    {
                        'id': produto.id,
                        'nome': produto.nome,
                        'preco': produto.preco,
                        'estoque': produto.estoque,
                        'ativo': produto.ativo,
                        'loja': {
                            'id': produto.vendedor_id,
                            'nome_loja': produto.vendedor.nome_loja,
                        },
                        'categoria': produto.categoria.nome if produto.categoria_id else None,
                    }
                    for produto in recent_products
                ],
                'notes': [
                    'O Django Admin é o CRUD oficial de usuários, lojas, produtos, pedidos e categorias.',
                    'A vitrine pública só mostra lojas que possuem produtos ativos com estoque.',
                    'Produtos decorativos do front foram removidos: se aparecer na home, veio do banco.',
                ],
            },
            message='Dashboard administrativo carregado com sucesso.',
        )


class OrderCreateView(APIView):
    """
    Sprint 8: criação de pedido (carrinho por loja + frete + endereço).
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if request.user.tipo != User.UserType.COMPRADOR and not request.user.is_staff:
            return api_response(
                message='Apenas compradores ou administradores podem finalizar pedidos.',
                success=False,
                status_code=status.HTTP_403_FORBIDDEN,
            )

        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        store_id = serializer.validated_data['store_id']
        shipping_address = serializer.validated_data['shipping_address']
        shipping_postal_code = serializer.validated_data.get('shipping_postal_code', '')
        items = serializer.validated_data['items']

        loja = Vendedor.objects.filter(id=store_id, user__is_active=True).first()
        if not loja:
            return api_response(
                message='Loja não encontrada.',
                success=False,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        total_qty = sum(int(it['quantity']) for it in items)
        shipping_quote = calculate_shipping_quote(loja, shipping_postal_code, total_qty, shipping_address)
        shipping_value = shipping_quote['value']

        with transaction.atomic():
            subtotal = Decimal('0.00')
            locked_products = {}
            for it in items:
                pid = it['product_id']
                qty = int(it['quantity'])
                produto = (
                    Produto.objects.select_for_update()
                    .select_related('vendedor')
                    .filter(id=pid, vendedor_id=store_id, ativo=True)
                    .first()
                )
                if not produto or produto.estoque <= 0:
                    return api_response(
                        message='Um ou mais produtos não estão disponíveis.',
                        success=False,
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )
                if produto.estoque < qty:
                    return api_response(
                        message=f'Estoque insuficiente para "{produto.nome}".',
                        success=False,
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )
                locked_products[pid] = produto
                subtotal += (produto.preco * qty)

            subtotal = subtotal.quantize(Decimal('0.01'))
            total = (subtotal + shipping_value).quantize(Decimal('0.01'))

            pedido = Pedido.objects.create(
                comprador=request.user,
                loja=loja,
                shipping_address=shipping_address,
                shipping_provider=shipping_quote['provider'],
                shipping_value=shipping_value,
                subtotal=subtotal,
                total=total,
                status=Pedido.Status.AGUARDANDO_PAGAMENTO,
            )

            for it in items:
                produto = locked_products[it['product_id']]
                qty = int(it['quantity'])
                unit_price = produto.preco
                total_price = (unit_price * qty).quantize(Decimal('0.01'))

                PedidoItem.objects.create(
                    pedido=pedido,
                    produto=produto,
                    quantity=qty,
                    unit_price=unit_price,
                    total_price=total_price,
                )

                produto.estoque = max(0, produto.estoque - qty)
                produto.save(update_fields=['estoque'])

        return api_response(
            data={'order': PedidoSerializer(pedido, context={'request': request}).data},
            message='Pedido criado com sucesso.',
            status_code=status.HTTP_201_CREATED,
        )


class ShippingQuoteView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        store_id = request.data.get('store_id')
        destination_postal_code = request.data.get('destination_postal_code') or request.data.get('cep')
        destination_address = request.data.get('destination_address') or request.data.get('address') or ''
        items = request.data.get('items') or []

        loja = Vendedor.objects.filter(id=store_id, user__is_active=True).first()
        if not loja:
            return api_response(
                message='Loja não encontrada para calcular o frete.',
                success=False,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        clean_cep = ''.join(ch for ch in str(destination_postal_code or '') if ch.isdigit())
        if not clean_cep:
            clean_cep = ''.join(ch for ch in str(destination_address or '') if ch.isdigit())

        total_qty = 0
        for item in items:
            try:
                total_qty += int(item.get('quantity', 1))
            except (TypeError, ValueError, AttributeError):
                total_qty += 1

        quote = calculate_shipping_quote(loja, clean_cep, total_qty or 1, destination_address)
        return api_response(
            data={
                **quote,
                'value': str(quote['value']),
            },
            message='Frete calculado com sucesso.',
        )


class BuyerOrderListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.tipo != User.UserType.COMPRADOR and not request.user.is_staff:
            return api_response(
                message='Apenas compradores ou administradores podem acessar pedidos.',
                success=False,
                status_code=status.HTTP_403_FORBIDDEN,
            )

        pedidos = (
            Pedido.objects.all() if request.user.is_staff else Pedido.objects.filter(comprador=request.user)
        )
        pedidos = (
            pedidos
            .select_related('comprador', 'loja')
            .prefetch_related('itens', 'itens__produto', 'itens__produto__vendedor', 'itens__produto__categoria', 'itens__produto__fotos')
        )
        return api_response(
            data={'orders': PedidoSerializer(pedidos, many=True, context={'request': request}).data},
            message='Pedidos do comprador carregados com sucesso.',
        )


class OrderPaymentProofView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, order_id):
        serializer = PaymentProofUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pedidos = Pedido.objects.filter(id=order_id)
        if not request.user.is_staff:
            pedidos = pedidos.filter(comprador=request.user)
        pedido = (
            pedidos
            .select_related('comprador', 'loja')
            .prefetch_related('itens', 'itens__produto', 'itens__produto__vendedor', 'itens__produto__categoria', 'itens__produto__fotos')
            .first()
        )
        if not pedido:
            return api_response(
                message='Pedido não encontrado.',
                success=False,
                status_code=status.HTTP_404_NOT_FOUND,
            )
        if pedido.status not in {Pedido.Status.AGUARDANDO_PAGAMENTO, Pedido.Status.CRIADO, Pedido.Status.REJEITADO}:
            return api_response(
                message='Este pedido não aceita novo comprovante neste status.',
                success=False,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        pedido.comprovante_pagamento = serializer.validated_data['comprovante']
        pedido.payment_submitted_at = timezone.now()
        pedido.status = Pedido.Status.AGUARDANDO_APROVACAO
        pedido.rejection_reason = ''
        pedido.save(update_fields=['comprovante_pagamento', 'payment_submitted_at', 'status', 'rejection_reason', 'updated_at'])
        try:
            pedido.comprovante_url = request.build_absolute_uri(pedido.comprovante_pagamento.url)
            pedido.save(update_fields=['comprovante_url', 'updated_at'])
        except Exception:
            pass

        return api_response(
            data={'order': PedidoSerializer(pedido, context={'request': request}).data},
            message='Comprovante enviado. O pedido está aguardando aprovação do vendedor.',
        )


class SellerOrderListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not ensure_vendor(request.user):
            return api_response(
                message='Apenas vendedores podem acessar pedidos da loja.',
                success=False,
                status_code=status.HTTP_403_FORBIDDEN,
            )

        status_filter = (request.query_params.get('status') or '').strip()
        pedidos = (
            Pedido.objects.all() if request.user.is_staff else Pedido.objects.filter(loja=get_or_create_vendedor_for_user(request.user))
        )
        pedidos = (
            pedidos
            .select_related('comprador', 'loja')
            .prefetch_related('itens', 'itens__produto', 'itens__produto__vendedor', 'itens__produto__categoria', 'itens__produto__fotos')
        )
        if status_filter:
            pedidos = pedidos.filter(status=status_filter)
        return api_response(
            data={'orders': PedidoSerializer(pedidos, many=True, context={'request': request}).data},
            message='Pedidos da loja carregados com sucesso.',
        )


class SellerPendingOrderListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not ensure_vendor(request.user):
            return api_response(
                message='Apenas vendedores podem acessar pedidos pendentes.',
                success=False,
                status_code=status.HTTP_403_FORBIDDEN,
            )

        pedidos = (
            Pedido.objects.filter(status=Pedido.Status.AGUARDANDO_APROVACAO) if request.user.is_staff else Pedido.objects.filter(loja=get_or_create_vendedor_for_user(request.user), status=Pedido.Status.AGUARDANDO_APROVACAO)
        )
        pedidos = (
            pedidos
            .select_related('comprador', 'loja')
            .prefetch_related('itens', 'itens__produto', 'itens__produto__vendedor', 'itens__produto__categoria', 'itens__produto__fotos')
        )
        return api_response(
            data={'orders': PedidoSerializer(pedidos, many=True, context={'request': request}).data},
            message='Pedidos pendentes carregados com sucesso.',
        )


class SellerOrderApproveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, order_id):
        if not ensure_vendor(request.user):
            return api_response(message='Apenas vendedores podem aprovar pedidos.', success=False, status_code=status.HTTP_403_FORBIDDEN)

        pedidos = Pedido.objects.filter(id=order_id)
        if not request.user.is_staff:
            pedidos = pedidos.filter(loja=get_or_create_vendedor_for_user(request.user))
        pedido = pedidos.select_related('comprador', 'loja').first()
        if not pedido:
            return api_response(message='Pedido não encontrado.', success=False, status_code=status.HTTP_404_NOT_FOUND)
        if pedido.status != Pedido.Status.AGUARDANDO_APROVACAO:
            return api_response(message='Apenas pedidos aguardando aprovação podem ser aprovados.', success=False, status_code=status.HTTP_400_BAD_REQUEST)

        pedido.status = Pedido.Status.PAGO
        pedido.data_aprovacao = timezone.now()
        pedido.rejection_reason = ''
        pedido.save(update_fields=['status', 'data_aprovacao', 'rejection_reason', 'updated_at'])
        notify_order_approved(pedido)
        return api_response(data={'order': PedidoSerializer(pedido, context={'request': request}).data}, message='Pagamento aprovado com sucesso.')


class SellerOrderRejectView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, order_id):
        if not ensure_vendor(request.user):
            return api_response(message='Apenas vendedores podem rejeitar pedidos.', success=False, status_code=status.HTTP_403_FORBIDDEN)

        serializer = OrderRejectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pedidos = Pedido.objects.filter(id=order_id)
        if not request.user.is_staff:
            pedidos = pedidos.filter(loja=get_or_create_vendedor_for_user(request.user))
        pedido = pedidos.select_related('comprador', 'loja').first()
        if not pedido:
            return api_response(message='Pedido não encontrado.', success=False, status_code=status.HTTP_404_NOT_FOUND)
        if pedido.status != Pedido.Status.AGUARDANDO_APROVACAO:
            return api_response(message='Apenas pedidos aguardando aprovação podem ser rejeitados.', success=False, status_code=status.HTTP_400_BAD_REQUEST)

        pedido.status = Pedido.Status.REJEITADO
        pedido.rejection_reason = serializer.validated_data['motivo']
        pedido.save(update_fields=['status', 'rejection_reason', 'updated_at'])
        notify_order_rejected(pedido)
        return api_response(data={'order': PedidoSerializer(pedido, context={'request': request}).data}, message='Pagamento rejeitado com sucesso.')


class SellerOrderShipView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, order_id):
        if not ensure_vendor(request.user):
            return api_response(message='Apenas vendedores podem enviar pedidos.', success=False, status_code=status.HTTP_403_FORBIDDEN)

        serializer = OrderShipSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pedidos = Pedido.objects.filter(id=order_id)
        if not request.user.is_staff:
            pedidos = pedidos.filter(loja=get_or_create_vendedor_for_user(request.user))
        pedido = pedidos.select_related('comprador', 'loja').first()
        if not pedido:
            return api_response(message='Pedido não encontrado.', success=False, status_code=status.HTTP_404_NOT_FOUND)
        if pedido.status != Pedido.Status.PAGO:
            return api_response(message='Apenas pedidos pagos podem ser enviados.', success=False, status_code=status.HTTP_400_BAD_REQUEST)

        pedido.status = Pedido.Status.ENVIADO
        pedido.tracking_code = serializer.validated_data['tracking_code']
        pedido.shipped_at = timezone.now()
        pedido.save(update_fields=['status', 'tracking_code', 'shipped_at', 'updated_at'])
        notify_order_shipped(pedido)
        return api_response(data={'order': PedidoSerializer(pedido, context={'request': request}).data}, message='Pedido marcado como enviado.')


class SellerOrderDeliverView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, order_id):
        if not ensure_vendor(request.user):
            return api_response(message='Apenas vendedores podem marcar pedidos como entregues.', success=False, status_code=status.HTTP_403_FORBIDDEN)

        pedidos = Pedido.objects.filter(id=order_id)
        if not request.user.is_staff:
            pedidos = pedidos.filter(loja=get_or_create_vendedor_for_user(request.user))
        pedido = pedidos.select_related('comprador', 'loja').first()
        if not pedido:
            return api_response(message='Pedido não encontrado.', success=False, status_code=status.HTTP_404_NOT_FOUND)
        if pedido.status != Pedido.Status.ENVIADO:
            return api_response(message='Apenas pedidos enviados podem ser marcados como entregues.', success=False, status_code=status.HTTP_400_BAD_REQUEST)

        pedido.status = Pedido.Status.ENTREGUE
        pedido.save(update_fields=['status', 'updated_at'])
        return api_response(data={'order': PedidoSerializer(pedido, context={'request': request}).data}, message='Pedido marcado como entregue.')


class SellerOrderLabelView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, order_id):
        if not ensure_vendor(request.user):
            return api_response(message='Apenas vendedores podem gerar etiquetas.', success=False, status_code=status.HTTP_403_FORBIDDEN)

        pedido = (
            Pedido.objects.filter(id=order_id)
            if request.user.is_staff else Pedido.objects.filter(id=order_id, loja=get_or_create_vendedor_for_user(request.user))
        )
        pedido = (
            pedido
            .select_related('comprador', 'loja', 'comprador__comprador')
            .prefetch_related('itens', 'itens__produto')
            .first()
        )
        if not pedido:
            return api_response(message='Pedido não encontrado.', success=False, status_code=status.HTTP_404_NOT_FOUND)

        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A6)
        pdf.setTitle(f'Etiqueta Pedido {pedido.id}')
        pdf.setFont('Helvetica-Bold', 12)
        pdf.drawString(20, 390, f'Etiqueta Pedido #{pedido.id}')
        pdf.setFont('Helvetica', 9)
        pdf.drawString(20, 372, f'Loja: {pedido.loja.nome_loja}')
        pdf.drawString(20, 358, f'Origem: {pedido.loja.endereco_completo}')
        pdf.drawString(20, 344, f'Destino: {pedido.shipping_address}')
        pdf.drawString(20, 330, f'Comprador: {pedido.comprador.nome}')
        pdf.drawString(20, 316, f'PIX: {pedido.loja.chave_pix}')
        pdf.drawString(20, 302, f'Rastreio: {pedido.tracking_code or "pendente"}')

        y = 280
        pdf.setFont('Helvetica-Bold', 9)
        pdf.drawString(20, y, 'Itens:')
        pdf.setFont('Helvetica', 8)
        for item in pedido.itens.select_related('produto').all():
            y -= 14
            pdf.drawString(24, y, f'{item.quantity}x {item.produto.nome}')

        pdf.showPage()
        pdf.save()

        buffer.seek(0)
        response = HttpResponse(buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="etiqueta-pedido-{pedido.id}.pdf"'
        return response


def home_page(request):
    lojas = (
        Vendedor.objects.filter(user__is_active=True)
        .annotate(total_produtos_publicos=Count('produtos', filter=Q(produtos__ativo=True, produtos__estoque__gt=0)))
        .filter(total_produtos_publicos__gt=0)
        .order_by('-total_produtos_publicos', 'nome_loja')
    )

    showcase = []
    for loja in lojas:
        produtos = (
            loja.produtos.filter(ativo=True, estoque__gt=0)
            .select_related('categoria')
            .prefetch_related('fotos', 'variacoes')
            .order_by('-destaque', '-data_cadastro', 'id')[:10]
        )
        if produtos:
            showcase.append({'loja': loja, 'produtos': produtos})

    context = {'showcase': showcase}
    return render(request, 'pages/home.html', context)


def search_page(request):
    q = (request.GET.get('q') or '').strip()
    sort = (request.GET.get('sort') or 'relevance').strip()
    min_price = (request.GET.get('min_price') or '').strip()
    max_price = (request.GET.get('max_price') or '').strip()
    category_values = request.GET.getlist('categories') or (request.GET.get('categories') or '').split(',')
    store_values = request.GET.getlist('stores') or (request.GET.get('stores') or '').split(',')
    category_ids = [int(x) for x in category_values if str(x).strip().isdigit()]
    store_ids = [int(x) for x in store_values if str(x).strip().isdigit()]

    qs = Produto.objects.filter(ativo=True, estoque__gt=0, vendedor__user__is_active=True).select_related('vendedor', 'categoria').prefetch_related('fotos')
    if q:
        qs = qs.filter(
            Q(nome__icontains=q)
            | Q(descricao__icontains=q)
            | Q(vendedor__nome_loja__icontains=q)
            | Q(categoria__nome__icontains=q)
        )
    if category_ids:
        qs = qs.filter(categoria_id__in=category_ids)
    if store_ids:
        qs = qs.filter(vendedor_id__in=store_ids)
    if min_price:
        try:
            qs = qs.filter(preco__gte=min_price)
        except Exception:
            pass
    if max_price:
        try:
            qs = qs.filter(preco__lte=max_price)
        except Exception:
            pass

    if sort == 'price_asc':
        qs = qs.order_by('preco', '-destaque', '-data_cadastro', 'id')
    elif sort == 'price_desc':
        qs = qs.order_by('-preco', '-destaque', '-data_cadastro', 'id')
    else:
        qs = qs.order_by('-destaque', '-data_cadastro', 'id')

    facet_qs = Produto.objects.filter(ativo=True, estoque__gt=0, vendedor__user__is_active=True)
    if q:
        facet_qs = facet_qs.filter(
            Q(nome__icontains=q)
            | Q(descricao__icontains=q)
            | Q(vendedor__nome_loja__icontains=q)
            | Q(categoria__nome__icontains=q)
        )

    categories = (
        facet_qs.exclude(categoria_id=None)
        .values('categoria_id', 'categoria__nome')
        .annotate(total=Count('id'))
        .order_by('-total', 'categoria__nome')
    )
    stores = (
        facet_qs.values('vendedor_id', 'vendedor__nome_loja')
        .annotate(total=Count('id'))
        .order_by('-total', 'vendedor__nome_loja')
    )

    return render(
        request,
        'pages/search.html',
        {
            'search_results': qs[:24],
            'search_categories': categories,
            'search_stores': stores,
            'search_query': q,
            'search_sort': sort,
            'search_min': min_price,
            'search_max': max_price,
            'search_categories_selected': category_ids,
            'search_stores_selected': store_ids,
        },
    )


def store_page(request, slug='loja-modelo'):
    context = {
        'store': {
            'nome_loja': 'Loja modelo',
            'descricao_loja': 'Página de rascunho (não vinculada ao banco).',
            'logo_url': '',
            'slug': slug,
        },
        'products': [],
        'categories': [],
    }
    return render(request, 'pages/store.html', context)


def product_page(request, slug='produto-modelo'):
    context = {
        'product': {
            'nome': 'Produto modelo',
            'descricao': 'Página de rascunho (não vinculada ao banco).',
            'preco': '0.00',
            'estoque': 0,
            'slug': slug,
        },
        'store': {'id': 0, 'nome_loja': 'Loja modelo', 'logo_url': ''},
        'photos': [],
        'variations': [],
        'reviews': [],
    }
    return render(request, 'pages/product.html', context)


def public_store_page(request, store_id):
    loja = Vendedor.objects.filter(id=store_id, user__is_active=True).first()
    if not loja:
        return render(request, 'pages/404.html', status=404)

    phone_digits = ''.join(ch for ch in loja.user.telefone if ch.isdigit())

    produtos = (
        loja.produtos.filter(ativo=True, estoque__gt=0)
        .select_related('categoria')
        .prefetch_related('fotos', 'variacoes')
        .order_by('-destaque', '-data_cadastro', 'id')
    )
    categorias = loja.categorias.filter(ativo=True).select_related('parent').order_by('nome', 'id')

    return render(
        request,
        'pages/store.html',
        {
            'store': loja,
            'products': produtos,
            'categories': categorias,
            'contact_email': loja.user.email,
            'contact_phone': loja.user.telefone,
            'store_url': request.build_absolute_uri(f'/api/front/loja/{loja.id}/'),
            'whatsapp_link': f'https://wa.me/{phone_digits}' if phone_digits else '',
        },
    )


def public_product_page(request, product_id):
    produto = (
        Produto.objects.filter(id=product_id, ativo=True, estoque__gt=0)
        .select_related('categoria', 'vendedor')
        .prefetch_related('fotos', 'variacoes')
        .first()
    )
    if not produto:
        return render(request, 'pages/404.html', status=404)

    return render(
        request,
        'pages/product.html',
        {
            'product': produto,
            'store': produto.vendedor,
            'photos': list(produto.fotos.all()),
            'variations': list(produto.variacoes.all()),
            'reviews': list(produto.avaliacoes.select_related('comprador').order_by('-data_avaliacao', '-id')[:8]),
        },
    )


def seller_dashboard_page(request):
    return render(request, 'pages/seller_dashboard.html')


def buyer_dashboard_page(request):
    return render(request, 'pages/buyer_dashboard.html')


def cart_page(request):
    return render(request, 'pages/cart.html')


def pix_payment_page(request):
    return render(request, 'pages/pix_payment.html')


def seller_orders_page(request):
    return render(request, 'pages/seller_orders.html')


def categories_page(request):
    categoria_nome = (request.GET.get('categoria') or '').strip()
    loja_id = (request.GET.get('loja') or '').strip()
    q = (request.GET.get('q') or '').strip()

    produtos_base = (
        Produto.objects.filter(ativo=True, estoque__gt=0, vendedor__user__is_active=True)
        .select_related('vendedor', 'categoria')
        .prefetch_related('fotos', 'variacoes')
    )

    category_filters = (
        produtos_base.exclude(categoria_id=None)
        .values('categoria__nome')
        .annotate(total=Count('id'))
        .order_by('categoria__nome')
    )
    store_filters = (
        produtos_base.values('vendedor_id', 'vendedor__nome_loja')
        .annotate(total=Count('id'))
        .order_by('vendedor__nome_loja')
    )

    if categoria_nome:
        produtos_base = produtos_base.filter(categoria__nome=categoria_nome)
    if loja_id.isdigit():
        produtos_base = produtos_base.filter(vendedor_id=int(loja_id))
    if q:
        produtos_base = produtos_base.filter(
            Q(nome__icontains=q)
            | Q(descricao__icontains=q)
            | Q(vendedor__nome_loja__icontains=q)
            | Q(categoria__nome__icontains=q)
        )

    nomes_categorias = (
        produtos_base.exclude(categoria_id=None)
        .values_list('categoria__nome', flat=True)
        .distinct()
        .order_by('categoria__nome')
    )

    categorias = []
    for nome_categoria in nomes_categorias:
        produtos = (
            produtos_base.filter(categoria__nome=nome_categoria)
            .select_related('vendedor', 'categoria')
            .prefetch_related('fotos', 'variacoes')
            .order_by('-destaque', '-data_cadastro', 'id')[:12]
        )
        categorias.append({
            'nome': nome_categoria,
            'descricao': produtos[0].categoria.descricao if produtos and produtos[0].categoria else '',
            'produtos': produtos,
            'total': produtos_base.filter(categoria__nome=nome_categoria).count(),
        })

    return render(
        request,
        'pages/categories.html',
        {
            'categorias': categorias,
            'category_filters': category_filters,
            'store_filters': store_filters,
            'selected_categoria': categoria_nome,
            'selected_loja': int(loja_id) if loja_id.isdigit() else None,
            'search_query': q,
        },
    )


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


def admin_dashboard_page(request):
    return render(request, 'pages/admin_dashboard.html')
