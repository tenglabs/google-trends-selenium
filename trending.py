from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
import datetime, time, json
from selenium.webdriver.firefox.options import Options


options = Options()
options.headless = False # Might not load correctly from first try if set to False
service = Service('./geckodriver')
driver = webdriver.Firefox(options=options, service=service)


url = 'https://trends.google.com/trends/trendingsearches/daily?geo=US'

driver.get(url)
driver.implicitly_wait(2) # To improve stability of this app and avoid abuse of target website, not the best way for production but does the trick for demo


date = driver.find_element(By.CLASS_NAME, "content-header-title").text
elems = driver.find_elements(By.XPATH, "//div[contains(@class, 'feed-list-wrapper')][1]//div[contains(@class, 'feed-item-header')]")

cookiebar = driver.find_element(By.CLASS_NAME, "cookieBarConsentButton") # Can be removed with better XPATH like in production...
cookiebar.click()

trends = {}
print('Welcome to Trend Scraper 1.0. Please restart this file if you have connection errors. ')
stop = input("How many trends you want to scan?: ")

for x, elem in enumerate(elems[0:int(stop)],1):
    #print(f'Scanning trend #{x}')
    elem.click()

    formatted = elem.text.split('\n', 2)[1] # Ugly Code, but for demo purposes it's ok
    related_queries = elem.find_elements(By.XPATH, "//a[contains(@class, 'chip')]")

    trends[x] = {
                            'name':formatted,
                            'related_queries':[],
                             }
    for query in related_queries:

        trends[x]['related_queries'].append(query.text)


    btns = elem.find_elements(By.XPATH, "//button[contains(@class, 'carousel-next')]")



    for btn in btns:
        tests = elem.find_elements(By.XPATH, "//ng-transclude[contains(@class, 'carousel-items')]//a")

        l1 = []
        for test in tests:
            link = test.get_attribute('href')
            title = test.get_attribute('title')
            source = test.find_element(By.XPATH,'.//span').get_attribute('innerHTML') #Ugly solution, I will leave it like this unless it will be in production

            l1.append({'title':title,'link':link,'source':source},)


        trends[x]['related_news'] = l1
#print(trends)


with open(f'output/result.json{datetime.datetime.now()}', 'w') as fp:
    json.dump(trends, fp)
    print('Output JSON file can be found in output directory')