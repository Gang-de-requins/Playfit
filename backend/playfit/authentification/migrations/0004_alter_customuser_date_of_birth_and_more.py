# Generated by Django 5.1.1 on 2025-01-23 12:18

import utilities.encrypted_fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentification', '0003_alter_customuser_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='date_of_birth',
            field=utilities.encrypted_fields.EncryptedDateField(max_length=10),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='email',
            field=utilities.encrypted_fields.EncryptedEmailField(max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='first_name',
            field=utilities.encrypted_fields.EncryptedCharField(blank=True, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='fitness_level',
            field=models.CharField(blank=True, choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')], default='beginner', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='gender',
            field=utilities.encrypted_fields.EncryptedCharField(blank=True, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], default='other', max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='last_name',
            field=utilities.encrypted_fields.EncryptedCharField(blank=True, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='password',
            field=models.CharField(max_length=128, verbose_name='password'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='physical_particularities',
            field=utilities.encrypted_fields.EncryptedTextField(blank=True, null=True),
        ),
    ]
