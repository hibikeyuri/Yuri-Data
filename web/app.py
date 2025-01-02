from csv import excel
import os, sys
from datetime import datetime, timezone, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask import render_template, request, url_for, abort
from flask.json import dumps

from config import *


app = Flask(__name__)
app.secret_key = "nozomizore_is_the_best"
app.jinja_env.variable_start_string = '{['
app.jinja_env.variable_end_string = ']}'

def get_yuris_filters():
    filters = {}

    #載體
    filters['carrier'] = {
        'label': '載體',
        'options': [{'id': 0, 'name': '漫画'}, {'id': 1, 'name': '小説'}],
        'type': ''
    }

    #種類
    genres = get_genres()
    filters['genre'] = {
        'label': '種類',
        'options': genres,
        'type': ''
    }

    #出版社
    publishers = get_publishers()
    filters['publisher'] = {
        'label': '出版社',
        'options': publishers,
        'type': ''
    }  

    #工口
    filters['r18'] = {
        'label': 'エロ',
        'options': [{'id': 0, 'name': '正常向'}, {'id': 1, 'name': 'エロ'}],
        'type': ''
    }

    #發售日年代
    years = get_publish_times()
    filters['year'] = {
        'label': '發售日年代',
        'options': years,
        'type': ''
    }

    return filters

def get_yuris():
    connection = connect()
    with connection.cursor() as cursor:
        sql_select_from_yuri= 'SELECT * FROM {}'.format(TABLE_YURI)
        cursor.execute(sql_select_from_yuri)

        datas = cursor.fetchall()
        res = []

        sql_select_genre = 'SELECT `name` FROM {} as t1, {} as t2 WHERE (YID=%s) AND (t1.GID=t2.id)'.format(TABLE_YURITOGENRE, TABLE_GENRE)


        for dbs in datas:
            genre = []

            #獲取作品種類
            cursor.execute(sql_select_genre, (dbs['id']))
            genre_sql_data = cursor.fetchall()

            for gen in genre_sql_data:
                genre.append(gen['name'])
            
            if(dbs['publish_time'] is None):
                year = 0
            else:
                year = dbs['publish_time'].year

            if(dbs['ero']):
                r18 = 'エロ'
            else:
                r18 = '正常向'

            res.append({
                'id': dbs['id'],
                'name': dbs['name'],
                'author': dbs['author'],
                'publisher': dbs['publisher'],
                'carrier': dbs['carrier'],
                'ero': dbs['ero'],
                'icon': dbs['small_img_url'],
                'publish_time': dbs['publish_time'],
                'genre': genre,
                'year': str(year),
                'r18': r18
            })

        return res

def get_yuri_info(id):
    connection = connect()
    sql_select_from_yuri_id = 'SELECT * FROM {} WHERE id=%s'.format(TABLE_YURI)
    sql_select_genre = 'SELECT `name` FROM {} as t1, {} as t2 WHERE (YID=%s) AND (t1.GID=t2.id)'.format(TABLE_YURITOGENRE, TABLE_GENRE)
    sql_select_author = 'SELECT `name` FROM {} as t1, {} as t2 WHERE (YID=%s) AND (t1.AID=t2.id)'.format(TABLE_YURITOAUTHOR, TABLE_AUTHOR)
    sql_select_from_buyurl_id = 'SELECT `buy_url` FROM {} WHERE YID=%s'.format(TABLE_BUYURL)
    sql_select_from_tankoubon_id = 'SELECT `img_url` FROM {} WHERE YID=%s'.format(TABLE_TANKOUBON)

    genre = []
    author = []
    buyurl = []
    tankoubon = []
    publisher = []
    moreinfo = {}

    with connection.cursor() as cursor:
        cursor.execute(sql_select_from_yuri_id, (id))
        info = cursor.fetchall()
        if not info:
            raise KeyError
        else:
            info = info[0]
        
        #獲取作品種類
        cursor.execute(sql_select_genre, (id))
        data = cursor.fetchall()
        for d in data:
            genre.append(d['name'])
        
        #獲取作者
        cursor.execute(sql_select_author, (id))
        data = cursor.fetchall()
        for d in data:
            author.append(d['name'])
        
        #獲取購買連結
        cursor.execute(sql_select_from_buyurl_id, (id))
        data = cursor.fetchall()
        for d in data:
            buyurl.append(d['buy_url'])
        
        #獲取其他單行本圖片
        cursor.execute(sql_select_from_tankoubon_id, (id))
        data = cursor.fetchall()
        for d in data:
            tankoubon.append(d['img_url'])
        
        moreinfo = {
            'genre': genre,
            'author': author,
            'buyurl': buyurl,
            'tankoubon': tankoubon,
        }

        connection.close()

        return info, moreinfo         

def get_author_sakuhin_info(id):
    connection = connect()
    #取得作者id後，從yuritoauthor獲取YID
    sql_select_from_yuri_id = 'SELECT * FROM {} WHERE id=%s'.format(TABLE_YURI)
    sql_select_yuritoauthor = 'SELECT `YID` FROM {} as t1 WHERE (t1.AID=%s)'.format(TABLE_YURITOAUTHOR)
    sql_select_from_author = 'SELECT `name` FROM {} WHERE id=%s'.format(TABLE_AUTHOR)
    
    info = []

    with connection.cursor() as cursor:

        cursor.execute(sql_select_from_author, (id))
        author_name = cursor.fetchall()[0]

        cursor.execute(sql_select_yuritoauthor, (id))
        info_temp = cursor.fetchall()
        for tmp in info_temp:
            cursor.execute(sql_select_from_yuri_id, (tmp['YID']))
            datas = cursor.fetchall()
            for dbs in datas:
                info.append({
                    'id': dbs['id'],
                    'name': dbs['name'],
                    'author': dbs['author'],
                    'publisher': dbs['publisher'],
                    'carrier': dbs['carrier'],
                    'ero': dbs['ero'],
                    'icon': dbs['small_img_url'],
                    'author_name': author_name['name']
            })

        connection.close()

        return info

def get_publisher_sakuhin_info(id):
    #取得出版社名稱
    publisher = get_publishers()[id - 1]
    print(publisher)
    connection = connect()
    sql_select_from_yuri_id = 'SELECT * FROM {} WHERE publisher=%s'.format(TABLE_YURI)
    
    info = []
    with connection.cursor() as cursor:
        cursor.execute(sql_select_from_yuri_id, (publisher['name']))
        datas = cursor.fetchall()
        for dbs in datas:
            info.append({
                'id': dbs['id'],
                'name': dbs['name'],
                'author': dbs['author'],
                'publisher': dbs['publisher'],
                'carrier': dbs['carrier'],
                'ero': dbs['ero'],
                'icon': dbs['small_img_url'],
                'publisher_name': publisher['name']
            })

        connection.close()
    return info

def get_genre_sakuhin_info(id):
    connection = connect()
    #取得作者id後，從yuritoauthor獲取YID -> 
    sql_select_from_yuri_id = 'SELECT * FROM {} WHERE id=%s'.format(TABLE_YURI)
    sql_select_yuritogenre = 'SELECT `YID` FROM {} as t1 WHERE (t1.GID=%s)'.format(TABLE_YURITOGENRE)
    sql_select_from_genre = 'SELECT `name` FROM {} WHERE id=%s'.format(TABLE_GENRE)

    info = []
    with connection.cursor() as cursor:

        cursor.execute(sql_select_from_genre, (id))
        genre_name = cursor.fetchall()[0]

        cursor.execute(sql_select_yuritogenre, (id))
        info_temp = cursor.fetchall()
        for tmp in info_temp:
            cursor.execute(sql_select_from_yuri_id, (tmp['YID']))
            datas = cursor.fetchall()
            for dbs in datas:
                info.append({
                    'id': dbs['id'],
                    'name': dbs['name'],
                    'author': dbs['author'],
                    'publisher': dbs['publisher'],
                    'carrier': dbs['carrier'],
                    'ero': dbs['ero'],
                    'icon': dbs['small_img_url'],
                    'genre_name': genre_name['name']
            })

        connection.close()

        return info

def get_authors():
    connection = connect()
    with connection.cursor() as cursor:
        sql_select_from_author= 'SELECT * FROM {}'.format(TABLE_AUTHOR)
        cursor.execute(sql_select_from_author)

        datas = cursor.fetchall()
        res = []
        for dbs in datas:
            res.append({
                'id': dbs['id'],
                'name': dbs['name']
            })
        connection.close()

        return res

def get_genres():
    connection = connect()
    with connection.cursor() as cursor:
        sql_select_from_genre= 'SELECT * FROM {}'.format(TABLE_GENRE)
        cursor.execute(sql_select_from_genre)

        datas = cursor.fetchall()
        res = []
        for dbs in datas:
            res.append({
                'id': dbs['id'],
                'name': dbs['name']
            })
        connection.close()

        return res

def get_publishers():
    connection = connect()
    with connection.cursor() as cursor:
        sql_select_from_yuri= 'SELECT `publisher` FROM {}'.format(TABLE_YURI)
        cursor.execute(sql_select_from_yuri)

        datas = cursor.fetchall()
        count = 0
        res = []
        publishers = dict()

        for dbs in datas:
            if dbs['publisher'] not in publishers.values():
                count += 1
                publishers.update({count : dbs['publisher']})
                res.append({
                    'id' : count,
                    'name': dbs['publisher']
                })
                
        connection.close()
        return res

def get_publish_times():
    connection = connect()
    with connection.cursor() as cursor:
        sql_select_from_yuri= 'SELECT `publish_time` FROM {}'.format(TABLE_YURI)
        cursor.execute(sql_select_from_yuri)

        datas = cursor.fetchall()
        count = 0
        res = []
        publishers = dict()

        for dbs in datas:
            if(dbs['publish_time'] is None):
                continue
            res.append(dbs['publish_time'].year)

        res = set(res)
        res = list(res)
        res.sort()
        
        res = [{'id': id + 1, 'name': year} for id, year in enumerate(res)]

        connection.close()

        return res

@app.route("/test")
def test():
    return render_template('index.html')

@app.route("/")
def home_page():
    return render_template("homepage.html")

@app.route("/yuris")
def yuri_home_page():
    yuris = get_yuris()
    filters = get_yuris_filters()
    return render_template('yuri.html', yuris=dumps(yuris), filters=dumps(filters))

@app.route("/yuris/<int:id>")
def yuri_page(id):
    try:
        info, moreinfo = get_yuri_info(id)
    except KeyError as err:
        abort(404)
    return render_template('sakuhin.html', title = info['name'], info=dumps(info), moreinfo=dumps(moreinfo))

@app.route("/authors")
def author_page():
    authors = get_authors()
    return render_template('author.html', authors=dumps(authors))

@app.route("/authors/<int:id>")
def author_sakuhin_page(id):
    try:
        info = get_author_sakuhin_info(id)
        print(info)
    except KeyError as err:
        abort(404)
    return render_template('authorsakuhin.html', title = info[0]['author_name'], auth_saku=dumps(info))

@app.route("/genres")
def genre_page():
    genres = get_genres()
    return render_template('genre.html', genres=dumps(genres))

@app.route("/genres/<int:id>")
def genre_sakuhin_page(id):
    try:
        info = get_genre_sakuhin_info(id)
        print(info)
    except KeyError as err:
        abort(404)
    return render_template('genresakuhin.html', title = info[0]['genre_name'], genre_saku=dumps(info))

@app.route("/publishers")
def publisher_page():
    publishers = get_publishers()
    return render_template('publisher.html', publishers=dumps(publishers))

@app.route("/publishers/<int:id>")
def publisher_sakuhin_page(id):
    try:
        info = get_publisher_sakuhin_info(id)
        print(info)
    except KeyError as err:
        abort(404)
    return render_template('publishersakuhin.html', title = info[0]['publisher_name'], pub_saku=dumps(info))

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)