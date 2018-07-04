import time
import os
import requests
import datetime
import pymysql
from bs4 import BeautifulSoup

def getHtmlText(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36"
        }
        gethtml = requests.get(url, headers=headers, timeout=30)
        gethtml.raise_for_status()
        #print(gethtml.apparent_encoding)
        gethtml.encoding = gethtml.apparent_encoding
        return gethtml.text
        #return gethtml.read()
    except:
        return "Error"

def saveHtmlFile(html,today):
    with open("/data/python_pro/Spider_py/LJ_html/"+today+".html", "wb") as f:
        f.write(html)

def checkMonthBegin(today):
    today_day = today.strftime('%d')
    if today_day == '01':
        return True
    else:
        return False

def saveLJDailayData(yesterday_str,allDailyData_Dict):
    db = pymysql.connect("localhost", "root", "hoolai", "HData")
    cursor = db.cursor()
    sql = "INSERT INTO LJ_DAILY_DATA(Date,NewAddHouse,NewAddPeople,FollowSee) VALUES('%s',%d,%d,%d)"\
          %(yesterday_str, allDailyData_Dict['NewAddHouse'], allDailyData_Dict['NewAddPeople'], allDailyData_Dict['FollowSee'])
    #print(sql)
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    db.close()

def saveLJMonthDate(last_month,allMonthData_Dict):
    db = pymysql.connect("localhost", "root", "hoolai", "HData")
    cursor = db.cursor()
    sql = "INSERT INTO LJ_MONTHLY_DATA(Month,AveragePrice) VALUES('%s',%d)" %(last_month, allMonthData_Dict['AveragePrice'])
    # print(sql)
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
    db.close()

if __name__ == "__main__":
    url = "https://bj.lianjia.com/fangjia/"
    htmltext = getHtmlText(url)
    today = datetime.date.today()
    today_str = today.strftime('%Y-%m-%d')
    oneday = datetime.timedelta(days=1)
    yesterday = today - oneday
    yesterday_str = yesterday.strftime('%Y-%m-%d')
    last_month = yesterday.strftime('%Y-%m')
    # print(last_month)

    html_name = today_str+".html"
    html_file = '/data/python_pro/Spider_py/LJ_html/'+html_name

    if os.path.exists(html_file):
        pass
    else:
        saveHtmlFile(htmltext.encode(), today_str)

    with open(html_file) as html:
        soup = BeautifulSoup(html, 'lxml')

    # OnSaleHouse = soup.find_all('a', attrs={'href': '/ershoufang/'})
    #print(OnSaleHouse[2].text)

    allDailyData_Dict = {}
    DailyData = soup.find_all('div', attrs={'class': 'num'})
    allDailyData_Dict['NewAddHouse'] = int(DailyData[0].text)
    allDailyData_Dict['NewAddPeople'] = int(DailyData[1].text)
    allDailyData_Dict['FollowSee'] = int(DailyData[2].text)
    # print(allDailyData_Dict)
    saveLJDailayData(yesterday_str, allDailyData_Dict)

    if checkMonthBegin(today):
        allMonthData_Dict = {}
        average_price = soup.find_all('div', attrs={'class': 'qushi-2'})
        # print(average_price[0].span.text)
        allMonthData_Dict['AveragePrice'] = int(average_price[0].span.text)
        # print(allMonthData_Dict)
        saveLJMonthDate(last_month, allMonthData_Dict)
    else:
        pass

