from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Categoria, Comprador, FotoProduto, Produto, User, VariacaoProduto, Vendedor


class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'nome', 'email', 'telefone', 'tipo', 'data_cadastro', 'is_active']


class VendedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendedor
        fields = [
            'nome_loja',
            'descricao_loja',
            'logo_url',
            'endereco_completo',
            'cnpj',
            'chave_pix',
        ]


class CompradorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comprador
        fields = ['cpf', 'endereco_completo']


class FotoProdutoSerializer(serializers.ModelSerializer):
    imagem_url = serializers.SerializerMethodField()

    class Meta:
        model = FotoProduto
        fields = ['id', 'ordem', 'imagem_url']

    def get_imagem_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.imagem.url)
        return obj.imagem.url


class ProdutoSerializer(serializers.ModelSerializer):
    fotos = FotoProdutoSerializer(many=True, read_only=True)
    total_fotos = serializers.IntegerField(source='fotos.count', read_only=True)
    status_estoque = serializers.SerializerMethodField()
    categoria = serializers.SerializerMethodField()
    variacoes = serializers.SerializerMethodField()

    class Meta:
        model = Produto
        fields = [
            'id',
            'categoria',
            'nome',
            'descricao',
            'preco',
            'estoque',
            'destaque',
            'ativo',
            'data_cadastro',
            'status_estoque',
            'total_fotos',
            'variacoes',
            'fotos',
        ]

    def get_status_estoque(self, obj):
        if obj.estoque == 0:
            return 'indisponivel'
        if obj.estoque < 5:
            return 'baixo'
        return 'ok'

    def get_categoria(self, obj):
        if not obj.categoria_id:
            return None
        return {
            'id': obj.categoria_id,
            'nome': obj.categoria.nome,
            'parent_id': obj.categoria.parent_id,
            'ativo': obj.categoria.ativo,
        }

    def get_variacoes(self, obj):
        return [
            {'id': v.id, 'tipo': v.tipo, 'valor': v.valor}
            for v in obj.variacoes.all()
        ]


class ProdutoCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = ['nome', 'descricao', 'preco', 'estoque', 'destaque', 'ativo', 'categoria']

    def validate_estoque(self, value):
        if value < 0:
            raise serializers.ValidationError('O estoque não pode ser negativo.')
        return value

    def validate_categoria(self, value):
        if not value:
            return value

        request = self.context.get('request')
        if not request or not request.user.is_authenticated or not hasattr(request.user, 'vendedor'):
            raise serializers.ValidationError('Categoria inválida.')

        if value.vendedor_id != request.user.vendedor.id:
            raise serializers.ValidationError('Categoria deve pertencer à sua loja.')
        return value


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nome', 'descricao', 'ativo', 'parent', 'data_cadastro']


class CategoriaCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['nome', 'descricao', 'ativo', 'parent']

    def validate_parent(self, value):
        if not value:
            return value
        request = self.context.get('request')
        if not request or not request.user.is_authenticated or not hasattr(request.user, 'vendedor'):
            raise serializers.ValidationError('Categoria pai inválida.')
        if value.vendedor_id != request.user.vendedor.id:
            raise serializers.ValidationError('Categoria pai deve pertencer à sua loja.')
        return value


class VariacaoProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariacaoProduto
        fields = ['id', 'tipo', 'valor', 'data_cadastro']


class VariacaoProdutoCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariacaoProduto
        fields = ['tipo', 'valor']

    def validate_tipo(self, value):
        value = (value or '').strip()
        if not value:
            raise serializers.ValidationError('Informe o tipo da variação.')
        return value

    def validate_valor(self, value):
        value = (value or '').strip()
        if not value:
            raise serializers.ValidationError('Informe o valor da variação.')
        return value


class FotoProdutoUploadSerializer(serializers.Serializer):
    fotos = serializers.ListField(
        child=serializers.ImageField(),
        allow_empty=False,
        write_only=True,
    )

    def validate_fotos(self, value):
        if len(value) > 5:
            raise serializers.ValidationError('Envie no máximo 5 imagens por vez.')

        for image in value:
            if image.size > 1024 * 1024:
                raise serializers.ValidationError(
                    f'A imagem "{image.name}" excede o limite de 1MB.'
                )
        return value


class SellerStoreSerializer(serializers.Serializer):
    user = UserSummarySerializer(read_only=True)
    vendedor = VendedorSerializer(read_only=True)
    stats = serializers.DictField(read_only=True)

    def to_representation(self, instance):
        vendedor = instance.vendedor
        produtos = vendedor.produtos.all()
        return {
            'user': UserSummarySerializer(instance).data,
            'vendedor': VendedorSerializer(vendedor).data,
            'stats': {
                'total_produtos': produtos.count(),
                'produtos_ativos': produtos.filter(ativo=True).count(),
                'produtos_destaque': produtos.filter(destaque=True, ativo=True).count(),
                'produtos_sem_estoque': produtos.filter(estoque=0, ativo=True).count(),
            },
        }


class RegistroVendedorSerializer(serializers.Serializer):
    nome = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    senha = serializers.CharField(write_only=True, min_length=8)
    telefone = serializers.CharField(max_length=20)
    nome_loja = serializers.CharField(max_length=255)
    descricao_loja = serializers.CharField(required=False, allow_blank=True)
    logo_url = serializers.URLField(required=False, allow_blank=True)
    endereco_completo = serializers.CharField()
    cnpj = serializers.CharField(required=False, allow_blank=True)
    chave_pix = serializers.CharField(max_length=255)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Já existe usuário com este e-mail.')
        return value

    def create(self, validated_data):
        vendedor_data = {
            'nome_loja': validated_data.pop('nome_loja'),
            'descricao_loja': validated_data.pop('descricao_loja', ''),
            'logo_url': validated_data.pop('logo_url', ''),
            'endereco_completo': validated_data.pop('endereco_completo'),
            'cnpj': validated_data.pop('cnpj', ''),
            'chave_pix': validated_data.pop('chave_pix'),
        }
        senha = validated_data.pop('senha')
        user = User.objects.create_user(
            password=senha,
            tipo=User.UserType.VENDEDOR,
            **validated_data,
        )
        Vendedor.objects.create(user=user, **vendedor_data)
        return user


class RegistroCompradorSerializer(serializers.Serializer):
    nome = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    senha = serializers.CharField(write_only=True, min_length=8)
    telefone = serializers.CharField(max_length=20)
    cpf = serializers.CharField(max_length=14)
    endereco_completo = serializers.CharField()

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Já existe usuário com este e-mail.')
        return value

    def create(self, validated_data):
        comprador_data = {
            'cpf': validated_data.pop('cpf'),
            'endereco_completo': validated_data.pop('endereco_completo'),
        }
        senha = validated_data.pop('senha')
        user = User.objects.create_user(
            password=senha,
            tipo=User.UserType.COMPRADOR,
            **validated_data,
        )
        Comprador.objects.create(user=user, **comprador_data)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    senha = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get('request'),
            username=attrs['email'],
            password=attrs['senha'],
        )
        if not user:
            raise serializers.ValidationError('Credenciais inválidas.')
        if not user.is_active:
            raise serializers.ValidationError('Usuário inativo.')
        attrs['user'] = user
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def save(self):
        email = self.validated_data['email']
        user = User.objects.filter(email=email).first()
        if not user:
            return None

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        return {
            'uid': uid,
            'token': token,
            'reset_link': f'/api/front/recuperar-senha/?uid={uid}&token={token}',
        }


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    nova_senha = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        try:
            user_id = force_str(urlsafe_base64_decode(attrs['uid']))
            user = User.objects.get(pk=user_id)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            raise serializers.ValidationError('Link de redefinição inválido.')

        if not default_token_generator.check_token(user, attrs['token']):
            raise serializers.ValidationError('Token inválido ou expirado.')

        attrs['user'] = user
        return attrs

    def save(self):
        user = self.validated_data['user']
        user.set_password(self.validated_data['nova_senha'])
        user.save(update_fields=['password'])
        return user


class ProfileSerializer(serializers.Serializer):
    user = UserSummarySerializer(read_only=True)
    vendedor = VendedorSerializer(read_only=True)
    comprador = CompradorSerializer(read_only=True)

    def to_representation(self, instance):
        data = {
            'user': UserSummarySerializer(instance).data,
            'vendedor': None,
            'comprador': None,
        }
        if hasattr(instance, 'vendedor'):
            data['vendedor'] = VendedorSerializer(instance.vendedor).data
        if hasattr(instance, 'comprador'):
            data['comprador'] = CompradorSerializer(instance.comprador).data
        return data


class ProfileUpdateSerializer(serializers.Serializer):
    nome = serializers.CharField(max_length=255, required=False)
    telefone = serializers.CharField(max_length=20, required=False)

    nome_loja = serializers.CharField(max_length=255, required=False)
    descricao_loja = serializers.CharField(required=False, allow_blank=True)
    logo_url = serializers.URLField(required=False, allow_blank=True)
    endereco_completo = serializers.CharField(required=False)
    cnpj = serializers.CharField(required=False, allow_blank=True)
    chave_pix = serializers.CharField(max_length=255, required=False)

    cpf = serializers.CharField(max_length=14, required=False)

    def update(self, instance, validated_data):
        user_fields = ['nome', 'telefone']
        for field in user_fields:
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        instance.save()

        if instance.tipo == User.UserType.VENDEDOR and hasattr(instance, 'vendedor'):
            vendedor = instance.vendedor
            for field in ['nome_loja', 'descricao_loja', 'logo_url', 'endereco_completo', 'cnpj', 'chave_pix']:
                if field in validated_data:
                    setattr(vendedor, field, validated_data[field])
            vendedor.save()

        if instance.tipo == User.UserType.COMPRADOR and hasattr(instance, 'comprador'):
            comprador = instance.comprador
            for field in ['cpf', 'endereco_completo']:
                if field in validated_data:
                    setattr(comprador, field, validated_data[field])
            comprador.save()

        return instance

    def create(self, validated_data):
        raise NotImplementedError


def build_auth_payload(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': ProfileSerializer(user).data,
    }
