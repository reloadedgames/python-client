from pprint import pprint
import requests

# Global
base_url = 'https://manifests.sandbox.reloadedtech.com'
username = 'lance@mcnearney.net'
password = 'testpass1'
credentials = (username, password)

# Login
url = '{0}/users/current'.format(base_url)
response = requests.get(url, auth=credentials)
json = response.json()
user_id = json['UserId']

# Pull accessible partners
url = '{0}/users/{1}/partners'.format(base_url, user_id)
response = requests.get(url, auth=credentials)
json = response.json()

for partner in json:
    print '{0} = {1}'.format(partner['Name'], partner['PartnerId'])

# Pull partner information
partner_id = '5178801235edd1035499887d'
url = '{0}/partners/{1}'.format(base_url, partner_id)
response = requests.get(url, auth=credentials)
json = response.json()
packages = json['Packages']

for package in packages:
    print package

# Pull private key
url = '{0}/partners/{1}/private-key'.format(base_url, partner_id)
response = requests.get(url, auth=credentials)
private_key = response.content
print private_key

# Pull SFTP settings
url = '{0}/settings/upload'.format(base_url)
response = requests.get(url)
json = response.json()
print json