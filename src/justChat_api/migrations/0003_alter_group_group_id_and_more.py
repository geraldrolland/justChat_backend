# Generated by Django 4.2.6 on 2024-10-28 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('justChat_api', '0002_alter_group_group_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='group_id',
            field=models.CharField(default='<function uuid4 at 0x0000023B3DFFA7A0>', editable=False, max_length=124, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='isgroupadmin',
            name='is_group_admin_id',
            field=models.CharField(default='<function uuid4 at 0x0000023B3DFFA7A0>', editable=False, max_length=124, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='message',
            name='message_id',
            field=models.CharField(default='501ef840-96b9-4c4f-8401-cace51c6780e', editable=False, max_length=124, primary_key=True, serialize=False),
        ),
    ]
