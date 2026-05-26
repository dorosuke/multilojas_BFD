from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O e-mail é obrigatório.')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('tipo', User.UserType.VENDEDOR)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superusuário deve ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superusuário deve ter is_superuser=True.')

        user = self.create_user(email, password, **extra_fields)

        try:
            user.vendedor
        except Exception:
            Vendedor.objects.create(
                user=user,
                nome_loja=f'Admin - {user.nome}',
                descricao_loja='Perfil de vendedor administrativo (ajuste os dados depois).',
                logo_url='',
                endereco_completo='(Defina o endereço completo no perfil do vendedor)',
                cnpj='',
                chave_pix=user.email,
            )

        return user


class User(AbstractBaseUser, PermissionsMixin):
    class UserType(models.TextChoices):
        VENDEDOR = 'vendedor', 'Vendedor'
        COMPRADOR = 'comprador', 'Comprador'

    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20)
    tipo = models.CharField(max_length=20, choices=UserType.choices)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome', 'telefone', 'tipo']

    def __str__(self):
        return f'{self.nome} <{self.email}>'


class Vendedor(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='vendedor',
    )
    nome_loja = models.CharField(max_length=255)
    descricao_loja = models.TextField(blank=True)
    logo_url = models.URLField(blank=True)
    endereco_completo = models.TextField()
    cnpj = models.CharField(max_length=18, blank=True)
    chave_pix = models.CharField(max_length=255)

    def __str__(self):
        return self.nome_loja


def get_or_create_vendedor_for_user(user):
    if not user or not getattr(user, 'is_authenticated', False):
        return None

    if hasattr(user, 'vendedor'):
        return user.vendedor

    if user.is_superuser or user.is_staff:
        return Vendedor.objects.create(
            user=user,
            nome_loja=f'Admin - {user.nome}',
            descricao_loja='Perfil de vendedor administrativo (ajuste os dados depois).',
            logo_url='',
            endereco_completo='(Defina o endereço completo no perfil do vendedor)',
            cnpj='',
            chave_pix=user.email,
        )

    return None


class Comprador(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='comprador',
    )
    cpf = models.CharField(max_length=14)
    endereco_completo = models.TextField()

    def __str__(self):
        return self.user.nome


class Produto(models.Model):
    vendedor = models.ForeignKey(
        Vendedor,
        on_delete=models.CASCADE,
        related_name='produtos',
    )
    categoria = models.ForeignKey(
        'Categoria',
        on_delete=models.SET_NULL,
        related_name='produtos',
        null=True,
        blank=True,
    )
    nome = models.CharField(max_length=255)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    estoque = models.PositiveIntegerField(default=0)
    destaque = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-destaque', '-data_cadastro']

    def __str__(self):
        return self.nome


class Categoria(models.Model):
    vendedor = models.ForeignKey(
        Vendedor,
        on_delete=models.CASCADE,
        related_name='categorias',
    )
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subcategorias',
    )
    data_cadastro = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nome', 'id']
        unique_together = [('vendedor', 'nome', 'parent')]

    def __str__(self):
        return self.nome


class VariacaoProduto(models.Model):
    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        related_name='variacoes',
    )
    tipo = models.CharField(max_length=50)
    valor = models.CharField(max_length=100)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['tipo', 'valor', 'id']
        unique_together = [('produto', 'tipo', 'valor')]

    def __str__(self):
        return f'{self.tipo}: {self.valor}'


class FotoProduto(models.Model):
    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        related_name='fotos',
    )
    imagem = models.ImageField(upload_to='produtos/')
    ordem = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['ordem', 'id']

    def __str__(self):
        return f'Foto de {self.produto.nome} ({self.id})'


class Pedido(models.Model):
    class Status(models.TextChoices):
        CRIADO = 'criado', 'Criado'
        CANCELADO = 'cancelado', 'Cancelado'

    comprador = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='pedidos',
    )
    loja = models.ForeignKey(
        Vendedor,
        on_delete=models.CASCADE,
        related_name='pedidos',
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CRIADO)

    shipping_address = models.TextField()
    shipping_provider = models.CharField(max_length=50, default='correios_stub')
    shipping_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at', '-id']

    def __str__(self):
        return f'Pedido #{self.id} ({self.status})'


class PedidoItem(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='itens',
    )
    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        related_name='pedido_itens',
    )
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'Item #{self.id} x{self.quantity}'
