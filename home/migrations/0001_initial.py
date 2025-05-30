# Generated by Django 5.2 on 2025-05-13 06:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Members',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('username', models.CharField(max_length=255, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('phone', models.CharField(max_length=20, unique=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='user-images/')),
                ('user_type', models.CharField(choices=[('Admin', 'Admin'), ('Customer', 'Customer')], max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Books',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('author', models.CharField(max_length=255)),
                ('pageCount', models.IntegerField()),
                ('borrowPrice', models.DecimalField(decimal_places=2, max_digits=10)),
                ('buyPrice', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('rating', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('stock', models.IntegerField()),
                ('count', models.IntegerField(default=0, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='book-images/')),
                ('category', models.CharField(max_length=255, null=True)),
                ('description', models.TextField(null=True)),
                ('published', models.IntegerField(null=True)),
                ('ratingCount', models.IntegerField(null=True)),
                ('book_category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='books', to='home.category')),
            ],
        ),
        migrations.CreateModel(
            name='BorrowedBook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('borrowed_date', models.DateTimeField(auto_now_add=True)),
                ('returned', models.BooleanField(default=False)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.books')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.members')),
            ],
        ),
    ]
