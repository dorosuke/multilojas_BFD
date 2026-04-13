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

        return self.create_user(email, password, **extra_fields)


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
