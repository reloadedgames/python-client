"""
Uploads the package contents to the S3 origin bucket.

Usage:
    supernode upload
"""

import boto
import math
import os

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
        s3 = boto.connect_s3(credentials['AccessKeyId'], credentials['SecretAccessKey'],
                             security_token=credentials['SessionToken'])

        bucket = s3.get_bucket(credentials['BucketName'], validate=False)

        print 'Uploading files...'

        for root, dirs, files in os.walk(path):
            for f in files:
                local_path = os.path.join(root, f)
                relative_path = local_path.replace(path, '').replace('\\', '/').lstrip('/\\')
                key_name = prefix + relative_path
                size = os.path.getsize(local_path)

                print relative_path

                # Files smaller than 50MB can be uploaded directly
                if size <= 52428800:
                    key = bucket.new_key(key_name)
                    key.set_contents_from_filename(local_path)
                    continue

                # Use multipart upload
                multipart = bucket.initiate_multipart_upload(key_name)
                bytes_per_chunk = max(int(math.sqrt(5242880) * math.sqrt(size)), 5242880)
                chunks_count = int(math.ceil(size / float(bytes_per_chunk)))

                with open(local_path, 'rb') as fp:
                    for i in range(chunks_count):
                        offset = i * bytes_per_chunk
                        remaining_bytes = size - offset
                        part_size = min([bytes_per_chunk, remaining_bytes])
                        part_number = i + 1

                        multipart.upload_part_from_file(fp, part_number, size=part_size)

                    multipart.complete_upload()

        print 'Upload complete.'