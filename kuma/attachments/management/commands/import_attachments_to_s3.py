import os
from multiprocessing.pool import ThreadPool

import boto3
from constance import config
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection

from kuma.attachments.models import AttachmentRevision

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

        print os.environ
        if len(rows) == 0:
            print 'Nothing left to migrate. Setting S3 as default storage, restart now!'
            config.USE_S3_AS_ATTACHMENT_STORAGE = True
            return

        ids, filenames = zip(*rows)

        s3 = boto3.client('s3')

        def upload(filename):
            s3.upload_file(
                os.path.join(settings.MEDIA_ROOT, filename),
                settings.MDN_API_S3_BUCKET_NAME,
                filename)

        pool = ThreadPool(processes=UPLOAD_PROCESSES)
        pool.map(upload, filenames)

        AttachmentRevision.objects.filter(id__in=ids).update(is_s3_migrated=True)
        print 'Migrated {} attachments to S3'.format(str(len(ids)))
