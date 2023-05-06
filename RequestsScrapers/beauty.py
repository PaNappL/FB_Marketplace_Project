import requests, re, csv
import brotli
import time
import urllib.parse
from bs4 import BeautifulSoup
from datetime import datetime
from collections import defaultdict
from Exceptions.CustomExceptions import *

class Beautiful_Check2():
    __resp = ""
    check = ""
    data_values = {}
    
    def get_link_data_save(self, user: dict, link: str, savePath: str):
        self.__load_HTML(user,link)
        self.__get_data()
        self.__reformat_desc()
        self.__save_data(link,savePath)

    def get_link_data(self, user: dict, link: str) -> list:
        self.__load_HTML(user,link)
        self.__get_data()
        self.__reformat_desc()
        return list(link, self.data_values.values())

    def get_link_data_test(self, user: dict, link: str):
        self.__load_HTML(user,link)
        self.__get_data()
        self.__reformat_desc()

    def __load_HTML(self, user: dict, dest_url: str):

        item_id = self.__get_id(dest_url)

        link = "https://www.facebook.com/api/graphql/"

        headers,data = self.__get_req_det(user, item_id)

        response = requests.post(
            link,
            data = data,
            headers = headers,
            )

        self.__resp = str(response.content)
        self.check = self.__resp
        self.__check_Exceptions()

    def __get_id(self, link: str):
        url_vars = link.split("/")

        for pos, var in enumerate(url_vars):
            if var == "item":
                return url_vars[pos+1]

    def __get_req_det(self, user: dict, item_id: str):

        headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "cache-control": "no-cache",
            "content-type": "application/x-www-form-urlencoded",
            "cookie": user["cookies"],
            "origin": "https://www.facebook.com",
            "pragma": "no-cache",
            "referer": "https://www.facebook.com/marketplace/?ref=app_tab",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            "x-fb-friendly-name": "MarketplacePDPContainerQuery",
        }
        
        cmmrc_rnk_obj = {
            "target_id":899565422787436585,
            "target_type":6,
            "primary_position":0,
            "ranking_signature":7708872560041000960,
            "commerce_channel":501,
            "value":0,
            "upsell_type":21,
            "candidate_retrieval_source_map":"null",
            "grouping_info":"null"
        }
        
        cmmrs_rnk_obj_str = "{"
        
        for k,v in cmmrc_rnk_obj.items():
            if cmmrs_rnk_obj_str != "{":
                cmmrs_rnk_obj_str += ","
            cmmrs_rnk_obj_str += fr'\\\"{k}\\\":{v}'
            
        cmmrs_rnk_obj_str += "}"
        
        pdpcntxtTD = {
            "qid":"-4832405415640296722",
            "mf_story_key":item_id,
            "commerce_rank_obj":cmmrs_rnk_obj_str,
            "ftmd_400706":"111112l"
        }
        
        pdpcntxtTD_str = "{"
        
        for k,v in pdpcntxtTD.items():
            if pdpcntxtTD_str != "{":
                pdpcntxtTD_str += ","
            pdpcntxtTD_str += fr'\"{k}\":\"{v}\"'
            
        pdpcntxtTD_str += "}"
        
        data_vars = {
            "UFI2CommentsProvider_commentsKey":"MarketplacePDP",
            "canViewCustomizedProfile":"true",
            "feedbackSource":56,
            "feedLocation":"MARKETPLACE_MEGAMALL",
            "location_latitude":51.512145996094,
            "location_longitude":-0.1043701171875,
            "location_radius":65,
            "location_vanity_page_id":"london",
            "pdpContext_isHoisted":"false",
            "pdpContext_trackingData":pdpcntxtTD_str,
            "referralCode":"marketplace_top_picks",
            "relay_flight_marketplace_enabled":"false",
            "scale":1,
            "should_show_new_pdp":"false",
            "targetId":item_id,
            "useDefaultActor":"true"
        }

        vars = "{"
        
        for k,v in data_vars.items():
            if vars != "{":
                vars += ","
            vars += f'"{k}":'
            if v == "true" or v == "false" or type(v) == float or type(v) == int:
                vars += f'{v}'
            else:
                vars += f'"{v}"'
        
        vars += "}"
        
        vars = urllib.parse.quote(vars, safe='')
        
        data_dict = user["data"]
        data_dict["variables"] = vars
        
        data = ""

        for k,v in data_dict.items():
            if len(data) != 0:
                data+= '&'
            data += f'{k}={v}'

        return headers,data

    def __check_Exceptions(self):
        query = '"marketplace_product_details_page":'
        pos = self.__resp.find(query)
        page_found = self.__resp[pos+len(query):].split("}")[0]

        query = '"Rate limit exceeded"'
        rate_exceeded = query in self.__resp

        query = 'error":'
        pos = self.__resp.find(query)
        try:
            error = int(self.__resp[pos+len(query):].split(',')[0])
        except:
            error = 0

        if page_found == "null":
            raise NoListingException("Listing Not Found")

        if rate_exceeded:
            raise NoLoadException("Rate Exceeded")

        if error == 1357053:
            raise NoLoadException("Account Has Been Banned")
        elif error == 1357001:
            raise NoLoadException("Not Logged In")

    def __get_data(self):
        data_location = self.__get_data_location()
        self.data_values = self.__get_data_value(data_location)
    
    def __get_data_location(self):
        search_queries = ['"__typename":"User","name":','"__typename":"User","id":','"redacted_description":{"text":','"location_text":{"text":','"join_time":','"listing_photos":','marketplace_listing_category_id":']

        username = self.__resp.find(search_queries[0])
        user_id = self.__resp.find(search_queries[1])
        description = self.__resp.find(search_queries[2])
        location = self.__resp.find(search_queries[3])
        join_date = self.__resp.find(search_queries[4])
        images_count = self.__resp.find(search_queries[5])
        category = self.__resp.find(search_queries[6])

        content = {"username":[username,len(search_queries[0])],"user_id":[user_id,len(search_queries[1])],"description":[description,len(search_queries[2])],"location":[location,len(search_queries[3])],"join_date":[join_date,len(search_queries[4])],"images_count":[images_count,len(search_queries[5])],"category":[category,len(search_queries[6])]}

        fail_count = 0

        for key,value in content.items():
            if(value[0] != -1):
                value[0] += value[1]
                content[key] = value[0]
            else:
                content[key] = -1
                fail_count += 1
        
        if fail_count == len(content.keys()):
            raise UserDataFail()

        return content
    
    def __get_data_value(self, data: dict):
        print(data)
        for key,value in data.items():

            if value == -1:
                continue

            index = value

            stringVals = self.__resp[index:]

            if(key == "join_date"):
                unixdate = stringVals.split('}')[0]
                unixdate = unixdate.split(',')[0]
                inp_value = datetime.fromtimestamp(int(unixdate)).strftime('%Y')
            elif(key == "images_count"):
                images = stringVals.split('ProductImage')[1:]
                inp_value = len(images)
            else:
                inp_value = stringVals.split('"')[1]
            
            data[key] = inp_value

        return data

    def __reformat_desc(self):
        description = self.data_values["description"]
        description = description.replace("\\n"," ")
        description = description.replace("\\","")
        description = self.__remove_special_chars(description)
        description = self.__get_word_freq(description)
        
        self.data_values["description"] = description
        
    def __remove_special_chars(self, string: str):
        return re.sub(r"[^a-zA-Z0-9 !?_]", "", string)
    
    def __get_word_freq(self, string):
        words = defaultdict(int)

        for word in string.split():
            if len(word) > 2:
                words[word] += 1

        return dict(words)
        
    def __save_data(self, url: str, savePath: str):
        fin = False
        while not fin:
            try:
                with open(savePath, 'a', newline='') as a:
                    values = list(self.data_values.values())
                    values.insert(0,url)
                    writer = csv.writer(a)
                    writer.writerow(values)
                fin = True
            except:
                time.sleep(0.2)

class Beautiful_Check():
    __soup = None
    data_values = {}
    
    def get_link_data(self, link, savePath):
        self.__load_HTML(link)
        self.__get_data()
        self.__reformat_desc()
        self.__save_data(link,savePath)

    def get_link_data_test(self,link):
        self.__load_HTML(link)
        self.__get_data()
        self.__reformat_desc()

    def __load_HTML(self, link):
        listingHTML = requests.get(link, 
            headers={
            'Host' : 'www.facebook.com',
            'accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding' : 'br',
            'cookie' : 'c_user=100089312301796; xs=36:lKFEpJFKWAx2_w:2:1674157250:-1:-1::AcVkHRsB_PznKWI_91c-Vr1uXJIJS7m_0zeZf5z_MA; oo=v1%7C3%3A1674325770',
            'sec-fetch-site' : 'same-origin',
            'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            }
        )

        self.__soup = BeautifulSoup(listingHTML.content, 'html.parser')

        self.__check_Exceptions(listingHTML)

    def __check_Exceptions(self, HTML):
        if self.__check_banned():
            raise NoLoadException("Seems like you got banned heh")

        if not HTML.headers.get('accept-ch-lifetime'):
            raise NoListingException("Listing Not Found or Unavailable")

    def __check_banned(self):
        try:
            title = self.__soup.find("title").text
            if title == "Log in to Facebook":
                return True
        except:
            None
        
        return False

    def __get_data(self):
        scripts = self.__soup.find_all("script", string=True)
        data_template = {"username":[],"user_id":[],"join_date":[],"description":[],"location":[],"images_count":[],"category":[]}
                    
        data_location = self.__get_data_location(scripts, data_template)
        self.data_values = self.__get_data_value(scripts, data_location)
    
    def __get_data_location(self, scripts, data):
        for index,script in enumerate(scripts):
            script = str(script)
            search_queries = ['"__typename":"User","name":','"__typename":"User","id":','"redacted_description":{"text":','"location_text":{"text":','"join_time":','"listing_photos":','marketplace_listing_category_name']

            username = script.find(search_queries[0])
            user_id = script.find(search_queries[1])
            description = script.find(search_queries[2])
            location = script.find(search_queries[3])
            join_date = script.find(search_queries[4])
            images_count = script.find(search_queries[5])
            category = script.find(search_queries[6])

            content = {"username":[username,len(search_queries[0])],"user_id":[user_id,len(search_queries[1])],"description":[description,len(search_queries[2])],"location":[location,len(search_queries[3])],"join_date":[join_date,len(search_queries[4])],"images_count":[images_count,len(search_queries[5])],"category":[category,len(search_queries[6])]}

            for key,value in content.items():
                if(value[0] != -1):
                    value[0] += value[1]
                    data[key] = [index, value[0]]
        
        return data
    
    def __get_data_value(self, scripts, data):
        for key,value in data.items():
            index = value[0]
            str_indx = value[1]

            stringVals = str(scripts[index])[str_indx:]

            if(key == "join_date"):
                unixdate = stringVals.split('}')[0]
                inp_value = datetime.fromtimestamp(int(unixdate)).strftime('%Y')
            elif(key == "images_count"):
                images = stringVals.split('ProductImage')[1:]
                inp_value = len(images)
            else:
                inp_value = stringVals.split('"')[1]
            
            data[key] = inp_value
        
        return data

    def __reformat_desc(self):
        description = self.data_values["description"]
        description = description.replace("\\n"," ")
        description = description.replace("\\","")
        description = self.__remove_special_chars(description)
        description = self.__get_word_freq(description)
        
        self.data_values["description"] = description
        
    def __remove_special_chars(self, string):
        return re.sub(r"[^a-zA-Z0-9 !?_]", "", string)
    
    def __get_word_freq(self, string):
        words = defaultdict(int)

        for word in string.split():
            if len(word) > 2:
                words[word] += 1

        return dict(words)
        
    def __save_data(self, url, savePath):
        with open(savePath, 'a', newline='') as a:
            values = list(self.data_values.values())
            values.insert(0,url)
            writer = csv.writer(a)
            writer.writerow(values)