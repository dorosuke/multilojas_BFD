from django.db import models, transaction
from django.db.models import Count, Q
from django.shortcuts import render
from rest_framework import permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.views import APIView
from decimal import Decimal

from .models import Categoria, FotoProduto, Pedido, PedidoItem, Produto, User, VariacaoProduto, Vendedor, get_or_create_vendedor_for_user
from .serializers import (
    CategoriaCreateUpdateSerializer,
    CategoriaSerializer,
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
                'version': 'sprint-6',
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

        return api_response(
            data={
                'produto': ProdutoSerializer(produto, context={'request': request}).data,
                'loja': {
                    'id': produto.vendedor_id,
                    'nome_loja': produto.vendedor.nome_loja,
                    'logo_url': produto.vendedor.logo_url,
                },
            },
            message='Produto carregado com sucesso.',
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


class OrderCreateView(APIView):
    """
    Sprint 8: criação de pedido (carrinho por loja + frete + endereço).
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if request.user.tipo != User.UserType.COMPRADOR:
            return api_response(
                message='Apenas compradores podem finalizar pedidos.',
                success=False,
                status_code=status.HTTP_403_FORBIDDEN,
            )

        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        store_id = serializer.validated_data['store_id']
        shipping_address = serializer.validated_data['shipping_address']
        items = serializer.validated_data['items']

        loja = Vendedor.objects.filter(id=store_id, user__is_active=True).first()
        if not loja:
            return api_response(
                message='Loja não encontrada.',
                success=False,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Frete (stub): base + por item. Integração Correios pode ser plugada aqui depois.
        total_qty = sum(int(it['quantity']) for it in items)
        shipping_value = (Decimal('10.00') + Decimal('2.00') * Decimal(total_qty)).quantize(Decimal('0.01'))

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
                shipping_provider='correios_stub',
                shipping_value=shipping_value,
                subtotal=subtotal,
                total=total,
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

        recent_products = (
            Produto.objects.select_related('vendedor', 'categoria')
            .order_by('-data_cadastro')[:8]
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
                    'products_out_of_stock': out_of_stock,
                    'products_low_stock': low_stock,
                },
                'low_stock': [
                    {
                        'id': p.id,
                        'nome': p.nome,
                        'estoque': p.estoque,
                        'loja': {'id': p.vendedor_id, 'nome_loja': p.vendedor.nome_loja},
                    }
                    for p in low_stock_items
                ],
                'recent_products': [
                    {
                        'id': p.id,
                        'nome': p.nome,
                        'preco': str(p.preco),
                        'estoque': p.estoque,
                        'ativo': p.ativo,
                        'loja': {'id': p.vendedor_id, 'nome_loja': p.vendedor.nome_loja},
                        'categoria': {'id': p.categoria_id, 'nome': p.categoria.nome} if p.categoria_id else None,
                    }
                    for p in recent_products
                ],
                'notes': [
                    'Até a Sprint 6 não existe checkout/pedido; portanto o estoque não é decrementado automaticamente por compras.',
                    'Quando o módulo de pedidos (Sprint 8+) for implementado, a regra esperada é decrementar o estoque ao criar o pedido.',
                ],
            },
            message='Dashboard administrativo carregado com sucesso.',
        )


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
        },
    )


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


def admin_dashboard_page(request):
    return render(request, 'pages/admin_dashboard.html')
