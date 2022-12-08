from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import Keys
from selenium.webdriver.support.ui import Select
import time
import re
import os

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

for roadNumber in driver.find_element(By.CLASS_NAME, value='rcbList').get_attribute('innerHTML').split('</li>'):
    flag = False
    print(cleanhtml(roadNumber))
    driver.find_element(By.XPATH, value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_Road_Input"]').clear()
    driver.find_element(By.XPATH, value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_Road_Input"]').send_keys(cleanhtml(roadNumber))
    time.sleep(1)
    driver.find_element(By.XPATH, value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_Road_Input"]').send_keys(Keys.ENTER)
    time.sleep(2)
    junctionsList = list(driver.find_element(By.XPATH, value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_Junction1_DropDown"]').get_attribute('innerHTML').split('</li>'))
    for idx,junctionName in enumerate(driver.find_element(By.XPATH, value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_Junction1_DropDown"]').get_attribute('innerHTML').split('</li>')):
        if idx + 1 == len(junctionsList) - 1:
            break
        if len(junctionsList) < 2:
            flag =True
        else:
            print(cleanhtml(junctionName), cleanhtml(junctionsList[idx+1]))
            driver.find_element(By.XPATH, value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_Junction1_Input"]').clear()
            driver.find_element(By.XPATH, value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_Junction1_Input"]').send_keys(cleanhtml(junctionName))
            time.sleep(1)
            driver.find_element(By.XPATH, value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_Junction1_Input"]').send_keys(Keys.ENTER)
            driver.find_element(By.XPATH, value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_Junction2_Input"]').clear()
            driver.find_element(By.XPATH, value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_Junction2_Input"]').send_keys(cleanhtml(junctionsList[idx+1]))
            time.sleep(1)
            driver.find_element(By.XPATH, value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_Junction2_Input"]').send_keys(Keys.ENTER)
        for year in YearList:
            print(year)
            # Starting with one year
            # driver.find_element(By.XPATH, value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_YearComboBox_Input"]').send_keys(2)
            time.sleep(1)
            driver.find_element(By.XPATH, value='//*[@id="ctl00_ctl00_ContentPlaceMain_contentPageMain_YearComboBox_Input"]').send_keys(Keys.ENTER)
            time.sleep(1)
            driver.find_element(By.XPATH, value='//*[@id="SearchButton"]').click()
            time.sleep(1)
            try:
                if flag:
                    # flag is for downloading whole year data fix this
                    collisionData = driver.find_element(By.CLASS_NAME, value='resultset').get_attribute('innerHTML')
                    # os.makedirs(
                    #     f'./{cleanhtml(roadNumber)}/{year}',
                    #     exist_ok=True)
                    # with open(
                    #         f'./{cleanhtml(roadNumber)}/{year}/{cleanhtml(roadNumber)}.text',
                    #         'w', encoding='utf-8') as f:
                    #     for tr in collisionData.split('</div>'):
                    #         f.write(cleanhtml(tr) + '\n')
                    # print((
                    #           f'./{cleanhtml(roadNumber)}/{year}/{cleanhtml(roadNumber)}.text saved succefully'))
                    mainDict.update({cleanhtml(roadNumber) + ":" + cleanhtml(junctionName) + ":" +cleanhtml(junctionsList[idx+1]) : collisionData})

                else:
                    collisionData=driver.find_element(By.CLASS_NAME, value='resultset').get_attribute('innerHTML').split('/n')
                    # os.makedirs(f'./{cleanhtml(roadNumber)}/{cleanhtml(junctionName)+":"+cleanhtml(junctionsList[idx + 1])}/{year}', exist_ok=True)
                    # with open(f'./{cleanhtml(roadNumber)}/{cleanhtml(junctionName)+":"+cleanhtml(junctionsList[idx + 1])}/{year}/{cleanhtml(junctionName)+"-"+cleanhtml(junctionsList[idx + 1])}.text', 'w', encoding='utf-8') as f:
                    #     for tr in collisionData.split('</div>'):
                    #         f.write(cleanhtml(tr)+'\n')
                    #
                    # print((f'./{cleanhtml(roadNumber)}/{cleanhtml(junctionName)+"-"+cleanhtml(junctionsList[idx + 1])}/{year}/{cleanhtml(junctionName)+"-"+cleanhtml(junctionsList[idx + 1])}.text saved succefully' ))
                    #     #f.write(cleanhtml(collisionData))
                    secondaryDict = {}
                    for item in collisionData:
                        secondaryDict.update({''.join(i for i in cleanhtml(item) if not i.isdigit()): int(re.search(r'\d+', cleanhtml(item)).group())})
                    mainDict.update({cleanhtml(roadNumber) + ":" + cleanhtml(junctionName) + ":" +cleanhtml(junctionsList[idx+1]) : secondaryDict})

            except Exception as e:
                print(e)
                pass




driver.quit()
