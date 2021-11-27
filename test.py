import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

class 아이템:
    def __init__(self, 이름='', 강화=0, 구매가격=None, 구매or제작='둘다'):
        pass

주옵션 = {}
부옵션 = {}
이름 = '설원의 마법구'
req = requests.get('https://odin.inven.co.kr/db/item', params={'searchword':이름})
soup = BeautifulSoup(req.text, 'html.parser')
req = requests.get('https://odin.inven.co.kr' + soup.select_one('table.list_table a').attrs['href'])
soup = BeautifulSoup(req.text, 'html.parser')
수치 = soup.select_one('div.headMainEffect span.effectColor').text.strip()
soup.select_one('div.headMainEffect span.effectColor').extract()
옵션 = soup.select_one('div.headMainEffect').text.strip()
주옵션[옵션] = 수치
for x in soup.select('ul.mainOption.optionList li'):
    부옵션[' '.join(x.text.split(' ')[:-1])] = x.text.split(' ')[-1]
print(부옵션)