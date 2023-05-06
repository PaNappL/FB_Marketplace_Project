from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time, csv, threading, json

template = {"user_id":"",
        "cookies": "",
        "data": {"av": "",
            "__user": "",
            "__a": "1",
            "__dyn": "7AzHxqU5a5Q1ryUqxenFw9uu2i5U4e0ykdwSwAyUco2qwJxS0DU6u3y4o1DU2_CxS320om782Cwwwqo465o-cw5MKdwGxu782lwv89kbxS2218wc61axe3S1lwlE-U2exi4UaEW2G1jxS6FobrwKxm5oe8464-5pUfEe872m7-2K0-pobodEGdwb61jg2cwMwiU8UdUcojxK2B0oobo8o",
            "__csr": "ghOj8BFO_OjpYiABkJIROhNaOrbDO4_s-yfj_QHiOaGbEydBl9p_AV9LhHheFaGGh6jz98yunQtpkArUCluibDKeUjASpz8SGxiaBHzk8xGl2UyudyoybLGu10Cx248cFUc8iwLzUGfzEGu3-Eydwyx6fypopwKCxSq6k3a4Ue8aUaU5C1AweW6UjAwVwgEbo-1TwmU2rxC1uK1Nw0H9w0g4802QfzA0-80xC04481ao0yh00hmE0Ia4tw0iko0Ta0cXw1He0ru0l-2a",
            "__req": "14",
            "__hs": "19382.HYP:comet_pkg.2.1.0.2.1",
            "dpr": "1",
            "__ccg": "EXCELLENT",
            "__rev": "1006861186",
            "__s": "dgjh58%3Ave8tjg%3Ak4cgw3",
            "__hsi": "7192651984101699527",
            "__comet_req": "15",
            "fb_dtsg": "",
            "jazoest": "25561",
            "lsd": "HOTw1Tns-g-ZUbfIpwMyWu",
            "__spin_r": "1006861186",
            "__spin_b": "trunk",
            "__spin_t": "1674669791",
            "fb_api_caller_class": "RelayModern",
            "fb_api_req_friendly_name": "MarketplacePDPContainerQuery",
            "variables": "",
            "server_timestamps": "true",
            "doc_id": "6115171051879362"}
    }

class userUpdate():

    def __init__(self):
        loginInfo = json.load(open("loginInfo.txt"))
        userData = {}

        for i in range(len(loginInfo["email"])):
            data = self.getUserData(loginInfo, i)
            userData[str(i+1)] = data

        self.saveUserData(userData)

    def getUserData(self, uInf, i) -> dict:
        email = uInf["email"][i]
        passwrd = uInf["pass"][i]

        driver = self.openChrome()
        self.loginToFB(driver, email, passwrd)
        data = self.getData(driver)
        data = self.reformatData(data)
        return data

    def openChrome(self) -> webdriver:
        #code by pythonjar, not me
        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.default_content_setting_values.notifications" : 2}
        chrome_options.add_experimental_option("prefs",prefs)
        chrome_options.set_capability(
                                "goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"}
                            )

        #specify the path to chromedriver.exe (download and save on your computer)
        driver = webdriver.Chrome('C:/Users/zorko/chromedriver.exe', options=chrome_options)

        #open the webpage
        driver.get("http://www.facebook.com")
        return driver

    def loginToFB(self, driver, email,passwrd) -> None:
        #Click cookies button
        try:
            WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-cookiebanner='accept_only_essential_button']"))).click()
        except:
            True

        #target username
        username = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='email']")))
        password = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='pass']")))

        print(password)

        #enter username and password
        username.clear()
        username.send_keys(email)
        password.clear()
        password.send_keys(passwrd)

        #target the login button and click it
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()

    def getData(self, driver) -> dict:
        self.openMarketplace(driver)
        time.sleep(4)
        logs = self.getLogs(driver)
        data = self.parseLogsForData(logs)
        return data

    def openMarketplace(self, driver) -> None:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href="https://www.facebook.com/marketplace/?ref=bookmark"]'))).click()

    def getLogs(self, driver) -> dict:
        link = self.getListing(driver)
        link.click()
        logs = driver.get_log("performance")
        return logs

    def getListing(self, driver) -> webdriver.remote.webelement.WebElement:
        links = driver.find_elements("xpath",'//a[@class="x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g x1lku1pv"]')
        return links[0]

    def parseLogsForData(self, logs) -> dict:
        queries = ['; c_user=','; xs=','&fb_dtsg=']
        data = {"user_id":"","xs":"","fb_dtsg":""}

        for log in logs:
            log = log["message"]
            if len(queries) == 0:
                break
            for query in queries:
                idx = log.find(query)
                if idx != -1:
                    shortLog = log[idx+len(query):]
                    if query == '&fb_dtsg=':
                        data["fb_dtsg"] = shortLog.split("&")[0]
                        queries.remove(query)
                    else:
                        newData = shortLog.split(";")[0]
                        if query == "; xs=":
                            data["xs"] = newData
                        else:
                            data["user_id"] = newData
                        queries.remove(query)

        return data

    def reformatData(self, data) -> dict:
        template = {"user_id": "","cookies": "","fb_dtsg": ""}

        cookies = f'c_user={data["user_id"]}; xs={data["xs"]}'

        for key in template.keys():
            if key == "cookies":
                template[key] = cookies
                continue
            template[key] = data[key]

        return template

    def saveUserData(self, data) -> None:
        json.dump(data, open("users.txt", "w"))

class userFetch():

    __users = {}

    def __init__(self) -> None:
        self.__users = json.load(open("users.txt"))

    def get_users(self) -> list:
        return list(self.__users.keys())

    def fetchUser(self, userID) -> dict:
        return self.__getData(userID)

    def __getData(self, userID: int) -> dict:
        return self.__template_sub(self.__users[userID])

    def __template_sub(self, user: dict) -> dict:
        data = template

        data["user_id"] = user["user_id"]
        data["cookies"] = user["cookies"]
        data["data"]["av"] = user["user_id"]
        data["data"]["__user"] = user["user_id"]
        data["data"]["fb_dtsg"] = user["fb_dtsg"]

        return data

if __name__ =="__main__":
    userUpdate()