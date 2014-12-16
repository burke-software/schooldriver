from storages.backends.s3boto import S3BotoStorage
from django.db import connection

class MediaRootS3BotoStorage(S3BotoStorage):
    def __init__(self, *args, **kwargs):
        path = 'media'
        if hasattr(connection, 'schema_name'):
            path = path + '/' + connection.schema_name
        kwargs['location'] = path
        super(MediaRootS3BotoStorage, self).__init__(*args, **kwargs)
