# Generated by Django 2.0.5 on 2018-05-24 08:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ui', '0002_auto_20180523_1931'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='canton',
            name='city',
        ),
        migrations.AddField(
            model_name='city',
            name='canton',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='ui.Canton'),
        ),
    ]
