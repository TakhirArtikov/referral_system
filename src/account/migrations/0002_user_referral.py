# Generated by Django 4.0.4 on 2024-02-12 10:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='referral',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    related_name='registered_users', to='account.referral',
                                    verbose_name='Registered referral code'),
        ),
    ]
