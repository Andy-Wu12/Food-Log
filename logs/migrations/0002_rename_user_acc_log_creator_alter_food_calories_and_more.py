# Generated by Django 4.1 on 2022-08-14 05:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logs', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='log',
            old_name='user_acc',
            new_name='creator',
        ),
        migrations.AlterField(
            model_name='food',
            name='calories',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='food',
            name='ingredients',
            field=models.CharField(max_length=500, null=True),
        ),
    ]
