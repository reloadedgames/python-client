import binascii
import os


def calculate_chunks(path, chunk_size):
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

if __name__ == '__main__':
    _path = 'C:\Users\lmcnearney\Downloads\Package\\'
    _chunk_size = 1048576

    result = calculate_chunks(_path, _chunk_size)

    for key in result:
        print '{0} - {1} bytes'.format(key, result[key]['size'])

        for crc in result[key]['pieces']:
            print '=> {0} = {0:x}'.format(crc)

        print ''