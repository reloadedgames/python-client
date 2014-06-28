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
                    bucket.initiate_multipart_upload(key_name)

                bytes_per_chunk = max(int(math.sqrt(5242880) * math.sqrt(size)), 5242880)
                chunks_count = int(math.ceil(size / float(bytes_per_chunk)))
                parts = multipart.get_all_parts()

                with open(local_path, 'rb') as fp:
                    for i in range(chunks_count):
                        part_number = i + 1
                        offset = i * bytes_per_chunk
                        remaining_bytes = size - offset
                        part_size = min([bytes_per_chunk, remaining_bytes])

                        if (part_number, part_size) in [(p.part_number, p.size) for p in parts]:
                            continue

                        multipart.upload_part_from_file(fp, part_number, size=part_size)

                    multipart.complete_upload()

        print 'Upload complete.'