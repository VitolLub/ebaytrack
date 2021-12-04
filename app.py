import time
from flask import send_file
from flask import Flask, request,render_template,Response,jsonify,json, session
from pymongo import MongoClient
from ebaysdk.finding import Connection as finding
import datetime
from bs4 import BeautifulSoup
import datefinder
from dateutil.parser import *
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import lxml.html
from datetime import *
from multiprocessing import Pool,cpu_count
import os
 

app = Flask(__name__)
SESSION_TYPE = "redis"
PERMANENT_SESSION_LIFETIME = 3600

app.config.update(SECRET_KEY=os.urandom(24))
db = MongoClient('mongodb+srv://vitol:vitol486070920@ebay.elcsu.mongodb.net/test?retryWrites=true&w=majority')
db = db['ebay']

itemId = []
title=[]
globalId=[]
galleryURL=[]
viewItemURL=[]
storeNme = []
storeUrl=[]
money_type=[]
money_vlue=[]
SECRET_KEY = os.urandom(24)
class Logic:
    def __init__(self,db):
        self.db = db
    def update_save_seller_datedate(self,date):
        pass
    def save_rest_of_data(self):
        pass
    def get_proxy(self):
        collection = db['proxy']
        res = collection.find({})
        proxy_arr = []
        for a in res:
            proxy_arr.append(a.get('proxy'))
        return proxy_arr
    def save_seller_date(self,seller_name):
        collection = db['users']
        now = datetime.today()
        seller_name = seller_name
        seller_p = seller_name
        seller = {'seller': seller_p}
        result = collection.find(seller).count()
        if result == 0:
            seller_d = {}
            seller_d['seller'] = seller_p
            seller_d['last_update'] = now
            result = collection.insert(seller_d)
            return False
        else:
            seller_d = {}
            seller_d['seller'] = seller_p
            seller_d['last_update'] = now
            res = collection.replace_one({'seller': seller_p}, seller_d)

            return True
    def save_item_date(self,status,dictstr):

        collection = db['items_data']
        full_arr=[]
        item_id_arr=[]
        item_arr = {}
        totalPages = dictstr.get('paginationOutput').get('totalPages')

        totalEntries = dictstr.get('paginationOutput').get('totalEntries')

        for i in range(0,len(dictstr.get('searchResult').get('item'))): #len(dictstr.get('searchResult').get('item'))
            try:
                item_arr = {}
                stat = dictstr.get('searchResult').get('item')[i].get('isMultiVariationListing')
                if stat=='false':
                    item_arr['itemId']=dictstr.get('searchResult').get('item')[i].get('itemId')
                    item_arr['title']=dictstr.get('searchResult').get('item')[i].get('title')
                    item_arr['globalId']=dictstr.get('searchResult').get('item')[i].get('globalId')
                    item_arr['galleryURL']=dictstr.get('searchResult').get('item')[i].get('galleryURL')
                    item_arr['viewItemURL']=dictstr.get('searchResult').get('item')[i].get('viewItemURL')
                    item_arr['storeName']=dictstr.get('searchResult').get('item')[i].get('sellerInfo').get('sellerUserName')
                    item_arr['storeURL']=dictstr.get('searchResult').get('item')[i].get('sellerInfo').get('storeURL')
                    item_arr['_currencyId']=dictstr.get('searchResult').get('item')[i].get('sellingStatus').get('currentPrice').get('_currencyId')
                    item_arr['value']=dictstr.get('searchResult').get('item')[i].get('sellingStatus').get('currentPrice').get('value')
                    item_arr['active']=dictstr.get('searchResult').get('item')[i].get('sellingStatus').get('sellingState')
                    full_arr.append(item_arr)
                    item_id_arr.append(item_arr['itemId'])
            except:
                pass
        # if status==True:
        #     pass
        # if status==False:
        for a in full_arr:
            if collection.count_documents({'itemId': a.get('itemId')}) == 0:
                collection.insert_one(a)
        return item_id_arr

    def fin_in_string(self,string):
        input_string = string
        # a generator will be returned by the datefinder module. I'm typecasting it to a list. Please read the note of caution provided at the bottom.
        matches = list(datefinder.find_dates(input_string))

        if len(matches) > 0:
            # date returned will be a datetime.datetime object. here we are only using the first match.
            date = matches[0]
            if input_string.find("$") == -1:
                print('Date is correct')
                return False
        else:
            return True

    def is_date(string, fuzzy=False):
        """
        Return whether the string can be interpreted as a date.

        :param string: str, string to check for date
        :param fuzzy: bool, ignore unknown tokens in string if True
        """
        try:
            parse(string, fuzzy=fuzzy)
            return True

        except ValueError:
            return False

    def check_variation_status(self,doc,variation_index):
        variation_available = doc.xpath('//tr[@class="app-table__header-row"]/th[2]//text()')
        print(variation_available)
        if 'Variation' in variation_available:
            variation_index = 4
        else:
            variation_index = variation_index
        print(variation_index)
        return variation_index
    def get_parsed_date(self,doc):
        print('variation_index')
        # variation_index = self.check_variation_status(self,doc)
        variation_available = doc.xpath('//tr[@class="app-table__header-row"]/th[2]//text()')
        print(variation_available)
        if 'Variation' in variation_available:
            variation_index = 5
        else:
            variation_index = 4
        print(variation_index)
        arr = []
        aa = len(doc.xpath(f'//table[@class="app-table__table"]//td[{variation_index}]/div//text()'))
        print(f'check element qt - {aa}')
        for element in doc.xpath(f'//table[@class="app-table__table"]//td[{variation_index}]/div//text()'):


            date_time_str = element

            if self.fin_in_string(date_time_str) == False:
                try:
                    aa = parse(date_time_str, fuzzy_with_tokens=True)
                    date_check = aa[0].strftime('%Y-%m-%d')
                    arr.append(date_check)
                except:
                    pass
        return arr
    def item_id_array(self,seller):
        item_id_array = self.seller_date(seller)
        #conver arr to str
        item_id_array = ', '.join(item_id_array)
        return item_id_array
    def get_parsed_qt(self,doc):
        variation_available = doc.xpath('//tr[@class="app-table__header-row"]/th[2]//text()')
        print(variation_available)
        if 'Variation' in variation_available:
            variation_index = 4
        else:
            variation_index = 3
        print(variation_index)
        print(f'variation_index {variation_index}')
        arr_quntiry = []
        for element in doc.xpath(f'//table[@class="app-table__table"]//td[{variation_index}]/div//text()'):
            print(element)
            if int(element) == True:
                arr_quntiry.append(element)
        return arr_quntiry
    def collect_all_pages(self,pages_count, seller):
        full_arr = []
        item_id_arr = []
        if pages_count == 1:
            pages_count = 2
        print(f'pages_count {pages_count}')
        print(f'seller {seller}')
        for a in range(int(pages_count)):
            dictstr =''
            api = finding(siteid='EBAY-US', appid='LubomirV-devbattl-PRD-9b058513b-91c210eb', config_file=None)
            api.execute('findItemsAdvanced', {
                'outputSelector': 'SellerInfo',
                'itemFilter': {
                    'name': 'Seller',
                    'value': seller,
                },

                'paginationInput': {
                    'entriesPerPage': 100,
                    'pageNumber': pages_count
                },
                'sortOrder': 'PricePlusShippingLowest'
            })
            dictstr = api.response_dict()
            #print(dictstr)
            try:
                for i in range(0, len(dictstr.get('searchResult').get('item'))):
                    #check if same itemId isset in array.
                    #exclude dublicates
                    if dictstr.get('searchResult').get('item')[i].get('itemId') not in item_id_arr:
                        stat = dictstr.get('searchResult').get('item')[i].get('isMultiVariationListing')
                        #if dictstr.get('searchResult').get('item')[i].get('itemId') not in item_id_arr:
                        item_arr = {}
                        item_arr['itemId'] =  dictstr.get('searchResult').get('item')[i].get('itemId') or ''
                        item_arr['title'] = dictstr.get('searchResult').get('item')[i].get('title') or ''
                        item_arr['globalId'] = dictstr.get('searchResult').get('item')[i].get('globalId') or ''
                        item_arr['galleryURL'] = dictstr.get('searchResult').get('item')[i].get('galleryURL') or ''
                        item_arr['viewItemURL'] = dictstr.get('searchResult').get('item')[i].get('viewItemURL') or ''
                        item_arr['storeName'] = dictstr.get('searchResult').get('item')[i].get('sellerInfo').get('sellerUserName') or ''
                        item_arr['storeURL'] = dictstr.get('searchResult').get('item')[i].get('sellerInfo').get('storeURL') or ''
                        item_arr['_currencyId'] = dictstr.get('searchResult').get('item')[i].get('sellingStatus').get(
                            'currentPrice').get('_currencyId') or ''
                        item_arr['watchCount'] = dictstr.get('searchResult').get('item')[i].get('listingInfo').get(
                            'watchCount') or ''
                        item_arr['value'] = dictstr.get('searchResult').get('item')[i].get('sellingStatus').get(
                            'currentPrice').get(
                            'value') or ''
                        item_arr['active'] = dictstr.get('searchResult').get('item')[i].get('sellingStatus').get(
                            'sellingState') or ''
                        full_arr.append(item_arr)
                        item_id_arr.append(item_arr['itemId'])
            except:
                print('Some problem during GET')
        try:
            collection = db['items_data']
            save_res = collection.insert_many(full_arr)
            return item_id_arr
        except:
            return False
    def save_item_quantity(self,item_id_list,seller,proxy):
        url = "https://www.ebay.com/bin/purchaseHistory?item=" + item_id_list
        ip_addresses = proxy
        proxy_index = random.randint(0, len(ip_addresses) - 1)
        proxy = {"http": ip_addresses[proxy_index]}
        r = requests.get(url, proxies=proxy)
        text = r.content
        doc = lxml.html.fromstring(r.content)

        collection = db['items_quantity']
        #get parsed selling quantity
        print("get parsed selling quantity")
        arr_quntiry = self.get_parsed_qt(doc)

        arr = self.get_parsed_date(doc)
        acc = {}
        index = 0
        for da in arr:
            try:
                qts = arr_quntiry[index]
                try:
                    acc[arr[index]] += int(qts)
                except:
                    acc[arr[index]] = 0
                    acc[arr[index]] += int(qts)
                index += 1
            except:
                pass
        acc = sorted(acc.items(), key=lambda x: datetime.strptime(x[0], '%Y-%m-%d'), reverse=True)
        for key in acc:
            dd = {}
            dd['itemId'] = item_id_list
            dd['date'] = key[0]
            dd['quantity'] = key[1]
            dd['storeName'] = seller
            res = collection.count_documents({'itemId': itemId, 'date': key[0]})
            if res == 0:
                collection.insert_one(dd)
    def get_seller_data(self,seller,page):
        collection = db['users']
        seller_qt =0
        if seller_qt==0:
            api = finding(siteid='EBAY-US', appid='LubomirV-devbattl-PRD-9b058513b-91c210eb', config_file=None)
            api.execute('findItemsAdvanced', {
                'outputSelector': 'SellerInfo',
                'itemFilter': {
                    'name': 'Seller',
                    'value': seller,
                },

                'paginationInput': {
                    'entriesPerPage': 100,
                    'pageNumber': page
                },
                'sortOrder': 'PricePlusShippingLowest'
            })
            dictstr = api.response_dict()
            ack = dictstr.get('ack')
            totalPages = dictstr.get('paginationOutput').get('totalPages')
            # totalEntries = dictstr.get('paginationOutput').get('totalEntries')
            #print(totalPages)
            if ack=="Success":
                print(f'totalPages {totalPages}')
                item_id_list = self.collect_all_pages(totalPages, seller)
                status = self.save_seller_date(seller)
                print(f'Status {status}')
                print('item_id_list')
                print(f'item_id_list count {len(item_id_list)}')
                print(f'cpu count {cpu_count()}')
                pool = Pool(cpu_count())
                len_index = 0
                #remove dublicated
                item_id_list = set(item_id_list)
                print(f'item_id_list after remove dublicated {item_id_list}')
                for item_id in item_id_list:
                    proxy = self.get_proxy()
                    print(f'Start get quantity {proxy}')
                    res = pool.apply_async(save_item_quantity, (item_id, seller, proxy))
                    print(f'pool res {res}')
                res.wait()
                return True

            else:
                return False
    def get_selling_qt_day_by_day(self,seller,itemId,days):
        now = datetime.today().strftime('%Y-%m-%d')
        lst_7d = datetime.today() - timedelta(days=int(days))
        lst_7d = lst_7d.strftime('%Y-%m-%d')
        collection = db['items_quantity']
        # res = collection.find({'date': {'$gte': lst_7d, '$lt': now},'storeName':'redstarus','itemId':'313405796455'})#,'storeName':'redstarus','itemId':'313405796455'
        res = collection.aggregate(
            [{'$match': {'date': {'$gte': lst_7d, '$lt': now}, 'storeName': seller, 'itemId': itemId}}, {
                '$group': {
                    '_id': 'null',
                    'total': {
                        '$sum': '$quantity'
                    }
                }
            }])
        try:
            b = [a for a in res if a.get('total')]
            return b[0].get('total')
        except:
            return 0
    def check_seler_available(self,seller):
        collection = db['users']
        seller_qt = collection.count_documents({'seller': seller})
        if seller_qt > 0:
            return True
        else:
            return False

    def check_seller_on_ebay(self,seller):
        api = finding(siteid='EBAY-US', appid='LubomirV-devbattl-PRD-9b058513b-91c210eb', config_file=None)
        api.execute('findItemsAdvanced', {

            'outputSelector': 'SellerInfo',
            'itemFilter': {
                'name': 'Seller',
                'value': seller,
                'paramName': 'Currency',
                'paramValue': 'USD',
            },
            'paginationInput': {
                'entriesPerPage': 3
            }
        })
        dictstr = api.response_dict()
        ack = dictstr.get('ack')
        return ack

    def collect_all_seller_data(self,seller, item_date, items_quantity_collection):
        all_date = {}
        item_arr = []
        for s in item_date:  #
            item_res = {}
            item_res['itemId'] = s.get('itemId')
            item_res['title'] = s.get('title')
            item_res['globalId'] = s.get('globalId')
            item_res['galleryURL'] = s.get('galleryURL')
            item_res['viewItemURL'] = s.get('viewItemURL')
            item_res['storeName'] = s.get('storeName')
            item_res['storeURL'] = s.get('storeURL')
            item_res['_currencyId'] = s.get('_currencyId')
            item_res['value'] = s.get('value')
            item_res['active'] = s.get('active')
            res_qt = items_quantity_collection.find({'storeName': seller, 'itemId': s.get('itemId')})
            qt_arr = []
            all_date = []
            all_qt = []
            qt_res = {}
            for a in res_qt:
                all_date.append(a.get('date'))
                all_qt.append(a.get('quantity'))
            qt_res['date'] = ','.join([str(elem) for elem in all_date])
            qt_res['quantity'] = all_qt
            qt_res['qt_30'] = self.get_selling_qt_day_by_day(seller, s.get('itemId'), 30)
            qt_res['qr_7'] = self.get_selling_qt_day_by_day(seller, s.get('itemId'), 8)
            qt_arr.append(qt_res)
            item_res['qt_res'] = qt_arr
            item_arr.append(item_res)
        return item_arr
    def seller_date(self,seller):
        collection = db['items_data']
        item_date = collection.find({'storeName': seller})
        itemId_arr = []
        for a in item_date:
            if a.get('itemId') not in itemId_arr:
                itemId_arr.append(a.get('itemId'))
        return itemId_arr
    def get_all_datas_by_seller_name(self,seller):
        items_quantity_collection = db['items_quantity']
        collection = db['items_data']
        item_date = collection.find({'storeName': seller})
        data_res = self.collect_all_seller_data(seller, item_date, items_quantity_collection)
        return data_res

    # function to get all items UPC
    def get_all_items_upc(self,item_id):
        headers = {
            'Authorization': "Bearer v^1.1#i^1#r^0#I^3#p^1#f^0#t^H4sIAAAAAAAAAOVYbWwURRjutddC+VYRKkg8toABsnezu3fH3cJdOLjWnlx7LXcUi0jZj9nrcnu7y84c7Zkg5X6UGDTGKMSA2IamMX7wQ8UQMYDGLxKDYvwAQvyBGtSQ+Muo0Rjd3SvlWgkgvcQm3p/LvPPOO8/zzPvOzA7orald1tfU9+t0x6TKgV7QW+lwUFNBbU318hlVlfOqK0CJg2Ogd1Gvs1D1wyrEZRWdXQ+RrqkIunqyiopY2xgicobKahySEatyWYhYLLDJSHOcpd2A1Q0Na4KmEK5YNEQEKb8XBmjIgBUS74fAtKpXY6a0EGEaOcnPQS4YhAFG8Jv9COVgTEWYU3GIoAFNkRRNAiZFMawXsEzQTfnAJsLVDg0ka6rp4gZE2IbL2mONEqw3hsohBA1sBiHCsUhjMhGJRRtaUqs8JbHCwzokMYdzaHRrrSZCVzun5OCNp0G2N5vMCQJEiPCEizOMDspGroK5Dfi21AzwUYyfEaQAw3sZmiuLlI2akeXwjXFYFlkkJduVhSqWcf5mippq8NuggIdbLWaIWNRl/bXlOEWWZGiEiIY1kY5IaysRjud4LSsb7aQId/AcxgrZuj5KBnngC5iceTJICTQFID88UTHasMxjZlqrqaJsiYZcLRpeA03UcKw2TIk2plNCTRgRCVuISv18VzX0+jZZi1pcxRzuUq11hVlTCJfdvPkKjIzG2JD5HIYjEcZ22BKFCE7XZZEY22nn4nD69KAQ0YWxzno83d3d7m7GrRlpDw0A5XmoOZ4UumDWzJCerFXrRX/55gNI2aYiQHMkklmc100sPWaumgDUNBGmg2YOrhjWfTSs8FjrPwwlnD2jK6JcFSJAhgsEJHEF7feLAb4sm014OEk9Fg7Ic3kyyxkZiHWFEyApmHmWy0JDFlnGJ9FMQIKk6A9KpDcoSSTvE/0kJUEIIOR5IRj4PxXKraZ6EgoGxGXJ9bLleVrUkDeTXp/JbngwHlzekEgGlOZ010bY0pbsSMI2wHd4dDWf0mFb6Far4brk1yqyqUzKnL8cAli1Xj4RmjSEoTgueklB02GrpshCfmItMGOIrZyB80moKKZhXCQjuh4rz15dNnr/cpu4Pd7lO6P+o/PpuqyQlbITi5U1HpkBOF12WyeQW9CyHqvWNc68fljmThv1uHjL5s11QrE2SRbZymLxyum26brRDsFtQKTlDPO27U5YN7CUloGqeZ5hQ1MUaLRT467nbDaHOV6BE62wy5DgMjfBDlvKzwR8TCDABMfFS7CP0s6JtiWVYyt2PnCb12rP6I/8cIX9owqON0HB8VqlwwE8YDFVDxbWVG1wVk2bh2QM3TInuZGcVs1vVwO6MzCvc7JRWePonnt86ETJs8LAI6Bu5GGhtoqaWvLKAO691lNNzZw7naYoGjAU4wVMcBOov9brpOY4Z3ef3XYos/3KzLbBw0dkeHJwyqlEBkwfcXI4qiucBUfFXT8ONnx4FCiF/C+5d3K/n8Gn4rPPMUNPb+xbOLh53YL5u860Fk6cP/vZue9qvmRf+H7r7suXVn+627l98sunu5Yf+WMgUhe8eLCWOv95Ysp+b7zp6J17r5z7+tuWnavv54+tO7A4Omff60tXDn3T4n/8xT3J559lZyxa+JS8J32ysOSxAx8s2d90LDzr4XvilxruqG/eN39dtO7ItOThJc+ln/ziUv9vnYktjYfa6Lee6Dndsbn/4IXtKMVFooXKoY97hrZe+OqNPzvffuWjScaWvq2Tf4ou+HnmSzvf3Rsr3DdtcT4w6/LxGv+y/N3U5L1LL0pN721b6eifGqrr/+v9+k9OPfPolV0GePUw6Ggki8v3N5XeKbTwEQAA",
            'Content-Type': "application/json",
            'X-EBAY-C-MARKETPLACE-ID': "EBAY_US",
            'X-EBAY-C-ENDUSERCTX': "contextualLocation=country=<2_character_country_code>,zip=<zip_code>,affiliateCampaignId=<ePNCampaignId>"
        }

        url = f"https://api.ebay.com/buy/browse/v1/item/v1|{item_id}|0?fieldgroups=PRODUCT"
        content = requests.get(url, headers=headers)
        print(content.status_code)
        # print(content.content)

        # content to json convert
        res = json.loads(content.content)
        categoryId = res['categoryId']
        categoryPath =  res['categoryPath']
        mi = res['localizedAspects']
        upcmpn_arr = []
        for upc in mi:
            if upc['name'] == 'MPN' or upc['name'] == 'UPC':
                upcmpn_arr.append(upc['value'])

        self.save_upc_in_db(categoryId,categoryPath,upcmpn_arr,item_id)

    def save_upc_in_db(self, categoryId, categoryPath, upcmpn_arr,item_id):
        # save data in db
        # items_data collection by item_id
        collection = db['items_data']
        collection.update_one()








@app.route('/download')
def downloadFile():
    #For windows you need to use drive name [ex: F:/Example.pdf]
    path = "C:\ebaytrack\GFG.csv"
    return send_file(path, as_attachment=True)



@app.route('/',methods=['GET','POST'])
def index(seller=None):
    if request.method=='POST':

        seller = request.form['seller']
        a = Logic(db)
        #check if seller available i database
        seller_available = a.check_seler_available(seller)

        print(f'seller_available {seller_available}')
        if seller_available==False:
            # check if seller availabel on ebay
            res = a.check_seller_on_ebay(seller)
            print(f'check if seller availabel {res}')
            if res=='Failure':
                message = 'This seller don\'t find or have some problem with request '
                return render_template('index.html',message=message)
            if res=="Success":
                status = a.get_seller_data(seller, 1)
                print(f'receive sattus after save data {status}')
                if status==True:
                    #item_id_array = a.item_id_array(seller)
                    data_res = a.get_all_datas_by_seller_name(seller)
                    #print(f'item_id_array {item_id_array}')
                    #print(f'item_id_array {type(item_id_array)}')
                return render_template('index.html', data_res=data_res,seller_name_str=seller, seller_name='')
        # if selelr available in local database
        if seller_available==True:
            data_res = a.get_all_datas_by_seller_name(seller)
            #print(f'item_id_array {data_res}')
            return render_template('index.html', data_res=data_res,seller_name_str=seller, seller_name='')
    else:
        return render_template('index.html', seller=seller)


def save_item_quantity(item_id_list,seller,proxy):
    print(item_id_list)
    url = "https://www.ebay.com/bin/purchaseHistory?item=" + item_id_list
    ip_addresses = proxy
    proxy_index = random.randint(0, len(ip_addresses) - 1)
    proxy = {"http": ip_addresses[proxy_index]}


    session = requests.Session()
    session.cookies.set('Host', 'ebay.com', domain='.ebay.com', path='/')
    session.cookies.set('region', 'US', domain='.ebay.com', path='/')
    session.trust_env = False
    cookies = {'__gads': 'ID=da5d4f1570f068f6:T=1635764052:S=ALNI_MZwUAUC1QyiuWjdRbaOoQDWVElK9w',
               '_ssds': '2',
               '__ssuzjsr2': 'a9be0cd8e',
               '__uzma': 'e40aae7b-31a6-4f34-b72e-e24bfb9b9d65',
               '__uzmaj2': '370517f0-91f0-4159-b4b5-f651ecbb14b0',
               '__uzmb': '1635764004',
               '__uzmbj2': '1635764006',
               '__uzmc': '1687220296796',
               '__uzmcj2': '2493511865733',
               '__uzmd': '1638463023',
               '__uzmdj2': '1638463025',
               '__uzme': '7665',
               '__uzmf': '7f30008d06bd68-42ca-47bc-b4e8-84c4f0794d070e3c437cbe7c2b78202',
               'ak_bmsc': '304B903C0107B2FE2145BCBE1C9B6474~000000000000000000000000000000~YAAQlKwQArQy53B9AQAAaAH4ew3WDoPqXf+JK+v/WIvyEcd3l8cltIQ8VEQf8MNXr9FbGYK9yKWKMWxur3WxI7eFVOas4sgrlxSZxTmDjLJar8dOQ/rmEnHKDSuMTnT3qsGTRhw28o706WDW3fL+/FHQBGdd/cNnDyCNdHACBArXgLgfV3p5lfR27xowA/bn8R9yxAftKyWkfLQAMLL9NC33teUHcJQqr/dEnMUVbIKFja+vowur7InWz3SfPRSFLCkKT58xH0j7JBhgl5y7rDcBHC5LQosxDYzj5YQKxiKD3JKthYG3v66+ld6GP5QxTvK3zM0qxl7kM5fYxJL2FMR0jjilBMN9Cl+1PBVzbe9YuPawEISQXbOR8VplTecdG7JvLVKyGab4',
               'bm_sv': '6FE95053EE6E16CFF6148776EA285B6E~FVADS8sa/UEahNsjD2G5vuk29RdXJI7RD+DWWbRCWNJQI3N7XZ///kiqPwQ0zTckXJQAZqr0BRPqxPZnQqnV0VdGurDoMVJ9FGWWmhC712Um5UcQBPSoUgMcPE4y2PUj0E2GkAoQ8raM/5e8rrI4bv95Jj0OI4XOqBMw2XwtBfY=',
               'cid': 'Jsl3DFbotEHOAzN9%23428046651',
               'dp1': 'bu1p/dml0b2xsdWJvbWly656b6382^kms/in656b6382^pbf/%2300008000e00000818002000000638a3002^u1f/Lubomyr656b6382^tzo/1a461a90443^expt/0001635764019928627060f4^bl/US656b6382^',
               'ds1': 'ats/1638462468823',
               'ebay': '%5Ejs%3D1%5EsfLMD%3D0%5Esin%3Din%5Esbf%3D%23000004%5E',
               'nonsession': 'BAQAAAXw0ACieAAaAAAQADGOKJ4R2aXRvbGx1Ym9taXIACAAcYdCJgjE2Mzg0NjI0MzJ4MjY0OTkxNjIzNTYzeDB4Mk4AEAAMY4owAnZpdG9sbHVib21pcgAzAA5jijACMDcwMDItNDAwMixVU0EAQAAMY4owAnZpdG9sbHVib21pcgCaAA1hq5cEdml0b2xsdWJvbWlyZwCcADhjijACblkrc0haMlByQm1kajZ3Vm5ZK3NFWjJQckEyZGo2QUNrNEtpQ0ppSG9nMmRqNng5blkrc2VRPT0AnQAIY4owAjAwMDAwMDAwAMoAIGVrY4JkYjIxYmQwODE3YzBhYjk3ZDFiY2E0NmFmZmFkYzJmMQDLAAJhqQOKNjkBZAAHZWtjgiMwMDAwMGGzvkU2YoLZ2GDH5RGe22eyp1EjEQ**',
               'npii': 'btguid/db21bd0817c0ab97d1bca46affadc2f1656b6382^cguid/db21c19717c0a0a66e40e472fd14912e656b6382^',
               'ns1': 'BAQAAAXw0ACieAAaAAKUADWOKMAIxNjMwMzA4NTMxLzA7/QCnmmc7p4hnsZuKobl+0vqXLl8*',
               's': 'BAQAAAXw0ACieAAWAAAEADGGqRYR2aXRvbGx1Ym9taXIAAwABYapHszAADAAKYapHszE2MzAzMDg1MzEAPQAMYapHs3ZpdG9sbHVib21pcgCoAAFhqkWEMQDuAClhqkezMTQGaHR0cHM6Ly93d3cuZWJheS5jb20vdXNyL3ZpdG9sbHVib21pcgcA+AAgYapHs2RiMjFiZDA4MTdjMGFiOTdkMWJjYTQ2YWZmYWRjMmYxAUUACGOKMAI2MTYzM2Q4MwFlAANhqkezIzAy9Sp8/fKDbw+kdE/ei6swCIp5eOI*',
               'shs': 'BAQAAAX1o/biYAAaAAVUAD2OKJ4QyMDkxODQ4NDQxMDAyLDIiSRC1+F3gBUb56xEgqKrGTaZgwQ**',
               'sru': 'X',
               'JSESSIONID': 'B4894DD5EEBFE618BF21F20600BB9DC5'
               }
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.5",
        'referer': 'https://www.google.com/'
    }
    r = session.get(url, timeout=20, headers=headers, cookies=cookies, proxies=proxy)




    print(f'get quantity satus code {r.status_code}')
    print(f'get quantity satus code {r.status_code}')
    print(item_id_list)
    doc = lxml.html.fromstring(r.content)
    collection = db['items_quantity']
    #get parsed selling quantity
    a = Logic(db)
    print('start to parse quantity')
    arr_quntiry = a.get_parsed_qt(doc)

    arr = a.get_parsed_date(doc)
    #print(item_id_list)
    print('arr_quntiry + arr')
    print(arr)
    print(len(arr))
    print(arr_quntiry)
    print(len(arr_quntiry))
    acc = {}
    print('Start to count quantyt by date')
    index = 0
    for da in arr:
        try:
            print('Index' + str(index))
            print(da)
            print(arr[index])
            print(arr_quntiry[index])
            print('quntyt sell in ' + arr[index] + ' ' + arr_quntiry[index])
            print(arr_quntiry[index])
            qts = arr_quntiry[index]
            try:
                acc[arr[index]] += int(qts)
            except:
                acc[arr[index]] = 0
                acc[arr[index]] += int(qts)
            print(acc)
            index += 1
        except:
            pass
    print('acc')
    print(acc)
    print(len(acc))
    acc = sorted(acc.items(), key=lambda x: datetime.strptime(x[0], '%Y-%m-%d'), reverse=True)
    for key in acc:
        dd = {}
        dd['itemId'] = item_id_list
        dd['date'] = key[0]
        dd['quantity'] = key[1]
        dd['storeName'] = seller
        res = collection.count_documents({'itemId': item_id_list, 'date': key[0]})
        if res == 0:
            collection.insert_one(dd)
    print('save_item_quantity done')
    return True

@app.route('/<name>')
def name(name):

    return "Hellp"+name

if __name__=='_main_':
    app.secret_key = SECRET_KEY
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)