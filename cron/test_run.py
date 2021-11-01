print('Hello ')

import requests
from bs4 import BeautifulSoup as soup

url = "https://www.aliexpress.com/item/1005003393871894.html?spm=a2g0o.productlist.0.0.64303178LJ4Z7q&algo_pvid=f8ab3789-1762-45cb-a355-5801d661ddf8&algo_exp_id=f8ab3789-1762-45cb-a355-5801d661ddf8-0&pdp_ext_f=%7B%22sku_id%22%3A%2212000025581510125%22%7D"
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
print(response.encoding )
print(response.headers)
print(response.cookies)
print(res.find("title"))

print(res.content)