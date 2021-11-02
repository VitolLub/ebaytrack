__author__      = "Lubomir Vitol"
__copyright__   = "Copyright 2021, Planet Earth"
"""
Class describe login and nethods to save data on veblite - https://newdropship.a2hosted.com/
# Consumer key: ck_34e7f3f1e99a0b0911283a82b61280bbe422d789
# Consumer secret: cs_e8838c981a6b91b89cbdfc8364152a569740e87d
"""
from woocommerce import API
from utility import Utility as utility


class SaveOnWebsite:

    def __init__(self,data):
        self.data = data
        self.all_translate_values = utility().read_translate_file()

    #website credential
    def credential(self):
        wcapi = API(
            url="https://newdropship.a2hosted.com/",
            consumer_key="ck_34e7f3f1e99a0b0911283a82b61280bbe422d789",
            consumer_secret="cs_e8838c981a6b91b89cbdfc8364152a569740e87d",
            timeout=40
        )

        return wcapi

    #test connet
    def connet_ping(self):


        wcapi = API(
            url="https://newdropship.a2hosted.com/",
            consumer_key="ck_34e7f3f1e99a0b0911283a82b61280bbe422d789",
            consumer_secret="cs_e8838c981a6b91b89cbdfc8364152a569740e87d",
            timeout=40
        )
        response = wcapi.get('products/categories/39617')
        return response.json()


    def create_category(self):

        wcapi = self.credential()

        batch_data = {
          'create': [
            {
              'id': 205002194,
              'name': "Dresses",
              'slug': 'dresses',
              'parent': 39617,
              'description': "Dresses",
              'display': 'default',
              'image': None,
              'menu_order': 0,
              'count': 0,
              '_links': {
                'self': [
                  {'href': 'http://localhost/wp-json/wc/v3/products/categories/205002194'}
                ],
               'collection': [
                 {'href': 'http://localhost/wp-json/wc/v3/products/categories'}
                ]
              }
            }
          ]
        }
        response = wcapi.post('products/categories/batch', batch_data)
        return response.json()

    #save data on website
    def save(self):
        # prepear video url
        if len(self.data[3])>0:
            video_embed = utility().fix_video_url(self.data[3][0])
        else:
            video_embed = ''

        attr_name_arr = []
        attrribute_value_full_arr = []
        for attr_count in self.data[6]:
            attr_name_arr.append(attr_count['name'])
            attr_dict = attr_count['values']

            attrribute_value_arr = []
            for attr_value in attr_dict:
                attributes_dict = {}
                attributes_dict['name']= attr_value['displayName']
                attributes_dict['displayName'] = attr_value['displayName']
                attributes_dict['id'] = attr_value['id']
                attrribute_value_arr.append(attributes_dict)
            attrribute_value_full_arr.append(attrribute_value_arr)



        #img array
        img_arr = []
        img_in_description = []
        for img in self.data[1]:
            img_dict = {}
            img_dict['src'] = img
            img_dict['alt'] = self.data[4]
            img_arr.append(img_dict)

            img_tag = f'<img src="{img_dict["src"]}" alt="{img_dict["alt"]}" ><br>'
            img_in_description.append(img_tag)


        # create oprion fro every attribute
        #look code below

        attr_option_arr = []

        for index, attr_option in enumerate(attr_name_arr):
            attr_option_dict = {}
            attr_option_dict['id'] = index + 1

            #translate att name

            attr_option_dict['name'] = utility().translate(attr_option,self.all_translate_values)
            attr_option_dict['visible'] = "True"
            attr_option_dict['variation'] = "True"

            val = []
            for a in attrribute_value_full_arr[index]:
                if len(a['name'])>2:
                    result = utility().translate(a['name'],self.all_translate_values)
                else:
                    result = a['name']
                val.append(result)
            attr_option_dict['options'] = val
            # #attrribute_value_full_arr[index]
            attr_option_arr.append(attr_option_dict)

        #add addition attributes
        for index, attr_atidion in enumerate(self.data[13]):
            attr_adition_dict = {}
            attr_adition_dict['name'] = attr_atidion['title']
            attr_adition_dict['visible'] = "True"
            attr_adition_dict['variation'] = "False"
            attr_adition_dict['options'] = [attr_atidion['value']]
            attr_option_arr.append(attr_adition_dict)

        wcapi = self.credential()


        product_data = {
            "name": self.data[4],
            "type": "variable",
            "sku":self.data[0],
            "regular_price": "",
            'price':"",

            "short_description": self.data[4],
            "description": video_embed+self.data[12],
            "categories": [
                {
                    "id": 39618
                }
            ],

            "images": img_arr,


            "attributes": attr_option_arr
        }
        response = wcapi.post('products', product_data)
        print('Data saving')
        return response.json()


    def load_attributes(self):
        wcapi = self.credential()
        response = wcapi.get('products/attributes')
        return response.json()


    def delete_product(self,id):
        wcapi = self.credential()
        response = wcapi.delete(f'products/{id}')
        return response.json()

    def add_attributes(self,id,res):
        res1 = res[6]
        res2 = res[7]

        attrribute_value_id_arr = self.extract_attrbute_nameAndId(res1)
        attrribute_skuPropIds_arr = self.extract_attrbute_skuPropIds(res2,attrribute_value_id_arr)



        try:
            #save attribute
            attributes_arr = []
            index=0
            for b in attrribute_skuPropIds_arr:
                attributes_arr.append(b)
                try:
                    if len(attributes_arr) >= 99:
                        self.save_all_attributes(attributes_arr,id)
                        attributes_arr = []
                        index=1
                    elif len(attributes_arr) == len(attrribute_skuPropIds_arr):
                        self.save_all_attributes(attributes_arr,id)
                        index=2
                    else:
                        index=3
                        attributes_arr = []
                except Exception as e:
                    print(f"During savind attributes upon error {e}")

            if index==3:
                self.save_all_attributes(attrribute_skuPropIds_arr,id)
        except Exception as e:
            print(f"During process in function add_attributes upon eroor {e}")




    def load_product_by_id(self,id):
        wcapi = self.credential()
        response = wcapi.get(f"products/{id}")
        return response.json()

    def extract_attrbute_nameAndId(self, res1):

        """
                code extract attr name and attribute ID
                follow data need to extract attributes value from skuPropIds
                Example format we receive from Aliexpress 'skuPropIds': '1254,200000990,201336100'
                """
        attr_name_arr = []
        attrribute_value_full_arr = []
        for attr_count in res1:
            attr_name_arr.append(attr_count['name'])
            attr_dict = attr_count['values']

            attrribute_value_arr = []
            for attr_value in attr_dict:
                attributes_dict = {}

                if len(attr_value['displayName'])>3:
                    attributes_dict['name'] = utility().translate(attr_value['displayName'],self.all_translate_values)
                else:
                    attributes_dict['name'] = attr_value['displayName']
                attributes_dict['id'] = attr_value['id']
                attrribute_value_arr.append(attributes_dict)
            attrribute_value_full_arr.append(attrribute_value_arr)

        return attrribute_value_full_arr

    #extract skuPropIds
    def extract_attrbute_skuPropIds(self, res2,attrribute_value_id_arr):
        """
        variation on aliexpress save like follow
        skuPropIds:1254,200003528,201336100 where
         1254 - color name
        200003528 - size name
        201336100 - country of shippig

        we need extracte data parse for atributes on our website
        """
        skuPropIds_addition_value_arr = []
        skuPropIds_arr = []
        for element in res2:
            #parse skuPropIds and send value for ID
            skuPropIds = element['skuPropIds']
            skuPropIds_arr = skuPropIds.split(",")
            attributes = self.receive_skuPropIds_data(skuPropIds_arr,attrribute_value_id_arr)


            #extract addition data of skuPropIds
            data_of_variation = {}
            data_of_variation['regular_price'] = element['amount']['value']
            data_of_variation['sale_price'] = element['activityAmount']['value']
            if int(element['availQuantity']) > 0:
                data_of_variation['stock_quantity'] = element['availQuantity']
                data_of_variation['stock_status'] = 'instock'
                data_of_variation['manage_stock'] = 'true'
            else:
                data_of_variation['stock_quantity'] = element['availQuantity']
                data_of_variation['stock_status'] = 'outofstock'
                data_of_variation['manage_stock'] = 'false'
                data_of_variation['status'] = 'private'
                data_of_variation['purchasable'] = 'false'


            data_of_variation['attributes'] = attributes
            skuPropIds_addition_value_arr.append(data_of_variation)
        return skuPropIds_addition_value_arr

    #parse skuPropIds
    def receive_skuPropIds_data(self, skuPropIds_arr,attrribute_value_id_arr):

        attr_id_value = []
        for skuid in skuPropIds_arr:
            for index, e in enumerate(attrribute_value_id_arr):

                for i, item in enumerate(e):
                    value_dict = {}
                    if item["id"] == skuid:
                        value_dict['id'] = index + 1
                        value_dict['option'] = item["name"]
                        attr_id_value.append(value_dict)

        return attr_id_value

    def save_all_attributes(self,attrribute_skuPropIds_arr,id):
        wcapi = self.credential()

        try:

            data = {
                "create": attrribute_skuPropIds_arr
            }
            wcapi.post(f"products/{id}/variations/batch", data).json()
        except Exception as e:
            return f"Function save_all_attributes upon error {e}"

