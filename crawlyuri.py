import json
import secrets
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime


def  bs4_data(url, *args, **kwargs):
    pass



soup = BeautifulSoup(res.text, 'html.parser')
sections = soup.find_all('section', class_="post")
print(sections[5])