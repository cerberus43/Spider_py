import time
import os
import requests
import pymysql
import datetime
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

def saveHtmlFile(html,date):
    with open("/data/python_pro/Spider_py/BJZJW_html/"+date+".html", "wb") as f:
        f.write(html)

def getSign(allInfo):
    AllSign_Dict = {}
    AllSign = allInfo[2]
    AllSign_Dict['SignNum'] = int(AllSign('td')[0].string)
    AllSign_Dict['SignArea'] = float(AllSign('td')[1].string)
    AllSign_Dict['SignHouseNum'] = int(AllSign('td')[2].string)
    AllSign_Dict['SignHouseArea'] = float(AllSign('td')[3].string)
    return AllSign_Dict

def getCheck(allInfo):
    AllCheck = allInfo[0]
    AllCheck_Dict = {}
    AllCheck_Dict['CheckNum'] = int(AllCheck('td')[0].string)
    AllCheck_Dict['CheckArea'] = float(AllCheck('td')[1].string)
    AllCheck_Dict['CheckHouseNum'] = int(AllCheck('td')[2].string)
    AllCheck_Dict['CheckHouseArea'] = float(AllCheck('td')[3].string)
    return AllCheck_Dict

def getMonthdata(allInfo):
    AllMonthdata = allInfo[1]
    AllMonthdata_Dict = {}
    AllMonthdata_Dict['SignNum'] = int(AllMonthdata('td')[0].string)
    AllMonthdata_Dict['SignArea'] = float(AllMonthdata('td')[1].string)
    AllMonthdata_Dict['SignHouseNum'] = int(AllMonthdata('td')[2].string)
    AllMonthdata_Dict['SignHouseArea'] = float(AllMonthdata('td')[3].string)
    return AllMonthdata_Dict

def saveDailyMysql(yesterday_str,AllCheck_Dict,AllSign_Dict):
#def saveMysql(date):
    db = pymysql.connect("localhost", "root", "hoolai", "HData")
    cursor = db.cursor()
    sql = "INSERT INTO BJZJW_DAILY_DATA(Date,CheckNum,CheckArea,CheckHouseNum,CheckHouseArea,SignNum,SignArea,SignHouseNum,SignHouseArea)\
           VALUES('%s',%d,%.2f,%d,%.2f,%d,%.2f,%d,%.2f)" %(yesterday_str,AllCheck_Dict['CheckNum'],AllCheck_Dict['CheckArea'],\
           AllCheck_Dict['CheckHouseNum'],AllCheck_Dict['CheckHouseArea'],AllSign_Dict['SignNum'],\
           AllSign_Dict['SignArea'],AllSign_Dict['SignHouseNum'],AllSign_Dict['SignHouseArea'])
    #sql = "INSERT INTO check_sign(Date)VALUES('%s')"%(date)
    # print(sql)
    try:
       cursor.execute(sql)
       db.commit()
    except:
       db.rollback()
    db.close()

def saveMonthMysql(lastmonth, AllMonthdata_Dict):
#def saveMysql(date):
    db = pymysql.connect("localhost", "root", "hoolai", "HData")
    cursor = db.cursor()
    sql = "INSERT INTO BJZJW_MONTH_DATA(Month,SignNum,SignArea,SignHouseNum,SignHouseArea)\
           VALUES('%s',%d,%.2f,%d,%.2f)" % (lastmonth, AllMonthdata_Dict['SignNum'],\
           AllMonthdata_Dict['SignArea'], AllMonthdata_Dict['SignHouseNum'], AllMonthdata_Dict['SignHouseArea'])
    #sql = "INSERT INTO check_sign(Date)VALUES('%s')"%(date)
    # print(sql)
    try:
       cursor.execute(sql)
       db.commit()
    except:
       db.rollback()
    db.close()

if __name__ == "__main__":
    url = "http://210.75.213.188/shh/portal/bjjs/index.aspx"
    htmltext = getHtmlText(url)
    #date = time.strftime("%Y-%m-%d", time.localtime())
    today = datetime.date.today()
    today_str = today.strftime('%Y-%m-%d')
    oneday = datetime.timedelta(days=1)
    yesterday = today - oneday
    yesterday_str = yesterday.strftime('%Y-%m-%d')
    lastmonth = yesterday.strftime('%Y-%m')
    html_name = today_str+".html"
    html_file = '/data/python_pro/Spider_py/BJZJW_html/'+html_name
    # print(lastmonth)

    if os.path.exists(html_file):
        pass
    else:
        saveHtmlFile(htmltext.encode(), today_str)

    with open(html_file) as html:
        soup = BeautifulSoup(html, 'lxml')
        allInfo = soup.find_all('table', attrs={'class': 'tjInfo'})

    if int(today.strftime('%d')) == 1:
        AllMonthdata_Dict = getMonthdata(allInfo)
        saveMonthMysql(str(lastmonth), AllMonthdata_Dict)

    AllCheck_Dict = getCheck(allInfo)
    AllSign_Dict = getSign(allInfo)
    saveDailyMysql(yesterday_str, AllCheck_Dict, AllSign_Dict)
    print('%s BJZJW_data get success!' %(yesterday_str))