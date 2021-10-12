import platform
import selenium.webdriver as webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from datetime import date
from datetime import timedelta
import time

chrome_options = Options()
chrome_options.add_argument('--headless')

# checks what the OS it is and executes the relevant driver
if platform.system() == "Windows":
    browser = webdriver.Chrome("E:\Python\chromedriver.exe")#, options = chrome_options)
elif platform.system() == "Linux":
    browser = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")#, options = chrome_options)

# this gets the current page number and enters into the url
with open('Page_number.txt', 'r') as file:
    text = file.read()
current_page = text.strip()

# Gets the number of links downloaded so far
with open('links.csv', 'r') as links_csv:
    text = links_csv.read()
last_line = text.split('\n')[-2]
try:
    num_of_links = int(last_line[:last_line.find(',')])
except:
    num_of_links = 0

url = f"https://gfx-hub.cc/textures/page/1/"
print('Current URL - ', url)

browser.get(url)
wait = WebDriverWait(browser, 5)
xpath_links = "//div[@class='shotstory-3d-text-format']/parent::div/preceding-sibling::div/a"
wait.until(EC.presence_of_element_located((By.XPATH, xpath_links)))
browser.execute_script("window.stop();")

def link_scraper(num_of_links):
    xpath_links = "//div[@class='shotstory-3d-text-format']/parent::div/preceding-sibling::div/a"
    wait.until(EC.presence_of_element_located((By.XPATH, xpath_links)))
    browser.execute_script("window.stop();")

    # this gets the current url and calculates the page number of next page
    separatorlist = []
    if browser.current_url == 'https://gfx-hub.cc/textures/':
        next_page_num = 2
    else:
        index = 0
        for char in browser.current_url:
            if char == '/':
                separatorlist.append(index)
            index += 1
        next_page_num = int(browser.current_url[(separatorlist[-2] + 1):separatorlist[-1]]) + 1

    xpath = "//div[@class='shotstory-3d-text-format']/parent::div/preceding-sibling::div"

    browser.switch_to.window(browser.window_handles[0])

    links = browser.find_elements_by_xpath(xpath)
    linkslist = []

    # appends all the links to the list
    for link in links:
        linkslist.append((link.find_element_by_tag_name('a').get_attribute('href')))
    print('Number of Single Textures on the Page - ', len(linkslist), '\n')
    # opens the links one by one
    i = 0

    for link in linkslist:
        begin = time.time()     # start time to calculate time taken to execute one loop
        i += 1
        xpath_hitfile = '//img[@src="/templates/personal-utf8/images/hitfile.png"]/parent::a/parent::div/following-sibling::div[1]'

        try:
            if i <= len(linkslist):
                browser.get(link)
                # wait.until(EC.presence_of_element_located((By.XPATH, xpath_hitfile)))
                time.sleep(2)
                browser.execute_script("window.stop();")

                title = browser.title.replace(' | GFX-HUB', '').replace('PBR textures – ', '').replace(' / ', '_')

                post_date = browser.find_element(By.XPATH,"//img[@src='/templates/personal-utf8/images/main-news-info1.png']/parent::div").text

                # Get date of the post
                today = date.today()

                if 'today' in post_date.lower():
                    date_of_post = today.strftime("%Y-%m-%d")
                elif 'yesterday' in post_date.lower():
                    date_of_post = (today - timedelta(days=1)).strftime("%Y-%m-%d")
                else:
                    date_of_post = post_date

                wait1 = WebDriverWait(browser, 40)
                browser.switch_to.window(browser.window_handles[0])
                tag = browser.find_element_by_xpath(xpath_hitfile).find_element_by_tag_name('a')
                tag.click()
                browser.switch_to.window(browser.window_handles[1])
                wait1.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

                print(title, browser.current_url)

                end = time.time()       # end time to calculate time taken to execute one loop
                print(f'TIme taken - {end - begin}')        # print time taken to execute the loop (to get one link)

                with open('links.csv','a') as file:
                    file.write(f'{num_of_links+1},{title},{browser.current_url},{date_of_post}\n')

                browser.close()
                browser.switch_to.window(browser.window_handles[0])
                num_of_links += 1
                print(f'Total Number of Links Collected : {num_of_links}\n')

            if i == len(linkslist):
                with open('Page_number.txt', 'w') as f:
                    f.write(str(next_page_num) + '\n')

                browser.get(f"https://gfx-hub.cc/textures/page/{next_page_num}/")
                link_scraper(num_of_links)

        except:
            continue

link_scraper(num_of_links)
