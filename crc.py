import binascii
import os

path = 'C:\Users\lmcnearney\Downloads\Package'
chunk_size = 1048576

if not os.path.isdir(path):
    exit('You must specify a directory')

for root, dirs, files in os.walk(path):
    for name in files:
        path = os.path.join(root, name)
        print path

        with open(path, 'r+b') as f:
            part = 0
            chunk = f.read(chunk_size)

            while chunk:
                part += 1
                length = chunk.__len__()
                crc = binascii.crc32(chunk) & 0xffffffff
                print 'Part = {0}, Length = {1}, CRC = {2}, Hex = {2:x}'.format(part, length, crc)

                chunk = f.read(chunk_size)

        print ''