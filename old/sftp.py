# SFTP
host = '173.195.34.8'
port = 30000
fingerprint = '7f:a2:98:2a:aa:3b:b4:3e:75:3e:05:a1:d1:a3:03:d2'.replace(':', '')

# Credentials
partner_id = '5178801235edd1035499887d'
private_key = '''-----BEGIN DSA PRIVATE KEY-----
MIIBuwIBAAKBgQCyssu/sK8YhBuWv6iO5JGtFIli4mnL7v+GTWTCuYpeD+g6ynZD
9ZuTvIVo4eaw94uIaIG/91MJdhzWV0SoWJgoHRSFAE4saFCLtAEQZ8Q+lu8utFTB
Y78CJ25lkDtoscUTFV8MXEp5cNDtiD0mibjAbTJBKMn5llVO1jMHMqvE3QIVAOSY
RdcnbeJo1ZQ01iXyHRV92rc5AoGACcRE0k/6yIxEDJPrKEHv9Ycwx8l+KzTBLAh6
CcIi46ounQJfsIHzfcshTYSUVqZBovxqzGschrsN7kD7AHOmF2J3EmMejAVnbwCs
4e+3ZAvru+utzq+sjM5Yu308s+L8rwC2s8GEVB/fDE+jt7yDKYmOo41HcehanCHs
eQCrdJsCgYAI6NVHh5qF/aVOIqVU0h9Xou2pr8nHmIYnkQ01dc+ILElsik1g0dzp
VaQtz2mWHZz/EW+nQsdr9ExASKhZZzb+UcXPU6E06O1jePQ3fkJGqhyycJV76QEY
qDS+VgFyWFTD3bmeyuSLTRClRFwnbSD34v+sxFVfHCfaS6hvDjpMkQIVAOPCckCc
cVsSZjGJ/OViSv9SgyOt
-----END DSA PRIVATE KEY-----'''

import binascii
import StringIO
import paramiko

# Load the private key from a string
key_file = StringIO.StringIO(private_key)
key = paramiko.DSSKey.from_private_key(key_file)

# Open a connection
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname=host, port=port, username=partner_id, pkey=key, look_for_keys=False)

# Verify fingerprint
server_key = ssh.get_transport().get_remote_server_key()
server_fingerprint = binascii.hexlify(server_key.get_fingerprint())

if server_fingerprint != fingerprint:
    raise Exception('Fingerprint does not match')

# SFTP client
sftp = ssh.open_sftp()
contents = sftp.listdir_attr('.')

for item in contents:
    print item

ssh.close()