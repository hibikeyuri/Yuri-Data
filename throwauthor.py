from config import *

def main():
    connection = connect()

    #drop_create_tables(connection.cursor(), TABLES)
    
    AUTHOR = get_author_form_data(FILENAME)

    sql = "INSERT INTO {}(`name`) VALUES(%s)"
    sql = sql.format(TABLE_AUTHOR)
    with connection.cursor() as cursor:
        for aut in AUTHOR:
            cursor.execute(sql, (aut))
            print("{} INSET complete!".format(aut))
            
        connection.commit()

    connection.close()


if __name__ == '__main__':
    main()