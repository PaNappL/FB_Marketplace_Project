from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time, csv

class ListingScraper():

    #Private Variables
    __username = "mociopocig@gmail.com"
    __password = "uduc#IoIA&ELfowbOU9iBS^7!h1W1kPwuCHg6Fg664v96S^AJo"
    __driver = None

    #Global Variables
    listingHeaders = ['Description','Location','ImageCount','ImageQuality']
    profileHeaders = ['ID','URL']
    listingInformation = []
    profileInformation = []

    def __init__(self) -> None:
        self.__start()
        self.__login()

    def __start(self):
        #code by pythonjar, not me
        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.default_content_setting_values.notifications" : 2}
        chrome_options.add_experimental_option("prefs",prefs)

        #specify the path to chromedriver.exe (download and save on your computer)
        self.__driver = webdriver.Chrome('C:/Users/zorko/chromedriver.exe', chrome_options=chrome_options)

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
        self.__goto_url(url)
        self.__getContent()
        self.__appendCSV(savePath, self.listingInformation)

    def __goto_url(self, url):
        #Go to url provided
        self.__driver.get(url)

    #Get and save listing and profile data
    def __getContent(self):
        self.listingInformation = []
        
        #Get Listing description
        description = self.__driver.find_element("xpath","(//span[@class='x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x6prxxf xvq8zen xo1l8bm xzsf02u'])")

        #Get Listing location
        location = self.__driver.find_element("xpath","(//span[@class='x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x4zkp8e x676frb x1nxh6w3 x1sibtaa xo1l8bm xi81zsa'])")
        try:
            location = location.text.split(": ",1)[1]
        except:
            location = location.text.split(" in ",1)[1]
            
        #Get images data
        images = self.__driver.find_elements("xpath","(//div[@class='x6s0dn4 x78zum5 x193iq5w x1y1aw1k xwib8y2 xu6gjpd x11xpdln x1r7x56h xuxw1ft xc9qbxq']//img)")

        if len(images) == 0:
            images = self.__driver.find_elements("xpath","(//div[@class='x6s0dn4 x78zum5 x1iyjqo2 xl56j7k x6ikm8r x10wlt62 xh8yej3 x1ja2u2z']//img)")

        image_size = []
            
        for image in images:
            h = image.get_attribute('naturalHeight')
            w = image.get_attribute('naturalWidth')
            image_size.append(str(w)+"x"+str(h))
            
        #Save Listing Information to Array
        self.listingInformation.append(description.text)
        self.listingInformation.append(location)
        self.listingInformation.append(len(images))
        self.listingInformation.append(image_size)
        
        #Click User Profile
        WebDriverWait(self.__driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[class='x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xzsf02u x1s688f']"))).click()
        
        time.sleep(2)

        #Get User Profile URL
        profile = self.__driver.find_element("xpath","//div[@class='__fb-light-mode x1n2onr6 xzkaem6']//a[@class='x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x1ypdohk xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x87ps6o x1lku1pv x1a2a7pz x9f619 x3nfvp2 xdt5ytf xl56j7k x1n2onr6 xh8yej3']")
        profileUrl = profile.get_attribute('href')

        #Destructure url to get Profile ID
        ID = profileUrl.rsplit("/",1)[1]
        
        #Save Profile ID and url to Array
        self.listingInformation.append(ID)
        self.listingInformation.append(profileUrl)

    def __appendCSV(self, path, data):
        with open(path, 'a', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(data)