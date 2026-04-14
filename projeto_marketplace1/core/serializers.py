from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Comprador, User, Vendedor


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
