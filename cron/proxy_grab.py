
from datetime import *
from pymongo import MongoClient
from fp.fp import FreeProxy



import datefinder
client = MongoClient('mongodb+srv://vitol:vitol486070920@ebay.elcsu.mongodb.net/test?retryWrites=true&w=majority')
db = client['ebay']
#db connect
collection = db['proxy']
for a in range(0,5):
    try:
        #check proxy
        proxy = FreeProxy(country_id=['US', 'BR'], timeout=0.3, rand=True).get()
        #check proxy in db
        proxy  = proxy[7:]
        print(proxy)
        res = collection.count_documents({'proxy':proxy})
        now = datetime.today().strftime('%Y-%m-%d')
        if res==0:
            collection.insert_one({'proxy':proxy,'date':now})
    except:
        pass