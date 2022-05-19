import json
import string
import random
import time
from turtle import delay
import requests
import re
from bs4 import BeautifulSoup
from config import *
from pprint import *


temp_slice = slice(5, 6)
temp_yuri_raw_data = []

delay_choices = [10, 20, 31, 6, 25, 21]


def bs4_raw_data(url, *args, **kwargs):
    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'html.parser')
    sections = soup.find_all(*args, **kwargs)

    return soup, sections

def yuri_url(yuri_url, end_page):
    yuri_urls = []
    temp_url = yuri_url.split('/1/')
    for i in range(0, end_page):
        yuri_urls.append(temp_url[0] + '/' + str(i+1) + '/' + temp_url[1])

    return yuri_urls

def handle_yuri(url):
    #處理百合漫畫資料庫
    temp_comic = {}
    soup, sections = bs4_raw_data(url, 'section', class_='post')

    delay_singles = [3, 7, 11, 18, 25, 30]
    #每一頁要爬的百合漫畫資料
    for index, section in enumerate(sections):
        print("Proccessing {}...".format(index + 1))
        delay_single = random.choice(delay_singles)
        print("delay single comic page {}s".format(delay_single))
        #time.sleep(delay_single)

        #每一頁先處理書名、icon url、每一個作品的頁面、種類
        comicpage = section.find('a').get('href')
        print('comic page: ' + comicpage)
        smallcover = section.find('img').get('src')
        print('small cover url: ' + smallcover)
        #title
        title = section.find('span').text
        if title == "NEW!":
            title = section.find('header', class_=re.compile('entry'))
            title = title.find('span').text
        print('comic title: ' + title)
        #genre
        genres = section.find_all('a', {"rel":"category tag"})
        genres_list = []
        for genre in genres:
            print('genre: ' + genre.text)
            genres_list.append(genre.text)
        
 
        #處理每個百合漫畫的資料
        #處理大圖url、作者、簡介(包含出版社、連載、類別)、百合狀態(?、其他單行本連結、其他單行本icon、購買連結
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

        #確認是否有無其他單行本
        if soup.find_all('table'):
            tankoubons = [ele.get('href') for ele in soup.find_all('table')[0].find_all('a')]
            #print('tankoubons: ', tankoubons)
            tankoubons_img_urls = [ele.get('src') for ele in soup.find('table').find_all('img')]
            #print('tankoubons_img_urls: ', tankoubons_img_urls)
        else:
            tankoubons.clear()
            tankoubons_img_urls.clear()
            #print('tankoubons: ', tankoubons)
            #print('tankoubons_img_urls: ', tankoubons_img_urls)
        
        #處理購買連結
        buy_links = []
        buy_link = sections[0].find('div', class_=re.compile('-page3'))
        for link in buy_link.find_all('p'):
            if link.find('a'):
                buy_links.append(link.find('a').get('href'))
        #print(buy_links)


        #將原始的百合漫畫資料存成python dict type
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
        temp_comic["buy urls"] = buy_links
        #pprint(temp_comic)
        temp_yuri_raw_data.append(temp_comic.copy())

    
YURI_URLS = yuri_url(YURI_URL, 23)

def main():
    ind = 0
    for yuri_url in YURI_URLS:
        ind += 1
        print("Proccessing {} page...".format(ind))
        delay = random.choice(delay_choices)
        print('delay for request url {} s'.format(delay))
        time.sleep(delay)
        handle_yuri(yuri_url)

    #將最終的資料轉換成json array
    f = open('yuri_raw_plus.json', "w")
    f.write(json.dumps(temp_yuri_raw_data, ensure_ascii=False))
    f.close()


if __name__ == '__main__':
    main()