import argparse
from enum import auto
from config import *


def get_yuri_rows():
    pass

def main():
    data = []
    errors = []
    author_set = get_author_form_data(FILENAME)
    with open(FILENAME) as f:
        data = json.load(f)
    
    connection = connect()
    
    for d in data:
        name = d["title"]
        author = d["author"]
        authors_id = []

        #print(name)
        with connection.cursor() as cursor:
            cursor.execute(sql_select_from_yuri, (name))
            rows = cursor.fetchall()
            id = rows[0]['id']
            for author_element in author_set:
                if author_element in author:
                    cursor.execute(sql_select_from_author, (author_element))
                    author_rows = cursor.fetchall()
                    author_id = author_rows[0]['id']
                    authors_id.append(author_id)
                    #print(author_element)

            for author_element_id in authors_id:
                cursor.execute(sql_insert_to_yuritoauthor, (id, author_element_id))
            
            print("INSERT {} OK!".format(TABLE_YURITOAUTHOR))

        print("YID: {}, author: {}. GID: {}".format(id, d["author"],authors_id))

        connection.commit()


    print(errors)
    connection.close()


if __name__ == '__main__':
    main()