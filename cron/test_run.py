import requests
from bs4 import BeautifulSoup as soup

url = "https://www.aliexpress.ru/item/1005003393871894.html?c_tp=RUB&region=UK&b_locale=en_US"
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
a = {'aep_usuc_f':'region=AU&site=glo&b_locale=en_US&c_tp=USD'}
response = requests.get(url, timeout=20, headers=headers, cookies=a)
res = soup(response.content, features="lxml")
print(response.encoding )
print(response.headers)
print(response.cookies)
print(res.find("title"))

print('__AER_DATA__')
full_script_data = res.find("script", {'id': '__AER_DATA__'})
res = full_script_data.getText()
print(res)