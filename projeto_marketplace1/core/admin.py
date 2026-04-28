from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Categoria, Comprador, FotoProduto, Produto, User, VariacaoProduto, Vendedor


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ['email']
    list_display = ['email', 'nome', 'tipo', 'is_active', 'is_staff']
    search_fields = ['email', 'nome']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações pessoais', {'fields': ('nome', 'telefone', 'tipo')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nome', 'telefone', 'tipo', 'password1', 'password2', 'is_staff', 'is_superuser'),
        }),
    )
    filter_horizontal = ('groups', 'user_permissions')


@admin.register(Vendedor)
class VendedorAdmin(admin.ModelAdmin):
    list_display = ['nome_loja', 'user', 'chave_pix']
    search_fields = ['nome_loja', 'user__email']


@admin.register(Comprador)
class CompradorAdmin(admin.ModelAdmin):
    list_display = ['user', 'cpf']
    search_fields = ['user__email', 'cpf']


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'vendedor', 'categoria', 'preco', 'estoque', 'destaque', 'ativo', 'data_cadastro']
    list_filter = ['ativo', 'destaque', 'categoria', 'data_cadastro']
    search_fields = ['nome', 'categoria__nome', 'vendedor__nome_loja', 'vendedor__user__email']


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'vendedor', 'parent', 'ativo', 'data_cadastro']
    list_filter = ['ativo', 'data_cadastro']
    search_fields = ['nome', 'vendedor__nome_loja', 'vendedor__user__email']


@admin.register(VariacaoProduto)
class VariacaoProdutoAdmin(admin.ModelAdmin):
    list_display = ['produto', 'tipo', 'valor', 'data_cadastro']
    list_filter = ['tipo', 'data_cadastro']
    search_fields = ['produto__nome', 'produto__vendedor__nome_loja', 'tipo', 'valor']


@admin.register(FotoProduto)
class FotoProdutoAdmin(admin.ModelAdmin):
    list_display = ['produto', 'ordem', 'imagem']
    search_fields = ['produto__nome', 'produto__vendedor__nome_loja']
