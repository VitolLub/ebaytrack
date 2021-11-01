print('Hello ')

import requests
from bs4 import BeautifulSoup as soup
import json

url = "https://aliexpress.ru/item/1005001999800710.html?spm=a2g0o.productlist.0.0.1e993178FMvmFE&algo_pvid=ccb3dbae-7e5b-44f5-a8de-4c4b624d098f&algo_exp_id=ccb3dbae-7e5b-44f5-a8de-4c4b624d098f-2&pdp_ext_f=%7B%22sku_id%22%3A%2212000018368782106%22%7D"
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
title = res.find("title")
#print(response.content)
# full_script_data = res.find_all("script")
# for full_script in full_script_data:
#     res = full_script.getText()
#     if res.find('window.runParams')>0:
#         # print("----- cript -----")
#         # y = json.loads(res)
#         print(res)


print('__AER_DATA__')
full_script_data = res.find("script", {'id': '__AER_DATA__'})
res = full_script_data.getText()
print(res)