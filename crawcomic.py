from datetime import datetime, timezone, timedelta
import json
from multiprocessing import connection
import re
import os.path
import pymysql.cursors
from config import *
import pprint


data = [] #csv資料讀取至此

def main():
    data = []
    #傳入json array檔案，經由load後每個元素為dict tpye
    with open('yuri.json') as f:
        data = json.load(f)
    
    connection = connect()

    drop_table(connection.cursor(), TABLES)
    create_table(connection.cursor(), TABLES)

    print(check_table(connection.cursor(), 'comic'))
    for d in data:
        print_debug_data(d)

        sql_insert = "INSERT INTO `comic`(`name`, `author`, `yuri status`) \
            VALUES(%s, %s, %s)"
        
        with connection.cursor() as cursor:
            cursor.execute(sql_insert, (d["title"], d["author"], d["yuri status"]))
            print("INSERT OK!")
    
        connection.commit()

    connection.close()


if __name__ == '__main__':
    main()