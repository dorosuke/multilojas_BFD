# Generated manually for sprint 3.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Produto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255)),
                ('descricao', models.TextField()),
                ('preco', models.DecimalField(decimal_places=2, max_digits=10)),
                ('estoque', models.PositiveIntegerField(default=0)),
                ('destaque', models.BooleanField(default=False)),
                ('ativo', models.BooleanField(default=True)),
                ('data_cadastro', models.DateTimeField(auto_now_add=True)),
                ('vendedor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='produtos', to='core.vendedor')),
            ],
            options={
                'ordering': ['-destaque', '-data_cadastro'],
            },
        ),
        migrations.CreateModel(
            name='FotoProduto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imagem', models.ImageField(upload_to='produtos/')),
                ('ordem', models.PositiveSmallIntegerField(default=0)),
                ('produto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fotos', to='core.produto')),
            ],
            options={
                'ordering': ['ordem', 'id'],
            },
        ),
    ]
