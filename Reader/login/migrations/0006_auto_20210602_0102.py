# Generated by Django 2.2.4 on 2021-06-02 01:02

from django.db import migrations
import login.fields


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0005_auto_20210601_0225'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='image',
            field=login.fields.ThumbnailImageField(blank=True, null=True, upload_to='profile/%Y/%m'),
        ),
    ]