from NER_base import preprocess, chunking, iob_tags, get_NER, visulize_NER

import en_core_web_sm
#from nltk import tokenize
import random
from datetime import datetime
import time
import pprint
import requests ,sys
import json
import re
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
    airport_query =  [key for key in info_dict if info_dict[key] == "GPE"]
    date_query = [key for key in info_dict if info_dict[key] == "CARDINAL" or info_dict[key]=="DATE"]
    #print(airport_query, date_query)
    # return airport_query if there are 2 valid airport, otherwise ask further
    #print(request_query)

    # if query is done, the user can change the value of each keys
   # if "start_airport" in request_query.keys() and "end_airport" in request_query.keys():
   #     airport_query_done = True


    """
    print("aq: " +str(airport_query)+ str(len(airport_query)))
    print("dq: "+ str(date_query))
    print("rq: " + str(request_query))
    """
    # the machine checkes 1. airport_query 2. date_query
    INFOGET_RESPONSE=["Got it! ", "Okay!", "No problem."]
    if len(airport_query) == 2:
        ## airport code convert
        request_query["start_airport"] = str(airport_query[0]).lower()
        request_query["end_airport"] = str(airport_query[1]).lower()
        #request_query.extend([ str(x).lower() for x in airport_query ])
        time.sleep(3)
        #print("RQ: "+ str(request_query))
        print(random.choice(INFOGET_RESPONSE))
        time.sleep(3)
        #if "start_airport" in request_query.keys() and "end_airport" in request_query.keys():
         #   airport_query_done = True
    elif "start_airport" not in request_query.keys() and "end_airport" not in request_query.keys() :
        time.sleep(3)
        print("Sorry, I am not Sure where do you want to fly from, "
              "and where do you want to go...")
        time.sleep(1)
        print("Could you tell me again, please?")
        user_request(input(), request_query, False)

    INFOWRONG_RESPONSE = ["You've entered an invalid date. Please try again. (YYYY-MM-DD)",
                          "Sorry, I can only process the date in the format YYYY-MM-DD. Please tell me again.",
                          "Oops, I was not taught how to process the date except for YYYY-MM-DD. Please try again."]

    DATE_INPUTS = ["to","and",","]
    #print("date_query_done == False.... go on here")
    if date_query_done == False:
        if len(date_query) == 1:
            token = str(date_query[0]).split()
            for t in token:
                if t in DATE_INPUTS:
                    token.remove(t)
            # check token[0] and token[1] format YYYY-MM-DD
            #print(len(token), str(token))

            # if only one date is given
            #print("token: " + str(token))
            if len(token) == 1 :
                print("Sorry, I need both start and return date to search for the best deal for you.")
                print("Please try again.")
                user_request(input(), request_query)
            try:
                if len(token) == 2:
                    if datetime.strptime(token[0], '%Y-%m-%d'): request_query["start_date"] = token[0]
                    if datetime.strptime(token[1], '%Y-%m-%d'): request_query["end_date"] = token[1]
                    #request_query.extend([x for x in token if datetime.strptime(x, '%Y-%m-%d')])
                    date_query_done = True
                    #print("after date query done: "+ str(request_query))
                else:
                    print(random.choice(INFOWRONG_RESPONSE))

            except ValueError:
                print(random.choice(INFOWRONG_RESPONSE))
            finally:
                if date_query_done == False:
                    user_request(input(), request_query)

            return request_query

        elif len(date_query) == 2:
            # check query format YYYY-MM-DD
            # in python3, map returns an iterator, so use list(map())
            token = list(map(str,date_query))
            try:
                if datetime.strptime(token[0], '%Y-%m-%d'): request_query["start_date"] = token[0]
                if datetime.strptime(token[1], '%Y-%m-%d'): request_query["end_date"] = token[1]
               # request_query.extend([x for x in token if datetime.strptime(x, '%Y-%m-%d')])
                date_query_done = True

            except ValueError:
                print("You've entered an invalid date. Please try again.")
            finally:
                if date_query_done == False:
                    random.choice(INFOWRONG_RESPONSE)
            return request_query
        else:
            print("when do you plan to start and return from your trip? "
                  "I'd like to have your information in this format: YYYY-MM-DD. Thank you!")
            user_request(input(), request_query)

    return request_query
def airport_code(airport_name):
    """
    Get the place code that match a query string in Skyscanner API
    :param airport_name:
    :return: airport_code
    """

    url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/autosuggest/v1.0/DE/EUR/de-DE/"
    querystring = {"query": airport_name}
    headers = {
        'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
        'x-rapidapi-key': "4471693d35msh38693640e9f39fep11449fjsnc7a32c6a2991"
    }

    # get airport code
    response = requests.request("GET", url, headers=headers, params=querystring)
    res = json.loads(response.text)


    return res["Places"][0]["PlaceId"]


def request_web(airport_query, start_date, end_date):
    """
    Connect to Skyscanner Flight Search API

    :param request_query: Departure airport name, Destination airport name, start date and end date.
    :return: return the web data
    """
    #27ba98d416mshac46526beae97f8p1306f8jsnc13488e74d1e

    url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browsequotes/v1.0/DE/EUR/de/"+ airport_query + "/"+ start_date
    querystring = {"inboundpartialdate": end_date}

    headers = {
        'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
        'x-rapidapi-key': "4471693d35msh38693640e9f39fep11449fjsnc7a32c6a2991"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    # To print prettier JSON with pprint.
    """
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(response.text)
    """

    # load JSON data and get MinPrice
    res = json.loads(response.text)
    return res["Quotes"][0]["MinPrice"]

def query_extraction(request_query):

    start_airport = request_query["start_airport"]
    end_airport = request_query["end_airport"]
    start_date = request_query["start_date"]
    end_date = request_query["end_date"]

    return start_airport, end_airport, start_date, end_date


if __name__ == '__main__':
    """
    nlp = en_core_web_sm.load()
    sentence, entity, labels = get_NER(nlp,"Stuttgart to Munich")
    print("ENTITIY: " + str(entity))
    print("LABEL: " + str(labels))
    """


    # 1. user input greeting
    user_input = input()
    time.sleep(0.5)
    print(greeting(user_input))

    # 2. machine answer greeting and ask for task and get the request_query from user
    time.sleep(1)
    print("I'm good at searching flight price. How can I help you?")
    user_input = input()
    request_query = {}
    user_request(user_input, request_query)
    # 3. map the request_query to websearch format and search for the ticket price
    start_airport, end_airport, start_date, end_date=  query_extraction(request_query)
    time.sleep(1)
    print("Got it. You want to fly from " + start_airport + " to " + end_airport)
    time.sleep(1)
    print("And your journey will be from "+ start_date + " to " + end_date)
    # 4. Confirmation
    time.sleep(1)
    print("Do you want to change anything? If yes, \"airport\" or \"dates\" or \"both?\" ")
    user_input = input().lower()
    if "no" in user_input.split() or user_input.startswith("n") :
        time.sleep(1)
        print("Great!")
    elif  "airport" in user_input.split():
        time.sleep(1)
        print("Ok, to change the airports, please tell me where do you want to start your trip and where is your destination.")
        user_input = input().lower()
        start_airport, end_airport, start_date, end_date = query_extraction(user_request(user_input, request_query, True, True))
        print("Your request has been changed. You want to fly from " + start_airport + " to " + end_airport + ".")

    elif "dates" or "date" in user_input.split():
        time.sleep(1.5)
        print("OK, to change the dates, please tell me when do you want to fly and when do you want to return. (in YYYY-MM-DD Format will be great!)")
        user_input = input()
        start_airport, end_airport, start_date, end_date = query_extraction(user_request(user_input, request_query, True, True))
        print("Your request has been changed. You want to travel from " + start_date + " to " +  end_date + ".")

    elif "both" in user_input.split():
        print("Ok....Just tell me where and when!")
        user_input = input()
        print("great!")

    # 5. Connect with API and get the price
    time.sleep(1)
    print("Just a moment........... I'll be right back with the best price!")
    start_airport, end_airport, start_date, end_date = query_extraction(request_query)
    airport_query = airport_code(start_airport) + "/" + airport_code(end_airport)
    price = request_web(airport_query, start_date, end_date)
    time.sleep(3)
    print("Hey! I've found a good price for you!)")
    print("The lowest price I've found is: " + str(price) + "€")


    #result= get_price(web)

    # 4. machine answer (a screen shot?)
