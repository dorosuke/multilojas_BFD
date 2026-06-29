from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction
from PIL import Image, ImageDraw
from io import BytesIO

from core.models import Categoria, Comprador, FotoProduto, Produto, Vendedor


User = get_user_model()


def build_demo_image(text, background):
    image = Image.new('RGB', (1200, 900), background)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((40, 40, 1160, 860), radius=48, outline=(255, 255, 255), width=16)
    draw.rounded_rectangle((120, 120, 1080, 780), radius=36, fill=(255, 255, 255))
    draw.text((180, 250), text, fill=(52, 35, 28))
    draw.text((180, 360), 'MultiLojas', fill=(196, 92, 47))

    buffer = BytesIO()
    image.save(buffer, format='PNG')
    return buffer.getvalue()


class Command(BaseCommand):
    help = 'Cria um conjunto demo de vendedores, categorias, produtos e fotos.'

    def handle(self, *args, **options):
        demo_users = [
            {
                'email': 'comprador@demo.com',
                'nome': 'Cliente Demo',
                'password': 'Comprador@12345',
                'tipo': User.UserType.COMPRADOR,
                'telefone': '(11) 98888-0001',
                'comprador': {
                    'cpf': '123.456.789-10',
                    'endereco_completo': 'Rua das Flores, 123, Centro, São Paulo - SP',
                    'cep': '01001000',
                },
            },
            {
                'email': 'modasolar@demo.com',
                'nome': 'Ana Moda',
                'password': 'Moda@12345',
                'tipo': User.UserType.VENDEDOR,
                'telefone': '(11) 97777-0002',
                'vendedor': {
                    'nome_loja': 'Moda Solar',
                    'descricao_loja': 'Coleções leves, elegantes e prontas para o dia a dia.',
                    'endereco_completo': 'Av. Paulista, 1000, Bela Vista, São Paulo - SP',
                    'cep': '01310000',
                    'cnpj': '12.345.678/0001-90',
                    'chave_pix': 'moda.solar@demo.com',
                    'logo_color': (232, 145, 92),
                },
            },
            {
                'email': 'casaaurora@demo.com',
                'nome': 'Bruno Casa',
                'password': 'Casa@12345',
                'tipo': User.UserType.VENDEDOR,
                'telefone': '(11) 96666-0003',
                'vendedor': {
                    'nome_loja': 'Casa Aurora',
                    'descricao_loja': 'Decoração, utilidades e peças para uma casa mais acolhedora.',
                    'endereco_completo': 'Rua Oscar Freire, 200, Jardins, São Paulo - SP',
                    'cep': '01426000',
                    'cnpj': '23.456.789/0001-01',
                    'chave_pix': 'casa.aurora@demo.com',
                    'logo_color': (139, 182, 198),
                },
            },
            {
                'email': 'sabordavila@demo.com',
                'nome': 'Carla Vila',
                'password': 'Sabor@12345',
                'tipo': User.UserType.VENDEDOR,
                'telefone': '(11) 95555-0004',
                'vendedor': {
                    'nome_loja': 'Sabor da Vila',
                    'descricao_loja': 'Cestas, doces e produtos artesanais para presentear.',
                    'endereco_completo': 'Rua Augusta, 450, Consolação, São Paulo - SP',
                    'cep': '01304000',
                    'cnpj': '34.567.890/0001-12',
                    'chave_pix': 'sabor.da.vila@demo.com',
                    'logo_color': (214, 168, 99),
                },
            },
            {
                'email': 'techprime@demo.com',
                'nome': 'Diego Tech',
                'password': 'Tech@12345',
                'tipo': User.UserType.VENDEDOR,
                'telefone': '(11) 94444-0005',
                'vendedor': {
                    'nome_loja': 'Tech Prime',
                    'descricao_loja': 'Acessórios e gadgets para o cotidiano.',
                    'endereco_completo': 'Rua Vergueiro, 1500, Vila Mariana, São Paulo - SP',
                    'cep': '04101000',
                    'cnpj': '45.678.901/0001-23',
                    'chave_pix': 'tech.prime@demo.com',
                    'logo_color': (97, 124, 214),
                },
            },
            {
                'email': 'atelierrosa@demo.com',
                'nome': 'Elisa Rosa',
                'password': 'Atelie@12345',
                'tipo': User.UserType.VENDEDOR,
                'telefone': '(11) 93333-0006',
                'vendedor': {
                    'nome_loja': 'Ateliê Rosa',
                    'descricao_loja': 'Peças autorais com identidade artesanal.',
                    'endereco_completo': 'Rua Treze de Maio, 310, Bela Vista, São Paulo - SP',
                    'cep': '01327000',
                    'cnpj': '56.789.012/0001-34',
                    'chave_pix': 'atelie.rosa@demo.com',
                    'logo_color': (194, 112, 170),
                },
            },
        ]

        demo_categories = [
            ('Moda feminina', 'Vestidos, blusas e conjuntos'),
            ('Decoração', 'Itens para casa e ambiente'),
            ('Alimentos', 'Cestas e delícias artesanais'),
            ('Tecnologia', 'Acessórios e gadgets'),
            ('Artesanato', 'Produtos feitos à mão'),
        ]

        demo_products = {
            'Moda Solar': [
                ('Vestido Floral', 89.90, 12, True, (237, 190, 175)),
                ('Conjunto Leve', 129.90, 8, True, (245, 220, 204)),
            ],
            'Casa Aurora': [
                ('Kit Velas Artesanais', 49.90, 15, True, (198, 224, 233)),
                ('Vaso Decorativo', 79.90, 9, False, (214, 224, 214)),
            ],
            'Sabor da Vila': [
                ('Cesta Gourmet', 129.90, 10, True, (239, 219, 170)),
                ('Doce Artesanal', 34.90, 20, False, (248, 231, 207)),
            ],
            'Tech Prime': [
                ('Fone Bluetooth', 149.90, 14, True, (190, 206, 241)),
                ('Suporte para Celular', 39.90, 22, False, (210, 221, 246)),
            ],
            'Ateliê Rosa': [
                ('Bolsa Artesanal', 119.90, 7, True, (237, 198, 223)),
                ('Estojo Bordado', 59.90, 16, False, (246, 222, 238)),
            ],
        }

        media_dir = Path(settings.MEDIA_ROOT) / 'demo_seed'
        media_dir.mkdir(parents=True, exist_ok=True)

        with transaction.atomic():
            legacy_buyer_email = 'pe' + 'dro@demo.com'
            legacy_user = User.objects.filter(email=legacy_buyer_email).first()
            if legacy_user and not User.objects.filter(email='comprador@demo.com').exclude(pk=legacy_user.pk).exists():
                legacy_user.email = 'comprador@demo.com'
                legacy_user.nome = 'Cliente Demo'
                legacy_user.set_password('Comprador@12345')
                legacy_user.save(update_fields=['email', 'nome', 'password'])

            for data in demo_users:
                user, created = User.objects.get_or_create(
                    email=data['email'],
                    defaults={
                        'nome': data['nome'],
                        'telefone': data['telefone'],
                        'tipo': data['tipo'],
                    },
                )
                if created:
                    user.set_password(data['password'])
                    user.save()
                else:
                    changed = False
                    if user.nome != data['nome']:
                        user.nome = data['nome']
                        changed = True
                    if user.telefone != data['telefone']:
                        user.telefone = data['telefone']
                        changed = True
                    if user.tipo != data['tipo']:
                        user.tipo = data['tipo']
                        changed = True
                    if changed:
                        user.save()

                if data['tipo'] == User.UserType.COMPRADOR:
                    comprador, _ = Comprador.objects.get_or_create(
                        user=user,
                        defaults={
                            'cpf': data['comprador']['cpf'],
                            'endereco_completo': data['comprador']['endereco_completo'],
                            'cep': data['comprador']['cep'],
                        },
                    )
                    comprador.cpf = data['comprador']['cpf']
                    comprador.endereco_completo = data['comprador']['endereco_completo']
                    comprador.cep = data['comprador']['cep']
                    comprador.save(update_fields=['cpf', 'endereco_completo', 'cep'])

                if data['tipo'] == User.UserType.VENDEDOR:
                    vendedor, _ = Vendedor.objects.get_or_create(
                        user=user,
                        defaults={
                            'nome_loja': data['vendedor']['nome_loja'],
                            'descricao_loja': data['vendedor']['descricao_loja'],
                            'logo_url': '',
                            'endereco_completo': data['vendedor']['endereco_completo'],
                            'cep': data['vendedor']['cep'],
                            'cnpj': data['vendedor']['cnpj'],
                            'chave_pix': data['vendedor']['chave_pix'],
                        },
                    )
                    vendedor.nome_loja = data['vendedor']['nome_loja']
                    vendedor.descricao_loja = data['vendedor']['descricao_loja']
                    vendedor.endereco_completo = data['vendedor']['endereco_completo']
                    vendedor.cep = data['vendedor']['cep']
                    vendedor.cnpj = data['vendedor']['cnpj']
                    vendedor.chave_pix = data['vendedor']['chave_pix']

                    logo_path = media_dir / f"{user.email.split('@')[0]}_logo.png"
                    if not logo_path.exists():
                        image = Image.new('RGB', (1200, 800), data['vendedor']['logo_color'])
                        draw = ImageDraw.Draw(image)
                        draw.text((130, 320), data['vendedor']['nome_loja'], fill=(255, 255, 255))
                        image.save(logo_path, format='PNG')

                    vendedor.logo_url = f'http://127.0.0.1:8000/media/demo_seed/{logo_path.name}'
                    vendedor.save(update_fields=['logo_url', 'nome_loja', 'descricao_loja', 'endereco_completo', 'cep', 'cnpj', 'chave_pix'])

                    vendor_categories = {}
                    for nome, descricao in demo_categories:
                        category, _ = Categoria.objects.get_or_create(
                            vendedor=vendedor,
                            nome=nome,
                            defaults={'descricao': descricao, 'ativo': True},
                        )
                        if category.descricao != descricao or not category.ativo:
                            category.descricao = descricao
                            category.ativo = True
                            category.save(update_fields=['descricao', 'ativo'])
                        vendor_categories[nome] = category

                    product_specs = demo_products.get(vendedor.nome_loja, [])
                    for position, (product_name, price, stock, highlighted, color) in enumerate(product_specs, start=1):
                        category_name = demo_categories[(position - 1) % len(demo_categories)][0]
                        product, _ = Produto.objects.get_or_create(
                            vendedor=vendedor,
                            nome=product_name,
                            defaults={
                                'descricao': f'{product_name} disponível na loja {vendedor.nome_loja}.',
                                'preco': price,
                                'estoque': stock,
                                'destaque': highlighted,
                                'ativo': True,
                                'categoria': vendor_categories.get(category_name),
                            },
                        )
                        updated = False
                        if not product.descricao:
                            product.descricao = f'{product_name} disponível na loja {vendedor.nome_loja}.'
                            updated = True
                        if product.preco != price:
                            product.preco = price
                            updated = True
                        if product.estoque != stock:
                            product.estoque = stock
                            updated = True
                        if product.destaque != highlighted:
                            product.destaque = highlighted
                            updated = True
                        if not product.ativo:
                            product.ativo = True
                            updated = True
                        if not product.categoria_id:
                            product.categoria = vendor_categories.get(category_name)
                            updated = True
                        if updated:
                            product.save()

                        photo_path = media_dir / f"{vendedor.nome_loja.lower().replace(' ', '_')}_{position}.png"
                        if not photo_path.exists():
                            image = Image.new('RGB', (1200, 900), color)
                            draw = ImageDraw.Draw(image)
                            draw.rounded_rectangle((60, 60, 1140, 840), radius=60, outline=(255, 255, 255), width=18)
                            draw.text((120, 320), product_name, fill=(255, 255, 255))
                            draw.text((120, 430), vendedor.nome_loja, fill=(255, 255, 255))
                            image.save(photo_path, format='PNG')

                        foto = product.fotos.first()
                        foto_ausente = (
                            not foto
                            or not foto.imagem
                            or not (Path(settings.MEDIA_ROOT) / foto.imagem.name).exists()
                        )
                        if foto_ausente:
                            with photo_path.open('rb') as photo_file:
                                if not foto:
                                    foto = FotoProduto(produto=product, ordem=1)
                                foto.ordem = 1
                                foto.imagem.save(photo_path.name, File(photo_file), save=True)

            self.stdout.write(self.style.SUCCESS('Dados demo criados/atualizados com sucesso.'))
