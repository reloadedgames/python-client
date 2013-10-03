from old.test import crc


path = 'C:\Users\lmcnearney\Downloads\Package\\'

result = crc.calculate_chunks(path)

for key in result:
    print '{0} - {1} bytes'.format(key, result[key]['size'])

    for crc in result[key]['pieces']:
        print '=> {0} = {0:x}'.format(crc)

    print ''