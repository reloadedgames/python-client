"""
Uploads the package contents to the S3 origin bucket.

Usage:
    supernode upload
"""

import boto
import math
import os
import sys

from progressbar import Bar, FileTransferSpeed, Percentage, ProgressBar
from supernode.command import Command

progress = None


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

        # Build a list of existing keys and their sizes to avoid re-uploading existing files
        keys = {}

        for key in bucket.list(prefix):
            keys[key.name] = key.size

        print 'Uploading files...'

        for root, dirs, files in os.walk(path):
            for f in files:
                local_path = os.path.join(root, f)
                relative_path = local_path.replace(path, '').replace('\\', '/').lstrip('/\\')
                key_name = prefix + relative_path
                size = os.path.getsize(local_path)

                #if key_name in keys and keys[key_name] == size:
                #    continue

                global progress

                # Objects over 5GB must be uploading using multipart
                multipart_required = (size >= 5368709120)

                if multipart_required:
                    with open(local_path, 'rb') as fp:
                        chunk_size = 67108864
                        chunks = int(math.ceil(size / float(chunk_size)))
                        multipart = bucket.initiate_multipart_upload(key_name)

                        for i in range(chunks):
                            part = i + 1
                            part_size = chunk_size

                            if part * chunk_size >= size:
                                part_size = size - (part - 1 * chunk_size) - 1

                            widgets = [os.path.basename(local_path) + ' ({0}/{1})'.format(part, chunks), Percentage(),
                                       ' ', Bar(), ' ', FileTransferSpeed()]
                            progress = ProgressBar(widgets=widgets, maxval=part_size)
                            progress.start()

                            multipart.upload_part_from_file(fp, part, size=part_size,
                                                            cb=self.update_progress, num_cb=100)
                            progress.finish()

                        multipart.complete_upload()

                else:
                    widgets = [os.path.basename(local_path) + ' ', Percentage(), ' ', Bar(), ' ', FileTransferSpeed()]
                    progress = ProgressBar(widgets=widgets, maxval=size if size > 0 else 1)
                    progress.start()
                    key = bucket.new_key(key_name)
                    key.set_contents_from_filename(local_path, cb=self.update_progress, num_cb=100)
                    progress.finish()

        #self.api.complete_upload(version_id)
        print 'Upload complete.'

    @staticmethod
    def update_progress(current, total):
        if total == 0:
            current = 1

        progress.update(current)