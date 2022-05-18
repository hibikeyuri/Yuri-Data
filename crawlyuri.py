import json
import string
#import secrets
#import string
import requests
import re
from bs4 import BeautifulSoup
from config import *


temp_slice = slice(5, 6)
temp_yuri_raw_data = []


def bs4_raw_data(url, *args, **kwargs):
    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'html.parser')
    sections = soup.find_all(*args, **kwargs)

    return soup, sections


def handle_yuri(url):
    #處理百合漫畫資料庫
    temp_comic = {}
    soup, sections = bs4_raw_data(url, 'section', class_='post')
    for index, section in enumerate(sections):
        print("Proccessing {}...".format(index))
        comicpage = section.find('a').get('href')
        print('comic page: ' + comicpage)
        smallcover = section.find('img').get('src')
        print('small cover url: ' + smallcover)
        #title
        title = section.find('span').text
        print('comic title: ' + title)
        #genre
        genres = section.find_all('a', {"rel":"category tag"})
        genres_list = []
        for genre in genres:
            print('genre: ' + genre.text)
            genres_list.append(genre.text)
        
 
        #處理每個百合漫畫的資料
        soup, sections = bs4_raw_data(comicpage, 'section')
        tankoubons = []
        tankoubons_img_urls = []
        maincover = sections[0].find('div', class_='syoseki-page1')
        maincover = maincover.find('img').get('src')
        print('maincover url: ' + maincover)
        author = sections[0].find('span', class_="futo")
        author = author.text
        print('author: ' + author)
        introductions =  [ele.text for ele in sections[0].select('p span')]
        print('comic introduction: ', introductions)
        yuri_status = sections[0].find_all('span', class_="futo")[1].text
        print('yuri status: ',  yuri_status)
        if soup.find_all('table'):
            tankoubons = [ele.get('href') for ele in soup.find_all('table')[0].find_all('a')]
            print('tankoubons: ', tankoubons)
            tankoubons_img_urls = [ele.get('src') for ele in soup.find('table').find_all('img')]
            print('tankoubons_img_urls: ', tankoubons_img_urls)
        else:
            tankoubons.clear()
            tankoubons_img_urls.clear()
            print('tankoubons: ', tankoubons)
            print('tankoubons_img_urls: ', tankoubons_img_urls)

        #將原始的百合漫畫資料存成json檔案
        temp_comic["title"] = title
        temp_comic["small cover"] = smallcover
        temp_comic["main cover"] = maincover
        temp_comic["author"] = author
        temp_comic["yuri status"] = yuri_status
        temp_comic["introduction"] = introductions
        temp_comic["genre"] = genres_list
        temp_comic["comic page"] = comicpage
        temp_comic["tankoubons"] = tankoubons
        temp_comic["tankoubons urls"] = tankoubons_img_urls
        print(temp_comic)
        temp_yuri_raw_data.append(temp_comic.copy())
        print(temp_yuri_raw_data)
    
    temp = open('yuri2.json', "w")
    temp.write(json.dumps(temp_yuri_raw_data, ensure_ascii=False))
    temp.close()


handle_yuri(YURI_URL)


# lucky = data[M-1]
# data.pop(M-1)
# ind = len(data) % M
# print(ind)
# if ind == 0:
#     print(data[M-1+1])
# else:
#     print(data[M-1+2])

