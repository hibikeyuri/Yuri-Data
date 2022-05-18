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
    with open('yuri.json') as f:
        data = json.load(f)
    
    connection = connect()

    for d in data:
        print("title: {} author: {}".format(d["title"], d["author"]))
        print("introduction type: {}".format(type(d["introduction"])))
        print("introduction data: {}".format(len(d["introduction"])))
        print("yuri status: {}".format(d["yuri status"]))

        sql_insert = "INSERT INTO `comic`(`name`, `author`, `yuri status`) \
            VALUES(%s, %s, %s)"
        
        with connection.cursor() as cursor:
            cursor.execute(sql_insert, (d["title"], d["author"], d["yuri status"]))
            print("INSERT OK!")
    
        connection.commit()

    connection.close()


if __name__ == '__main__':
    main()