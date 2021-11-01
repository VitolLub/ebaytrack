print('Hello ')

import requests
from bs4 import BeautifulSoup as soup

url = "https://www.aliexpress.com/item/1005003393871894.html"
session = requests.Session()
session.cookies.set('Host', 'aliexpress.com', domain='.aliexpress.com', path='/')
session.cookies.set('region', 'US', domain='.aliexpress.com', path='/')
headers = {
    "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
    "Accept-Language":"en-US,en;q=0.5",
    "Content-Language":"en"
}

proxyDict = {
              "http"  : "http://213.230.69.193:3128"
            }

response = requests.get(url, timeout=20, headers=headers, proxies=proxyDict)
res = soup(response.content, features="lxml")

print(res.find("title"))

#print(response.content)
full_script_data = res.find_all("script")
for full_script in full_script_data:
    try:
        script = full_script.getText()
        print(script[:500])
    except:
        pass