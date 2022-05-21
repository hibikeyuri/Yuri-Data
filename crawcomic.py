from datetime import datetime, timezone, timedelta
import json
from multiprocessing import connection
from operator import iconcat
import re
import os.path
import pymysql.cursors
from config import *
import pprint


data = [] #csv資料讀取至此
genre = set()
author = []

def main():
    data = []
    #傳入json array檔案，經由load後每個元素為dict tpye
    with open('yuri_raw_plus.json') as f:
        data = json.load(f)
    
    connection = connect()
    
    drop_create_tables(connection.cursor(), TABLES)

    #print(check_table(connection.cursor(), 'Yuri'))
    for d in data:
        print_debug_data(d)

        sql_insert = "INSERT INTO `Yuri`(`name`, `author`, `yuri_status`) \
            VALUES(%s, %s, %s)"
        
        with connection.cursor() as cursor:
            cursor.execute(sql_insert, (d["title"], d["author"], d["yuri status"]))
            print("INSERT OK!")
    
        connection.commit()

    connection.close()

def handle_data():
    different_publisher_data = []
    different_label = []

    with open('yuri_raw_plus.json') as f:
        data = json.load(f)

    date_rex = re.compile(r'(\d\d\d\d/\d(\d)?/\d(\d)?)')

    cnt = 0
    for ind, d in enumerate(data[:]):
        #print_debug_data(d)

        #json中的introduction欄位處理
        #擷取發售日
        #擷取出版社
        #擷取揭載誌
        #擷取label
        exp = d["introduction"][1]
        # 発売日
        date_search = date_rex.search(exp)
        if date_search:
            cnt += 1
            #print(date_search.group())
            #print(cnt)
        else:
            for intro in d["introduction"]:
                if intro.startswith('発売日'):
                    data_search = date_rex.search(intro)
                    #print(data_search.group())
        
        # 出版社
        publisher_rex = re.compile(r'(出版社：)(\t)?(\w+)(\n)?')
        publisher_rex2 = re.compile(r'(出版：)(\t)?(\w+)(\n)?')
        publisher_rex3 = re.compile(r'(出版社\(旧版\)：)(\t)?(\w+)(\n)?')

        publisher_search = publisher_rex.search(exp)
        
        if publisher_search:
            #print(publisher_search.groups())
            pass
        elif publisher_rex2.search(exp):
            temp = publisher_rex2.search(exp)
            #print(d["title"])
            #print(temp.groups())
        elif publisher_rex3.search(exp):
            temp = publisher_rex3.search(exp)
            #print(d["title"])
            #print(temp.groups())
            different_publisher_data.append(d)
        else:
            #print(d["title"])
            #print(d["introduction"])
            for intro in d["introduction"]:
                find = publisher_rex.search(intro)
                if find:
                    #print(find.groups())
                    pass
        
        # 掲載誌
        publish_magzine_rex = re.compile(r'掲載誌：(\w+)(\n)?')
        publish_magzine_rex2 = re.compile(r'発表：(\w+)(\n)?')

        publish_magzine_search = publish_magzine_rex.search(exp)
        
        if publish_magzine_search:
            pass
            #print(publish_magzine_search.groups())
        elif publish_magzine_rex2.search(exp):
            temp = publish_magzine_rex2.search(exp)
            #print(temp.groups())
        else:
            #print(d["title"])
            pass

        # レーベル
        label_rex = re.compile(r'レーベル：(\w+)(\n)?')
        label_rex2 = re.compile(r'レーベル(旧版)：(\w+)(\n)?')

        publish_label_search = label_rex.search(exp)
        if publish_label_search:
            pass
            #print(publish_label_search.groups())
        elif label_rex2.search(exp):
            temp = label_rex2.search(exp)
            #print(temp.groups())
        else:
            #print(d["title"])
            pass

def check_special_case():
    with open('yuri_raw_plus.json') as f:
        data = json.load(f)
    
    for d in data:
        if len(d["introduction"]) > 3:
            print(d["title"])


if __name__ == '__main__':
    #main()
    #handle_data()
    check_special_case()
    
# 出版
# 出版社(旧版)
# (新装版)
# レーベル(旧版)
# (新装版)
