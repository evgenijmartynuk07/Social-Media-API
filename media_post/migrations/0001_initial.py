# Generated by Django 4.2 on 2023-04-28 15:27

from django.db import migrations, models
import django.db.models.deletion
import media_post.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("user", "0005_alter_follow_follower_alter_follow_following"),
    ]

    operations = [
        migrations.CreateModel(
            name="Post",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("text_content", models.TextField(blank=True, max_length=1000)),
                (
                    "media_attachment",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to=media_post.models.post_image_file_path,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="user.userprofile",
                    ),
                ),
            ],
        ),
    ]
