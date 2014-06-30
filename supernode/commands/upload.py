"""
Uploads the package contents to the S3 origin bucket.

Usage:
    supernode upload [options]
    supernode upload -h | --help

Options:
    --no-resume         Do not resume multipart uploads
    --no-skip           Do not skip files which have already been uploaded
"""

# This must be first so it can replace the built-in http/url methods
# with the gevent versions for use by boto
import gevent.monkey
gevent.monkey.patch_all()

import boto
import math
import os

from boto.s3.multipart import MultiPartUpload
from supernode.command import Command


class UploadCommand(Command):
    def help(self):
        return __doc__

    def run(self, options):
        # Validate settings
        if ('partner_id', 'version_id', 'path') <= self.settings.keys():
            exit('The current saved configuration does not support uploading')

        path = self.settings['path']
        version_id = self.settings['version_id']

        print 'Querying upload credentials...'
        credentials = self.api.get_upload_credentials(version_id)
        prefix = credentials['KeyPrefix']

        print 'Connecting to S3 bucket...'
        bucket = self.get_bucket(credentials)
        keys = []

        if not options['--no-skip']:
            print 'Querying existing objects...'
            keys = list(bucket.list(prefix))

        multipart_uploads = []

        if not options['--no-resume']:
            print 'Querying multipart uploads...'
            multipart_uploads = list(bucket.list_multipart_uploads())

        print 'Uploading files...'

        for root, dirs, files in os.walk(path):
            for f in files:
                local_path = os.path.join(root, f)
                relative_path = local_path.replace(path, '').replace('\\', '/').lstrip('/\\')
                key_name = prefix + relative_path
                size = os.path.getsize(local_path)

                # Skip files that have already been uploaded
                if (key_name, size) in [(k.name, k.size) for k in keys]:
                    continue

                print relative_path

                # Files smaller than 50MB can be uploaded directly
                if size <= 52428800:
                    key = bucket.new_key(key_name)
                    key.set_contents_from_filename(local_path)
                    continue

                # Continue the last multipart upload?
                matching_uploads = [u for u in multipart_uploads if u.key_name == key_name]

                if matching_uploads:
                    multipart = matching_uploads[-1]
                else:
                    multipart = bucket.initiate_multipart_upload(key_name)

                ParallelUpload(credentials, key_name, multipart.id, local_path).upload()

        print 'Upload complete.'

    @staticmethod
    def get_bucket(credentials):
        s3 = boto.connect_s3(credentials['AccessKeyId'], credentials['SecretAccessKey'],
                             security_token=credentials['SessionToken'])

        return s3.get_bucket(credentials['BucketName'], validate=False)


class ParallelUpload(object):
    def __init__(self, credentials, key_name, multipart_id, path):
        file_size = os.path.getsize(path)

        self.__chunk_size = max(int(math.sqrt(5242880) * math.sqrt(file_size)), 5242880)
        self.__chunk_count = int(math.ceil(file_size / float(self.__chunk_size)))
        self.__credentials = credentials
        self.__file_size = file_size
        self.__key_name = key_name
        self.__multipart_id = multipart_id
        self.__path = path

    def _get_multipart(self):
        bucket = UploadCommand.get_bucket(self.__credentials)
        multipart = MultiPartUpload(bucket)
        multipart.id = self.__multipart_id
        multipart.key_name = self.__key_name

        return multipart

    def _upload_part(self, part_number, offset, size):
        multipart = self._get_multipart()

        with open(self.__path, 'rb') as f:
            f.seek(offset)
            multipart.upload_part_from_file(f, part_number, size=size)

    def upload(self):
        multipart = self._get_multipart()
        parts = multipart.get_all_parts()
        greenlets = []

        for i in range(self.__chunk_count):
            part_number = i + 1
            offset = i * self.__chunk_size
            remaining_bytes = self.__file_size - offset
            part_size = min([self.__chunk_size, remaining_bytes])

            if (part_number, part_size) in [(p.part_number, p.size) for p in parts]:
                continue

            greenlets.append(gevent.spawn(self._upload_part, part_number, offset, part_size))

        gevent.joinall(greenlets)
        multipart.complete_upload()