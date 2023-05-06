from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time, csv, threading

class LinksScraper:

    #Private Variables
    __username = "johncook987@wp.pl"
    __password = "rwjsYsXqnJK5hPtp"
    __driver = None
    __threadLocal = threading.local()

    def __init__(self):
        self.__start()
        try:
            while 1:
                self.__login()
        except:
            None

    def __start(self):

        self.__driver = getattr(self.__threadLocal, 'driver', None)

        if self.__driver is None:
            chrome_options = Options()
            prefs = {"profile.default_content_setting_values.notifications" : 2}
            chrome_options.add_experimental_option("prefs",prefs)

            self.__driver = webdriver.Chrome('C:/Users/zorko/chromedriver.exe', chrome_options=chrome_options)
            setattr(self.__threadLocal, 'driver', self.__driver)

        #open the webpage
        self.__driver.get("http://www.facebook.com")

    def __login(self):
        #Click cookies button
        try:
            WebDriverWait(self.__driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-cookiebanner='accept_only_essential_button']"))).click()
        except:
            True

        #target username
        username = WebDriverWait(self.__driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='email']")))
        password = WebDriverWait(self.__driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='pass']")))

        #enter username and password
        username.clear()
        username.send_keys(self.__username)
        password.clear()
        password.send_keys(self.__password)

        #target the login button and click it
        WebDriverWait(self.__driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()

    def fetch_data(self, url, savePath):
        saved = False
        attempts = 0

        while self.__driver.current_url != url and attempts != 2:
            self.__driver.delete_cookie('presence')
            self.__goto_url(url)
            attempts += 1
            time.sleep(0.5)

        if self.check_results() or attempts == 2:
            return

        self.__scroll_down()
        links = self.__get_all_links()
        while not saved:
            saved = self.__appendCSV(savePath,links)
            
        time.sleep(2)

    def __goto_url(self, url):
        #Go to url provided
        self.__driver.get(url)

    def __scroll_down(self):
        for _ in range(100):
            self.__driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.2)

    def __get_all_links(self):
        link_elements = self.__driver.find_elements("xpath","//div[@class='x8gbvx8 x78zum5 x1q0g3np x1a02dak x1rdy4ex xcud41i x4vbgl9 x139jcc6 x1nhvcw1']//a")
        links = []
        for link in link_elements:
            link = link.get_attribute('href')
            if "https://www.facebook.com/marketplace/" in link:
                links.append([link])
        return links

    def check_results(self):
        try:
            center_message = self.__driver.find_element("xpath","//div[@class='xzueoph x1k70j0n']//span[@class='x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xtoi2st x3x7a5m x1603h9y x1u7k74 x1xlr1w8 xi81zsa x2b8uid']")
            if "No listings" in center_message.text:
                return True
        except:
            return False

    def __appendCSV(self, path, data):
        try:
            with open(path, 'a', encoding='UTF8', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(data)
            return True
        except:
            return False



