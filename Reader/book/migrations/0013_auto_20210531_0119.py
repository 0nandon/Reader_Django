# Generated by Django 2.2.4 on 2021-05-31 01:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0012_auto_20210530_0327'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='book',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='book.Book'),
        ),
    ]
