# Generated by Django 4.1 on 2022-09-08 20:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('access', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
