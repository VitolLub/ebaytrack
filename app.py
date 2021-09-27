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
PERMANENT_SESSION_LIFETIME = 1800

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
                    item_arr['storeName']=dictstr.get('searchResult').get('item')[i].get('storeInfo').get('storeName')
                    item_arr['storeURL']=dictstr.get('searchResult').get('item')[i].get('storeInfo').get('storeURL')
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

    def get_parsed_date(self,doc):
        arr = []
        for element in doc.xpath(
                '//table[@class="app-table__table"]//tr[@class="app-table__row"]/td[4]/div//text()'):


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
        item_id_array = ', '.join(item_id_array)
        return item_id_array
    def get_parsed_qt(self,doc):
        arr_quntiry = []
        for element in doc.xpath(
                '//table[@class="app-table__table"]//tr[@class="app-table__row"]/td[3]/div//text()'):
            try:
                if int(element) == True:
                    arr_quntiry.append(element)
            except:
                pass
        return arr_quntiry
    def collect_all_pages(self,pages_count, seller):
        full_arr = []
        item_id_arr = []
        for a in range(1, int(pages_count)):
            dictstr =''
            api = finding(siteid='EBAY-US', appid='LubomirV-devbattl-PRD-9b058513b-91c210eb', config_file=None)
            api.execute('findItemsIneBayStores', {
                'storeName': str(seller),
                'outputSelector': 'StoreInfo',
                'itemFilter': {
                    'name': 'MinPrice',
                    'value': 1,
                    'paramName': 'Currency',
                    'paramValue': 'USD',
                },
                'itemFilter': {
                    'name': 'MaxPrice',
                    'value': 2000,
                    'paramName': 'Currency',
                    'paramValue': 'USD',
                },
                'paginationInput': {
                    'entriesPerPage': 100,
                    'pageNumber': pages_count
                },
                'sortOrder': 'PricePlusShippingLowest'
            })
            dictstr = api.response_dict()
            for i in range(0, len(dictstr.get('searchResult').get('item'))):
                stat = dictstr.get('searchResult').get('item')[i].get('isMultiVariationListing')
                #if dictstr.get('searchResult').get('item')[i].get('itemId') not in item_id_arr:
                item_arr = {}
                item_arr['itemId'] =  dictstr.get('searchResult').get('item')[i].get('itemId') or ''
                item_arr['title'] = dictstr.get('searchResult').get('item')[i].get('title') or ''
                item_arr['globalId'] = dictstr.get('searchResult').get('item')[i].get('globalId') or ''
                item_arr['galleryURL'] = dictstr.get('searchResult').get('item')[i].get('galleryURL') or ''
                item_arr['viewItemURL'] = dictstr.get('searchResult').get('item')[i].get('viewItemURL') or ''
                item_arr['storeName'] = dictstr.get('searchResult').get('item')[i].get('storeInfo').get('storeName') or ''
                item_arr['storeURL'] = dictstr.get('searchResult').get('item')[i].get('storeInfo').get('storeURL') or ''
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
            api.execute('findItemsIneBayStores', {
                'storeName': seller,
                'outputSelector': 'StoreInfo',
                'itemFilter': {
                    'name': 'MinPrice',
                    'value': 1,
                    'paramName': 'Currency',
                    'paramValue': 'USD',
                },
                'itemFilter': {
                    'name': 'MaxPrice',
                    'value': 2000,
                    'paramName': 'Currency',
                    'paramValue': 'USD',
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

            if ack=="Success":
                item_id_list = self.collect_all_pages(totalPages, seller)
                status = self.save_seller_date(seller)


                pool = Pool(cpu_count())
                for item_id in item_id_list:
                    proxy = self.get_proxy()
                    pool.apply_async(save_item_quantity, (item_id, seller, proxy))
                return True
            else:
                return False
            return True
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
        api.execute('findItemsIneBayStores', {
            'storeName': seller,
            'outputSelector': 'StoreInfo',
            'itemFilter': {
                'name': 'MinPrice',
                'value': 1,
                'paramName': 'Currency',
                'paramValue': 'USD',
            },
            'itemFilter': {
                'name': 'MaxPrice',
                'value': 2000,
                'paramName': 'Currency',
                'paramValue': 'USD',
            },
            'paginationInput': {
                'entriesPerPage': 100,
                'pageNumber': 1
            },
            'sortOrder': 'PricePlusShippingLowest'
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
            qt_res['date'] = all_date
            qt_res['quantity'] = all_qt
            qt_res['qt_30'] = self.get_selling_qt_day_by_day(seller, s.get('itemId'), 30)
            qt_res['qr_7'] = self.get_selling_qt_day_by_day(seller, s.get('itemId'), 7)
            qt_arr.append(qt_res)
            item_res['qt_res'] = qt_arr
            item_arr.append(item_res)
        return item_arr
    def seller_date(self,seller):
        collection = db['items_data']
        item_date = collection.find({'storeName': seller})
        itemId_arr = []
        for a in item_date:
            itemId_arr.append(a.get('itemId'))
        return itemId_arr

labels = [
    'JAN', 'FEB', 'MAR', 'APR',
    'MAY', 'JUN', 'JUL', 'AUG',
    'SEP', 'OCT', 'NOV', 'DEC'
]

values = [
    967.67, 1190.89, 1079.75, 1349.19,
    2328.91, 2504.28, 2873.83, 4764.87,
    4349.29, 6458.30, 9907, 16297
]

colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]

@app.route('/bar')
def bar():
    bar_labels=labels
    bar_values=values
    return render_template('bar.html', title='Bitcoin Monthly Price in USD', max=17000, labels=bar_labels, values=bar_values)

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
        #check if seller availabel on ebay
        if seller_available==False:
            res = a.check_seller_on_ebay(seller)
            if res=='Failure':
                message = 'This seller don\'t find or have some problem with request '
                return render_template('index.html',message=message)
            if res=="Success":
                status = a.get_seller_data(seller, 1)
                if status==True:
                    item_id_array = a.item_id_array(seller)
                return render_template('index.html', item_id_array=item_id_array,seller_name_str=seller, seller_name='')
        # if selelr available in local database
        if seller_available==True:
            item_id_array = a.item_id_array(seller)
            for a in item_id_array:
                print(a)
            return render_template('index.html', item_id_array=item_id_array,seller_name_str=seller, seller_name='')
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
    url = "https://www.ebay.com/bin/purchaseHistory?item=" + item_id_list
    ip_addresses = proxy
    proxy_index = random.randint(0, len(ip_addresses) - 1)
    proxy = {"http": ip_addresses[proxy_index]}
    r = requests.get(url, proxies=proxy)
    text = r.content
    print(item_id_list)
    doc = lxml.html.fromstring(r.content)

    collection = db['items_quantity']
    #get parsed selling quantity
    a = Logic(db)
    arr_quntiry = a.get_parsed_qt(doc)

    arr = a.get_parsed_date(doc)
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
@app.route('/test1',methods=['GET','POST'])
def test1():
    a = Logic(db)

    collection = db['items_data']
    items_quantity_collection = db['items_quantity']

    if request.method=="POST":
        seller = request.form.get('seller')
        item_ids = request.form.get('page_count')
        item_ids = item_ids.split(", ")
        print('First data')
        print(item_ids)
        #remove empty space in value
        item_date = collection.find({'storeName': seller, "itemId": {"$in": item_ids}})
        seller_date = a.collect_all_seller_data(seller, item_date, items_quantity_collection)
        return json.dumps(seller_date)
@app.route('/<name>')
def name(name):


    return "Hellp"+name
if __name__=='_main_':
    app.secret_key = SECRET_KEY
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)