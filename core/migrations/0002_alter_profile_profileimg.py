# Generated by Django 5.1.3 on 2024-12-01 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profileimg',
            field=models.ImageField(default='blank-profile-picture-973460_1280.png', upload_to='profile_images/'),
        ),
    ]
