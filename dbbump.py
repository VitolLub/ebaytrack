from pymongo import MongoClient

client = MongoClient('mongodb+srv://vitol:vitol486070920@ebay.elcsu.mongodb.net/test?retryWrites=true&w=majority')
db = client['ebay']
collection = db['items_data'] #,'items_quantity','users
collection.delete_many({ })
collection = db['items_quantity'] #,'items_quantity','users
collection.delete_many({ })
collection = db['users'] #,'items_quantity','users
collection.delete_many({ })