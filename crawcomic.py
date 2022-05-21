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

#throw Yuri to table
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

    for ind, d in enumerate(data[:]):
        #print_debug_data(d)

        #json中的introduction欄位處理
        publishinfo = d["introduction"][1]

        print('-----{}-----'.format(ind + 1))

        # 発売日
        date_search = 0
        if date_rex.search(publishinfo):
            data_search = date_rex.search(publishinfo)
            print(data_search.groups())
        else:
            #for special case, need to revise
            for intro in d["introduction"]:
                if intro.startswith('発売日'):
                    data_search = date_rex.search(intro)
                    #print(data_search.group())
        
        # 出版社
        publisher_rex = re.compile(r'(出版社：)(\t)?(\w+)(\n)?')
        publisher_rex2 = re.compile(r'(出版：)(\t)?(\w+)(\n)?')
        publisher_rex3 = re.compile(r'(出版社\(旧版\)：)(\t)?(\w+)(\n)?')

        publisher_search  = 0
        if publisher_rex.search(publishinfo):
            publisher_search = publisher_rex.search(publishinfo)
            print(publisher_search.groups())
        elif publisher_rex2.search(publishinfo):
            publisher_search = publisher_rex2.search(publishinfo)
            print(publisher_search.groups())
        elif publisher_rex3.search(publishinfo):
            publisher_search = publisher_rex3.search(publishinfo)
            print(publisher_search.groups())
            different_publisher_data.append(d)
        else:
            #print(d["title"])
            #print(d["introduction"])
            for intro in d["introduction"]:
                find = publisher_rex.search(intro)
                if find:
                    #print(find.groups())
                    pass
        
        # 掲載誌/発表
        publish_magzine_rex = re.compile(r'掲載誌：(\w+)(\n)?')
        publish_magzine_rex2 = re.compile(r'発表：(\w+)(\n)?')

        publish_magzine_search = 0 
        if publish_magzine_rex.search(publishinfo):
            publish_magzine_search = publish_magzine_rex.search(publishinfo)
            print(publish_magzine_search.groups())
        elif publish_magzine_rex2.search(publishinfo):
            publish_magzine_search = publish_magzine_rex2.search(publishinfo)
            print(publish_magzine_search.groups())            
        else:
            pass

        # レーベル
        label_rex = re.compile(r'レーベル：(\w+)(\n)?')
        label_rex2 = re.compile(r'レーベル(旧版)：(\w+)(\n)?')

        publish_label_search = 0
        if label_rex.search(publishinfo):
            publish_label_search = label_rex.search(publishinfo)
            print(publish_label_search.groups())
        elif label_rex2.search(publishinfo):
            publish_label_search = label_rex2.search(publishinfo)
            print(publish_label_search.groups())
        else:
            pass
        

if __name__ == '__main__':
    #main()
    handle_data()

# 出版
# 出版社(旧版)
# (新装版)
# レーベル(旧版)
# (新装版)
