from config import *

def main():
    connection = connect()

    #drop_create_tables(connection.cursor(), TABLES)
    
    GENRE = get_genre_from_data(FILENAME)
    print(GENRE)
    sql = "INSERT INTO {}(`name`) VALUES(%s)"
    sql = sql.format(TABLE_GENRE)
    with connection.cursor() as cursor:
        for gen in GENRE:
            cursor.execute(sql, (gen))
            print("{} INSET complete!".format(gen))
        
        connection.commit()
    
    connection.close()


if __name__ == '__main__':
    main()