from django.db import migrations


def forwards(apps, schema_editor):
    Post = apps.get_model('post', 'Post')
    PostMedia = apps.get_model('post', 'PostMedia')

    PostMedia.objects.bulk_create([
        PostMedia(
            post=post,
            content_type=post.media_type,
            position=0,
            media_url=post.media_url,
            media_key=post.raw_s3_key,
            is_processed=post.is_proccessed,
            thumbnail_url=post.thumbnail_url,
            category=post.category,
            upload_status=post.upload_status,
        )
        for post in Post.objects.all()
    ])


def backwards(apps, schema_editor):
    PostMedia = apps.get_model('post', 'PostMedia')
    PostMedia.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0010_postmedia'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
