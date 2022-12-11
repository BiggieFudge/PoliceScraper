from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import Keys
from selenium.webdriver.support.ui import Select
import time
import re
import os
import pandas as pd

# as per recommendation from @freylis, compile once only
CLEANR = re.compile('<.*?>')

def cleanhtml(raw_html):
  cleantext = re.sub(CLEANR, '', raw_html)
  return cleantext

Option = Options()
Option.headless = False
Option.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'

driver = webdriver.Firefox(options=Option)
driver.maximize_window()
driver.get("https://www.police.gov.il/mapskifout.aspx?mid=67")

driver.find_element(By.XPATH, value='//*[@id="checkRoad"]').click()

driver.find_element(By.XPATH, value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_Road_Arrow"]').click()
YearList = [2022]
YearList.reverse()

mainDict = {}
driver.find_element(By.XPATH, value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_YearComboBox_Input"]').send_keys(2)
driver.find_element(By.XPATH, value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_YearComboBox_Input"]').send_keys(Keys.ENTER)

for roadNumber in driver.find_element(By.CLASS_NAME, value='rcbList').get_attribute('innerHTML').split('</li>'):
    flag = False
    print(cleanhtml(roadNumber))
    driver.find_element(By.XPATH, value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_Road_Input"]').clear()
    driver.find_element(By.XPATH, value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_Road_Input"]').send_keys(cleanhtml(roadNumber))
    time.sleep(1)
    driver.find_element(By.XPATH, value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_Road_Input"]').send_keys(Keys.ENTER)
    time.sleep(2.5)
    junctionsList = list(driver.find_element(By.XPATH, value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_Junction1_DropDown"]').get_attribute('innerHTML').split('</li>'))
    # for idx,junctionName in enumerate(driver.find_element(By.XPATH, value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_Junction1_DropDown"]').get_attribute('innerHTML').split('</li>')):
    #     if idx + 1 == len(junctionsList) - 1:
    #         break
    #     if len(junctionsList) < 2:
    #         flag =True
    #     else:
            # print(cleanhtml(junctionName), cleanhtml(junctionsList[idx+1]))
            # driver.find_element(By.XPATH, value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_Junction1_Input"]').clear()
            # driver.find_element(By.XPATH, value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_Junction1_Input"]').send_keys(cleanhtml(junctionName))
            # time.sleep(1)
            # driver.find_element(By.XPATH, value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_Junction1_Input"]').send_keys(Keys.ENTER)
            # driver.find_element(By.XPATH, value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_Junction2_Input"]').clear()
            # driver.find_element(By.XPATH, value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_Junction2_Input"]').send_keys(cleanhtml(junctionsList[idx+1]))
            # time.sleep(1)
            # driver.find_element(By.XPATH, value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_Junction2_Input"]').send_keys(Keys.ENTER)

    driver.find_element(By.XPATH, value='//*[@id="SearchButton"]').click()
    time.sleep(1)
    try:
        if flag:
            # flag is for downloading whole year data fix this
            collisionData=driver.find_element(By.CLASS_NAME, value='resultset').get_attribute('innerHTML').split('</div>')
            secondaryDict = {}
            for index in range( 2 ,len(collisionData[2:]) - 2  ,2):
                secondaryDict.update({cleanhtml(collisionData[index]) : cleanhtml(collisionData[index + 1])})
            mainDict.update({cleanhtml(roadNumber) + ":": secondaryDict})


        else:
            collisionData=driver.find_element(By.CLASS_NAME, value='resultset').get_attribute('innerHTML').split('</div>')
            secondaryDict = {}
            for index in range( 2 ,len(collisionData[2:]) - 2  ,2):
                secondaryDict.update({cleanhtml(collisionData[index]) : cleanhtml(collisionData[index + 1])})
            mainDict.update({cleanhtml(roadNumber) + ":": secondaryDict})

    except Exception as e:
        print(e)
        pass
dataBase = pd.DataFrame.from_dict(mainDict, orient='index')
dataBase.fillna(0, inplace=True)
dataBase.to_csv('dataBase.csv' , encoding='utf-8-sig')






driver.quit()
