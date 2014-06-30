"""
Uploads the package contents to the S3 origin bucket.

Usage:
    supernode upload [options]
    supernode upload -h | --help

Options:
    --no-resume         Do not resume multipart uploads
    --no-skip           Do not skip files which have already been uploaded
"""

import boto
import math
import multiprocessing
import os
from boto.s3.multipart import MultiPartUpload

from concurrent.futures import ProcessPoolExecutor
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
        bucket = _get_bucket(credentials)
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

                bytes_per_chunk = max(int(math.sqrt(5242880) * math.sqrt(size)), 5242880)
                chunks_count = int(math.ceil(size / float(bytes_per_chunk)))
                parts = multipart.get_all_parts()

                # Pool for parallel uploading
                workers = multiprocessing.cpu_count() * 2
                with ProcessPoolExecutor(max_workers=workers) as pool:
                    futures = []

                    for i in range(chunks_count):
                        part_number = i + 1
                        offset = i * bytes_per_chunk
                        remaining_bytes = size - offset
                        part_size = min([bytes_per_chunk, remaining_bytes])

                        if (part_number, part_size) in [(p.part_number, p.size) for p in parts]:
                            continue

                        futures.append(pool.submit(_upload_multipart, credentials, multipart.id, key_name,
                                                   local_path, part_number, offset, part_size))

                    for future in futures:
                        future.result(timeout=1800)

                multipart.complete_upload()

        print 'Upload complete.'


def _get_bucket(credentials):
    s3 = boto.connect_s3(credentials['AccessKeyId'], credentials['SecretAccessKey'],
                         security_token=credentials['SessionToken'])

    return s3.get_bucket(credentials['BucketName'], validate=False)


def _upload_multipart(credentials, multipart_id, key_name, path, part_number, offset, size):
    bucket = _get_bucket(credentials)
    multipart = MultiPartUpload(bucket)
    multipart.id = multipart_id
    multipart.key_name = key_name

    with open(path, 'rb') as f:
        f.seek(offset)
        multipart.upload_part_from_file(f, part_number, size=size)