__author__      = "Lubomir Vitol"
__copyright__   = "Copyright 2021, Planet Earth"
"""
File contain help functions
"""
import re
from googletrans import Translator
translator = Translator()
import json
import ast

class Utility:
    def __init__(self):
        pass
    #cut all no needed infor from img after parsing
    def cut_img(self,img_link):
        try:
            return img_link.replace('_50x50.jpg','')
        except Exception as e:
            return f"During imgage {img_link} upon error {e}"


    #load proxy from db or file
    def proxy_load(self):
        return ["51.79.220.22:8080", "51.79.220.50:8080", "185.49.69.134:8888", "206.253.164.198:80"]

    def load_subcategory_id(self):
        pass

    def translate(self,value, all_translate_values):
        if self.has_cyrillic(value)==True:
            return self.find_translate(all_translate_values,value)
        else:
            return value


    def has_cyrillic(self,text):
        return bool(re.search('[а-яА-Я]', text))


    def save_translate_file(self,dict):
        f = open("translate_file.txt", "w")
        f.write(str(dict))
        f.close()

    def read_translate_file(self):
        # reading the data from the file
        with open('translate_file.txt') as f:
            data = f.read()

        res = ast.literal_eval(data)
        return res

    def find_translate(self,translate_dic,value):
        translated_value = ''
        for key, val in translate_dic.items():
            if key==value.strip():
                translated_value = val
                break
        if len(translated_value) == 0:
            translated_value = translator.translate(value, dest='en').text
            translate_dic[value] = translated_value
            self.save_translate_file(translate_dic)
        return translated_value

    def fix_video_url(self, param):
        position = param.rfind('`')
        if position > 0:
            video_url = param[0:position]
        else:
            video_url = param

        video_embed = "[embed]" + str(video_url) + "[/embed]"
        return video_embed