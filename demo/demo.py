import os
import requests
from bs4 import BeautifulSoup
import time
from queue import Queue
url = "https://api.convertio.co/convert"
data = '{"apikey": "ed8827e96df41a5f0ff9fbe9a04e1043", "input":"upload", "outputformat":"azw3"}'
res = requests.post(url=url, data=data)
res_json=res.json()
print(res_json)
putId = res_json['data']['id']
print(putId)
bookPath = "./novel/《百年孤独》加西亚·马尔克斯.epub"
bookName = "《百年孤独》加西亚·马尔克斯"
putUrl = "https://api.convertio.co/convert/"+str(putId)+"/"+bookName+".epub"
change_res = requests.put(url=putUrl,data=open(bookPath, 'rb'))
change_json = change_res.json()
#changeId = "dbfe177b9df83a1f3dea0deeb5d19039"
changeId = change_json['data']['id']
statusUrl = "https://api.convertio.co/convert/"+str(putId)+"/status"
status = requests.get(url=statusUrl)
print(status.json())
status_json = status.json()
step = status_json['data']['step']
while step != 'finish':
    status = requests.get(url=statusUrl)
    print(status.json())
    status_json = status.json()
    step = status_json['data']['step']

outputUrl = status_json['data']['output']['url']
f = requests.get(url=outputUrl)
with open(bookName+".azw3", "wb") as code:
    code.write(f.content)