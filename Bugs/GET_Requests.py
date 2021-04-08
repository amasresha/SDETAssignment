import requests

base_uri = "http://192.168.1.228:8088/hash/"


id_uri = "1"
url = base_uri + id_uri

# send get request
response = requests.get(url)
print(response.content)
