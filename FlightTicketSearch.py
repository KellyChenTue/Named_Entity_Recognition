from NER_base import preprocess, chunking, iob_tags, get_NER, visulize_NER

import en_core_web_sm
#from nltk import tokenize
import random
from datetime import datetime
import time
import pprint
import requests ,sys
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

#from selenium import webdriver
#from chatbot_ner.ner_v2.detectors.temporal.date.date_detection import DateDetector
#import dateparser.dateparser.parser
GREETING_INPUTS = ["hello", "hi", "greetings", "what's up","hey","hallo"]
GREETING_RESPONSES = ["hi", "hey", "hi there", "hello", "Hi!,I am glad! You are talking to me.","how are you?"]


def greeting(sentence):
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)

def user_request(sentence, request_query, airport_query_done = False , date_query_done = False):
    nlp = en_core_web_sm.load()
    sentence, entity, labels = get_NER(nlp, sentence)
    """
    print("ENTITIY: " + str(entity))
    print("LABEL: " + str(labels))
    """
    info_dict = dict(zip(entity,labels))
    #print(info_dict)
    airport_query =  [key for key in info_dict if info_dict[key] == "GPE"]
    date_query = [key for key in info_dict if info_dict[key] == "CARDINAL" or info_dict[key]=="DATE"]
    # return airport_query if there are 2 valid airport, otherwise ask further

    """
    print("aq: " +str(airport_query)+ str(len(airport_query)))
    print("dq: "+ str(date_query))
    print("rq: " + str(request_query))
    """
    # the machine checkes 1. airport_query 2. date_query
    INFOGET_RESPONSE=["Got it! ", "Okay!", "No problem."]
    if airport_query_done == False and len(airport_query) == 2:
        ## airport code convert
        request_query.extend([ str(x).lower() for x in airport_query ])
        time.sleep(3)
        #print("RQ: "+ str(request_query))
        print(random.choice(INFOGET_RESPONSE))
        time.sleep(3)
        airport_query_done = True
    elif airport_query_done == False:
        time.sleep(3)
        print("Sorry, I am not Sure where do you want to fly from, "
              "and where do you want to go...")
        time.sleep()
        print("Could you tell me again, please?")
        user_request(input(), request_query,False)


    INFOWRONG_RESPONSE = ["You've entered an invalid date. Please try again. (YYYY-MM-DD)",
                          "Sorry, I can only process the date in the format YYYY-MM-DD. Please tell me again.",
                          "Oops, I was not taught how to process the date except for YYYY-MM-DD. Please try again."]
    if airport_query_done == True and date_query_done == False:
        DATE_INPUTS = ["to","and",","]
        if len(date_query) == 1:
            token = str(date_query[0]).split()
            for t in token:
                if t in DATE_INPUTS:
                    token.remove(t)
            # check token[0] and token[1] format YYYY-MM-DD
            #print(len(token), str(token))

            # if only one date is given

            if len(token) == 1 :
                print("Sorry, I need both start and return date to search for the best deal for you.")
                print("Please try again.")
                user_request(input(), request_query, True, False)
            try:
                if len(token) == 2:
                    request_query.extend([x for x in token if datetime.strptime(x, '%Y-%m-%d')])
                    date_query_done = True
                else:
                    print(random.choice(INFOWRONG_RESPONSE))

            except ValueError:
                print(random.choice(INFOWRONG_RESPONSE))
            finally:
                if date_query_done == False:
                    user_request(input(), request_query, True, False)

            return request_query

        elif len(date_query) == 2 and date_query_done == False:
            # check query format YYYY-MM-DD
            # in python3, map returns an iterator, so use list(map())
            token = list(map(str,date_query))
            try:
                request_query.extend([x for x in token if datetime.strptime(x, '%Y-%m-%d')])
                date_query_done = True
                print(request_query)

            except ValueError:
                print("You've entered an invalid date. Please try again.")
            finally:
                if date_query_done == False:
                    random.choice(INFOWRONG_RESPONSE)
            return request_query
        else:
            print("when do you plan to start and return from your trip? "
                  "I'd like to have your information is this format: YYYY-MM-DD. Thank you!")
            user_request(input(), request_query, True, False)

def airport_code(airport_name):
    aircode_dict = {
    "stuttgart": "STR", "munich":"MUC", "taipei":"TPE", "taiwan":"TPE", "germany":"FRA", "frankfurt":"FRA",
    "china":"PEK", "barcelona":"BCN", "spain":"BCN"
    }
    code = aircode_dict[airport_name]
    return code


def request_web(airport_query, start_date, end_date):
    """
    Connect to kayak website

    :param request_query: Departure airport name, Destination airport name, start date and end date.
    :return: return the web data
    """
    #27ba98d416mshac46526beae97f8p1306f8jsnc13488e74d1e


    ## Just use browse Quotes, instead of POST and GET
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(response.text)



    """
    
    
    url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/pricing/v1.0"
    #url = 'https://www.kayak.com/flights/' + airport_query + '/' + start_date + '/' + end_date + '-flexible'
    url2 = "https://www.kayak.com/flights"
    payload = "inboundDate=2020-02-01&cabinClass=economy&children=0&infants=0&country=DE&currency=EUR&locale=de-DE&originPlace=MUC&destinationPlace=TPE&outboundDate=2020-01-05&adults=1"
    headers = {
        'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
        'x-rapidapi-key': "27ba98d416mshac46526beae97f8p1306f8jsnc13488e74d1e",
        'content-type': "application/x-www-form-urlencoded"
    }


    driver = requests.request("POST",url, data=payload, headers= headers)
    print(driver.text)

    #driver = webdriver.Chrome

    #soup = BeautifulSoup(driver.content, 'lxml')
    #div = soup.text
    #print(div)


    """

    ##################################################
    """
    # screen shot: pyppeteer
    # https://github.com/miyakogi/pyppeteer/tree/master
    driver = webdriver.PhantomJS()
    #driver.implicitly_wait(30)
    #https://www.kayak.com/flights/MUC-TPE/2020-01-09/2020-01-23-flexible
    url = 'https://www.kayak.com/flights/' + airport_query + '/' + start_date + '/' + end_date + '-flexible'
    driver.get(url)

    time.sleep(30)
    # problem: have to wait until the webpage is loaded fully, then get the complete info from web
    # WebDriverWait
    delay = 60  # seconds

    #element_present = driver.find_element_by_xpath("//div[contains(@id,'FlexMatrixCell')]")
    #element_present = driver.find_element_by_id("FlexMatrixCell__20200124_20200109")
    #print(element_present.text)


    try:
        #element_present = driver.find_element_by_id("FlexMatrixCell__20200124_20200109")
        #element_present = driver.find_element_by_xpath("//div[contains(@id,'FlexMatrixCell')]")
        #element_present = webdriver.PhantomJS.find_element_by_xpath("//div[contains(@id,'FlexMatrixCell')]")
        #element_present = EC.visibility_of_element_located((By.XPATH, "//div[contains(@id,'FlexMatrixCell')]"))
        #element_present = EC.visibility_of_element_located((By.XPATH, "//div[contains(@id,'FlexMatrixCell')]"))
        element_present = EC.presence_of_element_located((By.ID, "FlexMatrixCell__20200124_20200109"))
        WebDriverWait(driver, delay).until(element_present)

        print(str(element_present))
    except TimeoutException:
        driver.save_screenshot('screenshot.png')
        print("Loading took too much time!")



    soup = BeautifulSoup(driver.page_source, 'html.parser')
    #driver.quit()
    #print(soup.text)



    """
##############################################################

    """
    print("url " +url)
    try:
        response = requests.get(url, cookies={'over18': '1'})

    except:
        print("the request was rejected, try it out later!")
        sys.exit(1)
    print("get requests")
    html = response.content
    soup = BeautifulSoup(html, "lxml")
    print(soup)
    """
    return "pass"

def get_price(soup):
    #data = {}
    for div in soup.findAll('div', {'class': 'value'}):
        print("get data....")
        print(div)


if __name__ == '__main__':
    """
    nlp = en_core_web_sm.load()
    sentence, entity, labels = get_NER(nlp,"Stuttgart to Munich")
    print("ENTITIY: " + str(entity))
    print("LABEL: " + str(labels))
    """

    """
    # 1. user input greeting
    print("say something...")
    user_input = input()
    print(greeting(user_input))

    # 2. machine answer greeting and ask for task and get the request_query from user
    print("I'm good at searching flight price. How can I help you?")
    user_input = input()
    request_query = []
    user_request(user_input, request_query)

    # 3. map the request_query to websearch format and search for the ticket price
    print("==============step 3: ")
    print("Got it. You want to fly from " + request_query[0] + " to " + request_query[1])
    print("And your journey will be from "+ request_query[2] + " to " + request_query[3])
    print("Just a moment.......")
    # 3.1 map the airport code
    airport_query = airport_code(request_query[0]) + "-" + airport_code(request_query[1])
    """



    airport_query = "MUC-TPE"
    web = request_web(airport_query, "2020-01-09", "2020-01-23")
    #request_web(airport_query, request_query[2], request_query[3])
    #result= get_price(web)

    # 4. machine answer (a screen shot?)
