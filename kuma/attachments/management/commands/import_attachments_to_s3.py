import os
from multiprocessing.pool import ThreadPool
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection
from kuma.attachments.models import AttachmentRevision
import boto3

REVISIONS_QUERY = """
    select id, file
    from attachments_attachmentrevision
    where not is_s3_migrated
    limit %s;
"""

BATCH_SIZE = 1000
UPLOAD_PROCESSES = 150


class Command(BaseCommand):
    help = 'Moves a batch of {} attachments to S3'.format(str(BATCH_SIZE))

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute(REVISIONS_QUERY, [BATCH_SIZE])
            rows = cursor.fetchall()

        if len(rows) == 0:
            print 'Nothing left to migrate!'
            return

        ids, filenames = zip(*rows)

        s3 = boto3.client('s3',
                          aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

        def upload(filename):
            s3.upload_file(
                os.path.join(settings.MEDIA_ROOT, filename),
                settings.AWS_STORAGE_BUCKET_NAME,
                filename)

        pool = ThreadPool(processes=UPLOAD_PROCESSES)
        pool.map(upload, filenames)

        AttachmentRevision.objects.filter(id__in=ids).update(is_s3_migrated=True)
        print 'Migrated {} attachments to S3'.format(str(len(ids)))
