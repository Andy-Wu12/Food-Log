# Generated by Django 4.1 on 2022-09-07 20:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logs', '0003_food_image_alter_food_calories_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='food',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='logs', verbose_name='Image (Optional)'),
        ),
    ]