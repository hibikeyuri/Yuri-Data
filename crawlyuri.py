import json
import secrets
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
import html5lib

def  bs4_data_for_comic_page(url, *args, **kwargs):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    #section = soup.find_all('div', class_='entry-content')
    section = soup.find_all('section')
    maincover = section[0].find('div', class_='syoseki-page1')
    maincover = maincover.find('img').get('src')
    print(maincover)
    author = section[0].find('span',class_="futo")
    print(author.text)
    introduction =  section[0].select('p span')
    #print(section)
    for i, intro in enumerate(introduction):
        print(i, intro.text)
    # for span in section[0].find_all('span'):
    #     print(span.text)
    # for temp in section[0].find_all('a'):
    #     print(temp.get('href'))
    # for temp in section[0].select('div.syoseki-page3 a[href]'):
    #     print(temp)
    #for mutiple_comic
    if soup.find('table'):
        temp = [ele.get('href') for ele in soup.find_all('table')[0].find_all('a')]
        print(temp)
    



soup = BeautifulSoup(res.text, 'html.parser')
sections = soup.find_all('section', class_="post")
for section in sections[5:6]:
    #cover
    #cover = section.select('div.syoseki-thumbnail figure a img')
    #print(section)
    comicpage = section.find('a').get('href')
    bs4_data_for_comic_page(comicpage)
    print(comicpage)
    smallcover = section.find('img').get('src')
    print(smallcover)
    #title
    title = section.find('span').text
    print(title)
    #genre
    genres = section.find_all('a', {"rel":"category tag"})
    for genre in genres:
        print(genre.text)

