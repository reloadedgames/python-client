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
import gevent
import functools
import math
import os

from boto.s3.multipart import MultiPartUpload
from progressbar import ETA, FileTransferSpeed, Percentage, ProgressBar, WidgetHFill
from supernode.command import Command

# The upload progress bar
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

                # Files smaller than 50MB can be uploaded directly
                if size <= 52428800:
                    key = bucket.new_key(key_name)
                    progress_bar = self.create_progress_bar(relative_path, size)
                    key.set_contents_from_filename(local_path, cb=self.update_progress, num_cb=100)
                    progress_bar.finish()
                    continue

                # Continue the last multipart upload?
                matching_uploads = [u for u in multipart_uploads if u.key_name == key_name]

                if matching_uploads:
                    multipart = matching_uploads[-1]
                else:
                    multipart = bucket.initiate_multipart_upload(key_name)

                ParallelUpload(credentials, key_name, multipart.id, local_path, relative_path).upload()

        print 'Upload complete.'

    @staticmethod
    def get_bucket(credentials):
        s3 = boto.connect_s3(credentials['AccessKeyId'], credentials['SecretAccessKey'],
                             security_token=credentials['SessionToken'])

        return s3.get_bucket(credentials['BucketName'], validate=False)

    @staticmethod
    def create_progress_bar(name, size):
        if size == 0:
            size = 1

        global progress
        widgets = [Percentage(), ' ', NameWidget(name), ' ', FileTransferSpeed(), ' ', ETA()]
        progress = ProgressBar(widgets=widgets, maxval=size)
        progress.start()

        return progress

    @staticmethod
    def update_progress(current, total):
        if total == 1:
            current = 1

        global progress
        progress.update(current)


class ParallelUpload(object):
    def __init__(self, credentials, key_name, multipart_id, path, relative_path):
        file_size = os.path.getsize(path)

        self.__chunk_size = max(int(math.sqrt(5242880) * math.sqrt(file_size)), 5242880)
        self.__chunk_count = int(math.ceil(file_size / float(self.__chunk_size)))
        self.__credentials = credentials
        self.__file_size = file_size
        self.__key_name = key_name
        self.__multipart_id = multipart_id
        self.__path = path
        self.__progress = [0] * self.__chunk_count
        self.__relative_path = relative_path
        self.__progress_bar = UploadCommand.create_progress_bar(self.__relative_path, file_size)

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

            multipart.upload_part_from_file(f, part_number,
                                            cb=functools.partial(self._update_progress, part_number),
                                            num_cb=100,
                                            size=size)

    def _update_progress(self, part_number, current, total):
        self.__progress[part_number - 1] = current
        sum_current = sum(self.__progress)

        UploadCommand.update_progress(sum_current, self.__file_size)

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
        self.__progress_bar.finish()
        multipart.complete_upload()


class NameWidget(WidgetHFill):
    def __init__(self, name):
        self.__name = name

    def update(self, pbar, width):
        name = self.__name

        if len(name) > width:
            name = '...' + name[-width + 3:]

        return name + ''.ljust(width - len(name))