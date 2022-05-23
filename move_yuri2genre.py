import argparse
from config import *


def get_yuri_rows():
    pass

def main():
    data = []
    errors = []

    with open('yuri_raw_plus.json') as f:
        data = json.load(f)
    
    connection = connect()

    for d in data:
        name = d["title"]
        genre = d["genre"]
        genres_id = []

        print(name)
        with connection.cursor() as cursor:
            cursor.execute(sql_select_from_yuri, (name))
            rows = cursor.fetchall()
            id = rows[0]['id']
            for gen in genre:
                cursor.execute(sql_select_from_genre, (gen))
                #獲取的是list中裝著dicts
                genre_id = cursor.fetchall()
                if not genre_id:
                    errors.append(genre + "Not Found in {} Table".format(TABLE_GENRE))
                    continue
                genre_id = genre_id[0]['id']
                genres_id.append(genre_id)

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