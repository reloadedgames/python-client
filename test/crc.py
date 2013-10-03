import binascii
import os


def calculate_chunks(path, chunk_size=1048576):
    if not os.path.isdir(path):
        exit('You must specify a directory')

    chunks = {}

    for root, dirs, files in os.walk(path):
        for name in files:
            file_path = os.path.join(root, name)
            relative_path = file_path.replace(path, '')
            chunks[relative_path] = {
                'pieces': [],
                'size': os.path.getsize(file_path)
            }

            with open(file_path, 'r+b') as f:
                chunk = f.read(chunk_size)

                while chunk:
                    crc = binascii.crc32(chunk) & 0xffffffff
                    chunks[relative_path]['pieces'].append(crc)
                    chunk = f.read(chunk_size)

    return chunks