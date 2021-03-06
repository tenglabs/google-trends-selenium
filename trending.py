from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
import datetime, time, json, traceback
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


options = Options()
options.headless = False
service = Service('./geckodriver')
driver = webdriver.Firefox(options=options, service=service)

geo = input("GEO : ")
url = f'https://trends.google.com/trends/trendingsearches/daily?geo={geo}'

driver.get(url)
driver.implicitly_wait(1) # To avoid abuse of targeted website !!! In production should be replaced or reworked for proxies


date = driver.find_element(By.CLASS_NAME, "content-header-title").text
xdate = datetime.date.today()

today = xdate.strftime("%A, %B %-d, %Y")
if today != date:
    print(f'News for {today} not found. Shutting down.')
    exit()
wait = WebDriverWait(driver, 15)
elems = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'feed-list-wrapper')][1]//div[contains(@class, 'feed-item-header')]")))
cookiebar = driver.find_element(By.CLASS_NAME, "cookieBarConsentButton") # Can be removed with better XPATH like in production...
cookiebar.click()

trends = {}
print('Welcome to Trend Scraper 1.0. Please restart this file if you have connection errors.')
stop = input("How many trends you want to scan?: ")

for x, elem in enumerate(elems[0:int(stop)],1):
    print(f'Scanning trend #{x}')
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

        wait = WebDriverWait(elem, 15)
        tests = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//ng-transclude[contains(@class, 'carousel-items')]//a")))

        l1 = []
        for test in tests:

            link = test.get_attribute('href')
            title = test.get_attribute('title')
            wait = WebDriverWait(test, 15)
            source = wait.until(EC.presence_of_element_located((By.XPATH,'.//span'))).get_attribute('innerHTML')
            l1.append({'title':title,'link':link,'source':source},)


        trends[x]['related_news'] = l1

print('Finished scaning trends. Scaning google.com')

# ?????????? ???????????????? ???????????? ?? ?????????????? ???????????? ?? ?????????????? related ?? ????????????????, ?????????? ???????????????????? ?????? ???????????????? ???? ???????? ?????????????????? ????????????
search_list = []
for name in trends:
    query = trends[name]
    title = query['name']
    search_list.append(title)
    related_queries = query['related_queries']
    for q in related_queries:
        search_list.append(q)


for data in search_list:
    print(data)

    google = f'https://www.google.com/search?q={data}'
    related_query = query['related_queries']
    driver.get(google)
    wait = WebDriverWait(driver, 10)
    pageInfo = []
    try:
        related_searches = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'y6Uyqe')]")))
    except:
        print(traceback.format_exc())
        try:
            related_searches = driver.find_element(By.XPATH, "//div[contains(@class, 'card-section')]")

        except:
            print('Something went Wrong... ')
            print(traceback.format_exc())
    pageInfo.append({'related_searches': related_searches.text}) # Iterate over this...
    searchResults = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "g")))

    for xr, result in enumerate(searchResults, start=1):

        try:

            wait = WebDriverWait(result, 10)

            element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a")))
            link = element.get_attribute('href')
            header = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h3'))).text
            text = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'IsZvec'))).text

            pageInfo.append({'postion':xr,
            'header': header, 'link': link, 'text': text
                            })
        except:
            print('Something went wrong')
            print(traceback.format_exc())



final_data = {'trends':trends, 'google_search':pageInfo}


with open(f'output/data{datetime.datetime.now()}.json', 'w', encoding='utf-8') as f:
    json.dump(final_data, f, ensure_ascii=False, indent=4)


# ???????????? ???? ?????????? ?? ???????????????????? (?? ???????? ???? ???????? ?????????????????? ?????????????? ?????????????? ?? ???????????????????? ??????), ???? ???????????????????? ???????????? ???????????? ?? Selenium .
# ?????? ???????????????????? ?????????????? ???? ??????????????: 1) Rotating Proxies ( ?????????????? ????????????)
#                                    2) ?????????????????????????? ?? ?????????? ???????????????????????? ???????? (?????????????? ?????????? ???????? ?????????? ???????????????? ?? ??????????????,
#                                       ?? ?????????????????? ???? ??????????: settings, trending, google_search
#                                    3) ???????????????????????????? ?? ?????????????????????????? ?????? ?????????? HTML-????????????????  ?? google (???? ???????????? ???????????? ?????????????????????????? ???????????? ?????????????? ??????????????)
#                                    4) ????????????/???????????????????????????? try/except
#                                    5) ???????????????????????? ?????????????????? ???????????????? ???? ?????????????? ???????????????????????? JSON
#                                    6) ???????????????????? related searches ??. ???? ????????????, ???? ?? ?? ?????? ???????????????????? ?????????????? ???????????????? ???? ???????????????????? ????????.
# ?????????????? ???? ???????? ?????????? ?? ????????????????.


# ?????????????????? ????????:
# 1) ???????? ???????????? ?????????????? ???????????????? ???? ???????????? - ?????????? ???????????????????? ???? ???????????????? ?????? ???? ???????????????????? DOM. - ???????????????? ?? ?????????????? Proxy Rotation
# 2) ???? ?????? ???????????????? ?? ?????????? ??????????????????, ?? ?????????????????? ?????????????? ?????????????????????? ???????????????? ?? ?????????????? ???????????????????? ?????????????????? ?????? XPATH ( ???????????????? ?????????????? ?? ?????????? #1)
#    - ???????????????? ?? ?????????????? ???????????? ?? ???????????????????? ???????????????? ???????????????????? HTML ???????????????? google
# 3) ?????? ?????????????????????????? VPN ?????? ???????????? ???? ???????? ???????????? - ?????? ?????????? ???????????????? ??.??. ???????????????????????? ???????????? ?????? ???????? ????????????
# 4) ???????????????????? ???????? ???????????????? ?????????????????????? ???????????????? ???????????? ????????????????????, ?????????????????? ???????????????????? ???????? (Telegram Desktop ?????????? ???????????????????????? ???????????????? ???? Ubuntu)
#    - ???????????????? ?????????????????????????? headless ????????????????
