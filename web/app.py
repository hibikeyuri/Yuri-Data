from flask import Flask
from flask import render_template, request, url_for, abort
from flask.json import dumps
import pymysql.cursors
from datetime import datetime
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
                'ero': dbs['ero']
            })
        connection.close()

        return res

@app.route("/test")
def test():
    return render_template('index.html')

@app.route("/")
def yuri_home_page():
    yuris = get_yuris()
    return render_template('yuri.html', yuris=dumps(yuris))


if __name__ == '__main__':
    app.run(host='localhost', port=5000)
