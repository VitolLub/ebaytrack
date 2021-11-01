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

from scipy.sparse import data

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
            print(dictstr)
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
            print(totalPages)
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




@app.route('/download')
def downloadFile():
    #For windows you need to use drive name [ex: F:/Example.pdf]
    path = "C:\ebaytrack\GFG.csv"
    return send_file(path, as_attachment=True)

@app.route('/bar')
def bar():
    a = Logic(db)
    seller = 'roughriders12'
    items_quantity_collection = db['items_quantity']
    collection = db['items_data']
    item_date = collection.find({'storeName': seller})
    data_res = a.collect_all_seller_data(seller, item_date, items_quantity_collection)
    print(data_res)
    return render_template('bar.html', data_res=data_res)

@app.route('/',methods=['GET','POST'])
def index(seller=None):
    if request.method=='POST':

        seller = request.form['seller']
        # session['session_check_status'] = '0'
        # session['seller_name'] = 'redstarus'
        # session['seller_page_count'] = 10
        #marcetplace = request.form['marcetplace']
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
            print(f'item_id_array {data_res}')
            return render_template('index.html', data_res=data_res,seller_name_str=seller, seller_name='')
    else:
        return render_template('index.html', seller=seller)
def collect_all_seller_data(seller,item_date,items_quantity_collection):
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
        # print(item_res)
        res_qt = items_quantity_collection.find({'storeName': seller, 'itemId': s.get('itemId')})
        qt_arr = []
        all_date = []
        all_qt = []
        qt_res = {}
        for a in res_qt:
            all_date.append(a.get('date'))
            all_qt.append(a.get('quantity'))
        qt_res['date'] = all_date
        qt_res['quantity'] = all_qt
        a = Logic()
        qt_res['qt_30'] = a.get_selling_qt_day_by_day(seller, s.get('itemId'), 30)
        qt_res['qr_7'] = a.get_selling_qt_day_by_day(seller, s.get('itemId'), 7)
        qt_arr.append(qt_res)
        item_res['qt_res'] = qt_arr
        item_arr.append(item_res)
    return item_arr
def save_item_quantity(item_id_list,seller,proxy):
    print(item_id_list)
    url = "https://www.ebay.com/bin/purchaseHistory?item=" + item_id_list
    ip_addresses = proxy
    proxy_index = random.randint(0, len(ip_addresses) - 1)
    proxy = {"http": ip_addresses[proxy_index]}
    r = requests.get(url, proxies=proxy)
    print(f'get quantity satus code {r.status_code}')
    text = r.content
    print(f'get quantity satus code {r.status_code}')
    print(item_id_list)
    doc = lxml.html.fromstring(r.content)

    collection = db['items_quantity']
    #get parsed selling quantity
    a = Logic(db)
    print('start to parse quantity')
    arr_quntiry = a.get_parsed_qt(doc)

    arr = a.get_parsed_date(doc)
    print(item_id_list)
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