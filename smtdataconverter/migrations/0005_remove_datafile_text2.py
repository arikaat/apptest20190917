# Generated by Django 2.2.1 on 2019-08-28 05:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('smtdataconverter', '0004_datafile_text2'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datafile',
            name='text2',
        ),
    ]
