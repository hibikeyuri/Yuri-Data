import argparse
from config import *


def get_yuri_rows():
    pass

def main():
    data = []
    errors = []
    author_set = get_author_form_data(FILENAME)
    with open('yuri_raw_plus.json') as f:
        data = json.load(f)
    
    connection = connect()

    for d in data:
        name = d["title"]
        author = d["author"]
        authors_id = []

        print(name)
        with connection.cursor() as cursor:
            cursor.execute(sql_select_from_yuri, (name))
            rows = cursor.fetchall()
            id = rows[0]['id']
            for author_element in author_set:
                if author_element in author:
                    pass  
            #將YID和GID丟到table
            for genid in genres_id:
                cursor.execute(sql_insert_to_yuritogenre, (id, genid))
            print("INSERT {} OK!".format(TABLE_YURITOGENRE))


        print("YID: {}, GID: {}".format(id, genres_id))

        connection.commit()

    print(errors)
    connection.close()


if __name__ == '__main__':
    main()