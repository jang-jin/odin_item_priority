import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

강화석 = {
    '무기' : '무기 강화석',
    '방어구' : '방어구 강화석',
    '망토' : '방어구 강화석',
    '장신구' : '장신구 강화석',
    '호각' : '장신구 강화석',
    '문장' : '장신구 강화석',
    '완장' : '장신구 강화석',
    '견장' : '장신구 강화석',
}
강화확률 = {
    '무기' : [1, 1, 1, 1, 1, 1, 0.51, 0.28, 0.18, 0.13, 0.10],
    '방어구' : [1, 1, 1, 1, 1, 1, 0.42, 0.26, 0.18, 0.13, 0.10],
    '망토' : [1, 1, 0.83, 0.44, 0.29, 0.23, 0.19, 0.15, 0.13, 0.11, 0.10],
    '장신구' : [1, 1, 0.74, 0.40, 0.29, 0.23, 0.19, 0.15, 0.13, 0.11, 0.10],
    '호각' : [1, 1, 0.83, 0.52, 0.37, 0.28, 0.23, 0.18, 0.15, 0.13, 0.11],
    '문장' : [1, 1, 0.81, 0.51, 0.37, 0.28, 0.22, 0.18, 0.15, 0.13, 0.11],
    '완장' : [1, 1, 0.85, 0.54, 0.38, 0.29, 0.23, 0.19, 0.16, 0.13, 0.12],
    '견장' : [1, 1, 0.85, 0.54, 0.38, 0.29, 0.23, 0.19, 0.16, 0.13, 0.12],
}

def 아이템(이름, 강화, 종류, 기본구매가격=None, 구매or제작='둘다'):
    구매가격리스트 = ['구매선택X']*(강화+1)
    제작가격리스트 = ['제작선택X']*(강화+1)
    필요개수리스트 = 강화필요개수기댓값(강화, 종류)
    재료리스트 = 제작재료(이름)
    거래소X = []

    if 기본구매가격 is not None and 구매or제작 != '제작':
        구매가격리스트 = 강화다이아기댓값(강화, 종류, 기본구매가격)
    if 구매or제작 != '구매' and len(재료리스트) > 0:
        기본제작가격 = 0
        for 재료, 재료개수 in 재료리스트:
            재료가격 = 거래소.get(재료, 재료)
            if isinstance(재료가격, str):
                거래소X.append(재료)
            else:
                기본제작가격 += 재료가격*재료개수
        제작가격리스트 = 강화다이아기댓값(강화, 종류, 기본제작가격)
        if len(거래소X) > 0:
            print(f'{이름}의 제작재료 가격을 거래소에 등록해주세요.')
            print(거래소X)
            제작가격리스트 = ['거래소재료등록X']*(강화+1)
    if len(재료리스트) == 0:
        제작가격리스트 = ['제작아이템X']*(강화+1)
    최소금액 = 우선순위(구매가격리스트[-1], 제작가격리스트[-1])

    결과 = {'이름' : f'+{강화} {이름}', '최소금액' : 최소금액, '구매가격' : 구매가격리스트[-1], '제작가격' : 제작가격리스트[-1]}
    for i, (구매가격, 제작가격, 필요개수) in enumerate(zip(구매가격리스트, 제작가격리스트, 필요개수리스트)):
        결과[f'{i}강구매가격'] = 구매가격
        결과[f'{i}강제작가격'] = 제작가격
        결과[f'{i}강필요개수'] = 필요개수

    return 결과

def 강화다이아기댓값(강화, 종류, 기본가격):
    가격리스트 = [기본가격]*(강화+1)
    for i in range(1, 강화+1):
        기본가격 = (기본가격 + 거래소[강화석[종류]]) / 강화확률[종류][i]
        가격리스트[i] = round(기본가격, 2)
    return 가격리스트

def 강화필요개수기댓값(강화, 종류, 개수=1):
    필요개수리스트 = [개수]*(강화+1)
    for i in range(강화, 0, -1):
        개수 = 개수 / 강화확률[종류][i]
        필요개수리스트[i-1] = round(개수, 2)
    return 필요개수리스트

def 제작재료(이름):
    재료리스트 = []
    req = requests.get('https://odin.inven.co.kr/db/item', params={'searchword':이름})
    soup = BeautifulSoup(req.text, 'html.parser')
    req = requests.get('https://odin.inven.co.kr' + soup.select_one('table.list_table a').attrs['href'])
    soup = BeautifulSoup(req.text, 'html.parser')
    for i in soup.select('ul.materialList span.text'):
        재료, 재료개수 = map(lambda x:x.strip(), i.text.split('x'))
        재료개수 = int(재료개수.replace(',', ''))
        if 재료 != '골드':
            재료리스트.append([재료, 재료개수])
    return 재료리스트

def 우선순위(구매가격, 제작가격):
    if isinstance(구매가격, str) and isinstance(제작가격, str):
        return None
    elif isinstance(구매가격, str):
        return 제작가격
    elif isinstance(제작가격, str):
        return 구매가격
    else:
        return min(구매가격, 제작가격)

############################### 오딘_아이템_우선순위v1.0 사용법 ###############################
# 1. 목록에 다음과 같은 형식으로 얻고자하는 강화아이템의 정보를 적습니다.
#   - 아이템(아이템명, 목표강화수치, 아이템종류, 기본구매가격=0강아이템가격)
#     + 아이템명 : 문자, (주의) 아이템의 이름이 조금이라도 틀리면 안됩니다!
#     + 목표강화수치 : 숫자
#     + 아이템종류 : ('무기', '방어구', '망토', '장신구', '호각', '문장', '완장', '견장') 중 하나
#     + 0강아이템가격 : 숫자, 현재 거래소에서 판매하는 강화되지 않은 아이템의 가격을 적습니다.
#   - 예) 아이템('설원의 마법구', 6, '무기', 기본구매가격=650)
# 2. 거래소에 재료 가격을 최신화합니다.
#   - 제작에 필요한 재료를 거래소에 등록하지 않고 3.을 실행했을 때 필요한 재료목록이 출력됩니다.
# 3. python main.py 를 실행합니다.
#   - 엑셀 내용 설명
#     + 최소금액 : 구매가격과 제작가격의 최솟값
#     + 구매가격 : 해당 아이템을 구매하여 목표치까지 강화하는데 필요한 다이아 기댓값
#     + 제작가격 : 해당 아이템을 제작하여 목표치까지 강화하는데 필요한 다이아 기댓값
#     + x강구매가격 : 해당 아이템을 구매하여 x강까지 강화하는데 필요한 다이아 기댓값
#     + x강제작가격 : 해당 아이템을 제작하여 x강까지 강화하는데 필요한 다이아 기댓값
#     + x강필요개수 : 해당 아이템을 목표치까지 강화하는데 필요한 x강 아이템 개수 기댓값
#############################################################################################

# 21.11.21 기준
거래소 = { 
    '무기 강화석' : 2.6,
    '방어구 강화석' : 0.343,
    '장신구 강화석' : 17,
    '나무' : 0.04,
    '광석' : 0.157,
    '아마풀' : 0.663,
    '연마석' : 1.3,
    '가공석' : 0.692,
    '위그드람' : 5.44,
    '구드벨' : 3.25,
    '마력 깃든 정수' : 29,
    '의문의 결정' : 3.16,
}

목록 = [
    아이템('설원의 마법구', 6, '무기', 기본구매가격=650),
    아이템('검은 모래 투구', 9, '방어구', 기본구매가격=13),
    아이템('드베르그의 갑옷', 7, '방어구', 기본구매가격=298),
    아이템('혹한의 장갑', 6, '방어구', 기본구매가격=690),
    아이템('혹한의 신발', 7, '방어구', 기본구매가격=295),
    아이템('요르문간드의 비늘 망토', 2, '망토', 기본구매가격=81),
    아이템('아스크의 전투 목걸이', 5, '장신구', 기본구매가격=10),
    아이템('발키리의 전투 목걸이', 5, '장신구', 기본구매가격=380),
    아이템('겨울의 귀걸이', 2, '장신구', 기본구매가격=380),
    아이템('망자의 비명 팔찌', 2, '장신구', 기본구매가격=90),
    아이템('망자의 비명 반지', 3, '장신구', 기본구매가격=90),
    아이템('북풍의 벨트', 2, '장신구', 기본구매가격=500),
]

목록 = pd.DataFrame(목록).sort_values(by='최소금액')
파일이름 = '오딘_아이템_우선순위v1.0.csv'
목록.to_csv(파일이름, encoding='')
print(f"{os.getcwd()}\\{파일이름} 에 저장되었습니다.")