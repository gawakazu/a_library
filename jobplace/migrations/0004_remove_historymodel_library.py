# Generated by Django 3.2.6 on 2023-01-15 08:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobplace', '0003_bookmodel_book3'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historymodel',
            name='library',
        ),
    ]