# Generated by Django 2.2.4 on 2021-05-22 01:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0004_auto_20210521_0105'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='image_sub1',
        ),
        migrations.RemoveField(
            model_name='book',
            name='image_sub2',
        ),
        migrations.RemoveField(
            model_name='book',
            name='image_sub3',
        ),
        migrations.AddField(
            model_name='book',
            name='publication_date',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='review',
            name='book',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='book.Book'),
        ),
    ]