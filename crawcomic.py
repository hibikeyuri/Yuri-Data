from datetime import datetime, timezone, timedelta
import json
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
    #紀錄可能會有出版社和單行本類型新舊版差異的作品
    different_publisher_data = []
    different_label = []
    special_case = []

    # connection = connect()    
    # drop_create_tables(connection.cursor(), TABLES)

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
        date = 0
        if date_rex.search(publishinfo):
            date_search = date_rex.search(publishinfo)
            date = date_search.groups()[0]
            #print(date_search.groups())
        else:
            pass
        
        # 出版社
        publisher_rex = re.compile(r'(出版社：)(\t)?(\w+)(\n)?')
        publisher_rex2 = re.compile(r'(出版：)(\t)?(\w+)(\n)?')
        publisher_rex3 = re.compile(r'(出版社\(旧版\)：)(\t)?(\w+)(\n)?')

        publisher_search  = 0
        publisher = 0
        if publisher_rex.search(publishinfo):
            publisher_search = publisher_rex.search(publishinfo)
            publisher = publisher_search.groups()[2]
            #print(publisher_search.groups())
        elif publisher_rex2.search(publishinfo):
            publisher_search = publisher_rex2.search(publishinfo)
            publisher = publisher_search.groups()[2]
            #print(publisher_search.groups())
        elif publisher_rex3.search(publishinfo):
            publisher_search = publisher_rex3.search(publishinfo)
            publisher = publisher_search.groups()[2]
            #print(publisher_search.groups())
            different_publisher_data.append(d["title"])
        else:
            pass
        
        # 掲載誌/発表
        publish_magzine_rex = re.compile(r'掲載誌：(\w+)(\n)?')
        publish_magzine_rex2 = re.compile(r'発表：(\w+)(\n)?')

        publish_magzine_search = 0 
        publish_magzine = 0
        if publish_magzine_rex.search(publishinfo):
            publish_magzine_search = publish_magzine_rex.search(publishinfo)
            publish_magzine = publish_magzine_search.groups()[0]
            #print(publish_magzine_search.groups())
        elif publish_magzine_rex2.search(publishinfo):
            publish_magzine_search = publish_magzine_rex2.search(publishinfo)
            publish_magzine = publish_magzine_search.groups()[0]
            #print(publish_magzine_search.groups())            
        else:
            pass

        # レーベル
        label_rex = re.compile(r'レーベル：(\w+)(\n)?')
        label_rex2 = re.compile(r'レーベル\(旧版\)：(\w+)(\n)?')

        publish_label_search = 0
        publish_label = 0
        if label_rex.search(publishinfo):
            publish_label_search = label_rex.search(publishinfo)
            publish_label = publish_label_search.groups()[0]
            #print(publish_label_search.groups())
        elif label_rex2.search(publishinfo):
            publish_label_search = label_rex2.search(publishinfo)
            publish_label = publish_label_search.groups()[0]
            different_label.append(d["title"])
            #print(publish_label_search.groups())
        else:
            pass
        
        #特判其他作品
        if len(d["introduction"]) > 3:
            special_case.append(d)
            #for special case
            for intro in d["introduction"]:
                if intro.startswith('発売日'):
                    date = date_rex.search(intro).groups()[0]

                if publisher_rex.search(intro):
                    publisher = publisher_rex.search(intro).groups()[2]
                
                if publish_magzine_rex.search(intro):
                    publish_magzine = publish_magzine_rex.search(intro).groups()[0]
                
                if label_rex.search(intro):
                    publish_label = label_rex.search(intro).groups()[0]


        #漫畫或小說
        carrier_rex = re.compile(r'【小説】')
        carrier = 0
        if carrier_rex.search(d["title"]):
            carrier = "小説"
        else:
            carrier = "漫画"

        #yuri status revised
        yuri_status = d["yuri status"]
        if not(( "✔ 百合承認済み" in d["yuri status"]) or ("✔ 百合公認" in d["yuri status"])):
            yuri_status = None

        #R18作品確認
        ero = 0
        if ("エロ" in d["genre"]) or ("成人向け" in d["genre"]):
            ero = 1
        
        #作者
        author = d["author"]
        author = author.split("著・")
        if author[0] != "":
            author = author[0]
        else:
            author = author[1].split(" / ")

        print(author)
        #print('{}, {}, {}, {}, {}, {}, {}, "エロ":{}, author:{}'.format(d["title"], date, publisher, publish_magzine, publish_label, carrier, yuri_status, ero, author))

        sql_insert = "INSERT INTO `Yuri`(`name`, `author`, `yuri_status`, `carrier`, `ero`) \
            VALUES(%s, %s, %s, %s, %s)"
        
        # with connection.cursor() as cursor:
        #     cursor.execute(sql_insert, (d["title"], d["author"], d["yuri status"], carrier, ero))
        #     print("INSERT OK!")
    
        # connection.commit()

    # connection.close()


    print(different_publisher_data)
    print(different_label)
    for ele in special_case:
        print(ele["title"])

if __name__ == '__main__':
    #main()
    handle_data()