import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask import render_template, request, url_for, abort
from flask.json import dumps

from config import *


app = Flask(__name__)
app.secret_key = "nozomizore_is_the_best"
app.jinja_env.variable_start_string = '{['
app.jinja_env.variable_end_string = ']}'

def get_yuris():
    connection = connect()
    with connection.cursor() as cursor:
        sql_select_from_yuri= 'SELECT * FROM {}'.format(TABLE_YURI)
        cursor.execute(sql_select_from_yuri)

        datas = cursor.fetchall()
        res = []
        for dbs in datas:
            res.append({
                'id': dbs['id'],
                'name': dbs['name'],
                'author': dbs['author'],
                'publisher': dbs['publisher'],
                'carrier': dbs['carrier'],
                'ero': dbs['ero'],
                'icon': dbs['small_img_url']
            })
        connection.close()

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

@app.route("/test")
def test():
    return render_template('index.html')

@app.route("/")
def home_page():
    return render_template("homepage.html")

@app.route("/yuris")
def yuri_home_page():
    yuris = get_yuris()
    return render_template('yuri.html', yuris=dumps(yuris))

@app.route("/yuris/<int:id>")
def yuri_page(id):
    try:
        info, moreinfo = get_yuri_info(id)
    except KeyError as err:
        abort(404)
    return render_template('sukuhin.html', title = info['name'], info=dumps(info), moreinfo=dumps(moreinfo))

@app.route("/authors")
def author_page():
    authors = get_authors()
    return render_template('author.html', authors=dumps(authors))

@app.route("/genres")
def genre_page():
    genres = get_genres()
    return render_template('genre.html', genres=dumps(genres))

@app.route("/publishers")
def publisher_page():
    publishers = get_publishers()
    return render_template('publisher.html', publishers=dumps(publishers))

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


if __name__ == '__main__':
    app.debug = True
    app.run(host='localhost', port=5000)
