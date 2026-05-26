from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_categoria_produto_categoria_variacaoproduto'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pedido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('criado', 'Criado'), ('cancelado', 'Cancelado')], default='criado', max_length=20)),
                ('shipping_address', models.TextField()),
                ('shipping_provider', models.CharField(default='correios_stub', max_length=50)),
                ('shipping_value', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('subtotal', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('comprador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pedidos', to='core.user')),
                ('loja', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pedidos', to='core.vendedor')),
            ],
            options={
                'ordering': ['-created_at', '-id'],
            },
        ),
        migrations.CreateModel(
            name='PedidoItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('pedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itens', to='core.pedido')),
                ('produto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='pedido_itens', to='core.produto')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
    ]

