# Generated by Django 5.1.1 on 2024-10-30 01:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentification', '0003_customuser_physical_particularities'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='first_name',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='fitness_level',
            field=models.CharField(choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='gender',
            field=models.CharField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='last_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='physical_particularities',
            field=models.TextField(null=True),
        ),
    ]
