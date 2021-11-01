from urllib.request import urlopen
from urllib.parse import quote_plus
import random
import lxml.html
import xml.etree.ElementTree as ET


"""
Class cantain function for data manipulation
"""
class ParsingData:
    def __init__(self,url):
        self.url = url

    """
    parsing ebay page by item using proxycrawl.com
    """
    def parsing_by_proxycrawl(self):
        url = self.url
        print(url)
        #use county listi to make request from diff countryes
        country_list = ['US','JP','GB','FR','IN','NL','RU','UA']
        random_country = random.randint(0, len(country_list)-1)
        print(country_list[random_country])
        handler = urlopen(f'https://api.proxycrawl.com/?token=y8HmZ4hAheixlyoTvhN9Iw&country={country_list[random_country]}&url={url}').read()
        handler = str(handler, 'utf-8')
        print(handler)
        print(type(handler))
        doc = lxml.html.fromstring(handler)
        return doc