# Generated by Django 4.1 on 2022-08-12 00:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('logs', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='user_acc',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
