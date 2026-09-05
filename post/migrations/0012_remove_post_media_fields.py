from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0011_migrate_post_media_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='category',
        ),
        migrations.RemoveField(
            model_name='post',
            name='is_proccessed',
        ),
        migrations.RemoveField(
            model_name='post',
            name='media_type',
        ),
        migrations.RemoveField(
            model_name='post',
            name='media_url',
        ),
        migrations.RemoveField(
            model_name='post',
            name='raw_s3_key',
        ),
        migrations.RemoveField(
            model_name='post',
            name='thumbnail_url',
        ),
        migrations.RemoveField(
            model_name='post',
            name='upload_status',
        ),
    ]
