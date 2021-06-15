from pymongo import MongoClient

import datefinder
client = MongoClient('mongodb+srv://vitol:vitol486070920@ebay.elcsu.mongodb.net/test?retryWrites=true&w=majority')
db = client['ebay']
collection = db['items_data'] #,'items_quantity','users
collection.remove({'storeName':'redstarus'})
collection = db['items_quantity'] #,'items_quantity','users
collection.remove({'storeName':'redstarus'})
collection = db['users'] #,'items_quantity','users
collection.remove({'seller':'redstarus'})