# Generated by Django 5.1.5 on 2025-02-12 18:24

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_discussionpost_discussionreply'),
    ]

    operations = [
        migrations.RenameField(
            model_name='donation',
            old_name='donation_date',
            new_name='created_at',
        ),
        migrations.RenameField(
            model_name='donation',
            old_name='note',
            new_name='message',
        ),
        migrations.AddField(
            model_name='donation',
            name='email',
            field=models.EmailField(default=django.utils.timezone.now, max_length=254),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='donation',
            name='name',
            field=models.CharField(default=django.utils.timezone.now, max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='donation',
            name='proof',
            field=models.FileField(blank=True, null=True, upload_to='donation_proofs/'),
        ),
        migrations.AlterField(
            model_name='donation',
            name='donor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='donations', to=settings.AUTH_USER_MODEL),
        ),
    ]
