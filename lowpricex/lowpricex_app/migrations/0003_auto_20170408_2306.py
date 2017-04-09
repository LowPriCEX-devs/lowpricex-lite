# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-04-08 23:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lowpricex_app', '0002_juegodetalles'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='imagenjuego',
            name='juego',
        ),
        migrations.RemoveField(
            model_name='juegodetalles',
            name='juego',
        ),
        migrations.RemoveField(
            model_name='videojuego',
            name='juego',
        ),
        migrations.RemoveField(
            model_name='juego',
            name='categoria',
        ),
        migrations.RemoveField(
            model_name='juego',
            name='desarrolladores',
        ),
        migrations.RemoveField(
            model_name='juego',
            name='fechaSalida',
        ),
        migrations.RemoveField(
            model_name='juego',
            name='generos',
        ),
        migrations.RemoveField(
            model_name='juego',
            name='keywords',
        ),
        migrations.RemoveField(
            model_name='juego',
            name='publishers',
        ),
        migrations.RemoveField(
            model_name='juego',
            name='temas',
        ),
        migrations.AddField(
            model_name='juego',
            name='portadaCEX',
            field=models.URLField(null=True),
        ),
        migrations.AlterField(
            model_name='juego',
            name='sku',
            field=models.TextField(primary_key=True, serialize=False),
        ),
        migrations.DeleteModel(
            name='Categoria',
        ),
        migrations.DeleteModel(
            name='Empresa',
        ),
        migrations.DeleteModel(
            name='Genero',
        ),
        migrations.DeleteModel(
            name='ImagenJuego',
        ),
        migrations.DeleteModel(
            name='JuegoDetalles',
        ),
        migrations.DeleteModel(
            name='Keyword',
        ),
        migrations.DeleteModel(
            name='Tema',
        ),
        migrations.DeleteModel(
            name='VideoJuego',
        ),
    ]