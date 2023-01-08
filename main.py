from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import Keys
from selenium.webdriver.support.ui import Select
import time
import re
import os
import pandas as pd

CLEANR = re.compile('<.*?>')


def cleanhtml(raw_html):
    cleantext = re.sub(CLEANR, '', raw_html)
    return cleantext


Option = Options()
Option.headless = True
Option.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'

driver = webdriver.Firefox(options=Option)
driver.maximize_window()
driver.get("https://www.police.gov.il/mapskifout.aspx?mid=67")

driver.find_element(By.XPATH, value='//*[@id="checkRoad"]').click()

driver.find_element(By.XPATH, value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_Road_Arrow"]').click()

collisionData = str
mainDict = {}
roadsWithNoData = []

# Choose year (2021)
for i in range(2):
    driver.find_element(By.XPATH,
                    value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_YearComboBox_Input"]').send_keys(2)
driver.find_element(By.XPATH,
                    value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_YearComboBox_Input"]').send_keys(
    Keys.ENTER)

for roadNumber in driver.find_element(By.CLASS_NAME, value='rcbList').get_attribute('innerHTML').split('</li>'):
    roadNumber = cleanhtml(roadNumber)

    driver.find_element(By.XPATH, value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_Road_Input"]').clear()
    driver.find_element(By.XPATH, value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_Road_Input"]').send_keys(roadNumber)
    time.sleep(1)
    driver.find_element(By.XPATH, value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_Road_Input"]').send_keys(
        Keys.ENTER)
    time.sleep(2)
    try:
        junctionsList = list(driver.find_element(By.XPATH, value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_Junction1_DropDown"]').get_attribute('innerHTML').split('</li>'))
    except Exception as e:
        print('No junctions for road number: ' + roadNumber)
        continue
    for idx, junction in enumerate(junctionsList[0:len(junctionsList)-2]):
        junctionFrom = cleanhtml(junction)
        junctionTo = cleanhtml(junctionsList[idx+1])
        print(roadNumber + ' ' + junctionFrom + ' ' + junctionTo)
        try:
            driver.find_element(By.XPATH,value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_Junction1_Input"]').clear()
            driver.find_element(By.XPATH, value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_Junction1_Input"]').send_keys(junctionFrom)
            time.sleep(1)
            driver.find_element(By.XPATH, value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_Junction1_Input"]').send_keys(Keys.ENTER)
            driver.find_element(By.XPATH, value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_Junction2_Input"]').clear()
            driver.find_element(By.XPATH, value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_Junction2_Input"]').send_keys(junctionTo)
            time.sleep(1)
            driver.find_element(By.XPATH, value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_Junction2_Input"]').send_keys(Keys.ENTER)
        except:
            print('unknown error occured')
            continue
        driver.find_element(By.XPATH, value='//*[@id="SearchButton"]').click()
        time.sleep(1)
        try:
            collisionData = driver.find_element(By.CLASS_NAME, value='resultset').get_attribute('innerHTML')
        except Exception as e:
            print(e)
            print('No data for road number: ' + roadNumber + ' junctions: ' + junctionFrom + ' - ' + junctionTo)
            roadsWithNoData.append(roadNumber)
            continue
        collisionData = collisionData.split('</div>')
        secondaryDict = {}
        for index in range(2, len(collisionData[2:]) - 2, 2):
            secondaryDict.update({cleanhtml(collisionData[index]): cleanhtml(collisionData[index + 1])})
        mainDict.update({roadNumber +'::' + junctionFrom + ':'+ junctionTo: secondaryDict})

dataBase = pd.DataFrame.from_dict(mainDict, orient='index')
dataBase.fillna(0, inplace=True)
dataBase.to_csv('dataBase.csv', encoding='utf-8-sig')
print(roadsWithNoData)
driver.quit()
