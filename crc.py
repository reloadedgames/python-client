import binascii
import os

# Parameters
current_path = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_path, 'checksum.txt')
chunk_size = 8192

with open(file_path, 'r+b') as f:
    chunk = f.read(chunk_size)

    while chunk:
        # Perform CRC
        length = chunk.__len__()
        crc = binascii.crc32(chunk) & 0xffffffff

        print 'Length = {0}'.format(length)
        print 'CRC = {0} = {0:x}'.format(crc)

        # Next chunk
        chunk = f.read(chunk_size)