# Generated by Django 5.1.2 on 2024-10-24 02:45

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appGestionInventario', '0002_alter_usoitemlaboratorio_usuario_delete_usuario'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categoria',
            name='cod_categoria',
            field=models.CharField(default=uuid.uuid4, editable=False, max_length=10, primary_key=True, serialize=False),
        ),
    ]
