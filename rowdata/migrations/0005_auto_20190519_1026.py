# Generated by Django 2.2.1 on 2019-05-19 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rowdata', '0004_auto_20190519_1025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='race',
            name='end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]