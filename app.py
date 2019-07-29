'''
Created on 2017. 6. 14.

@author: JJW
'''

#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
import urllib
from werkzeug.urls import BaseURL
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os
import requests


from flask import Flask
from flask import request
from flask import make_response
#from searchairportcity import processAirportCityCodeRequest
from utils import parseFlightDate, generateFlightDate, generateReturnMsg,checkFlightTime

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))
 #   res = processFlightScheduleRequest(req)
    
    
    action = req.get("result").get("action");
    
    if action == "actionFlightStatusSearch":
        res = processFlightStatusRequest(req)
    elif action == "actionFlightScheduleSearch":
        res = processFlightScheduleRequest(req)
    elif action == "actionKoreanAirFAQ":
        res = processFAQEng(req)

    
    #res = processRequest(req)
    print (res)
    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


#FlightSchedule Function
def processFlightScheduleRequest(req):
    print("processFlightScheudelRequest")
    
    parameters = req.get("result").get("parameters")
    
    destCityInfo = processAirportCityCodeRequest(parameters.get('ToLocation'))

    originCityInfo = processAirportCityCodeRequest(parameters.get('FromLocation'))
  
    paramDate = parameters.get("StartDate")
    startDate = parseFlightDate(paramDate)
    startTime = parameters.get("StartTime")

    
    baseurl = "https://[base url]/api/flightstatus/" + startDate + "/cities"
    
    data = {
        "departureAirportList" : [originCityInfo.get('cityCode')],
        "arrivalAirportList" : [destCityInfo.get('cityCode')]
    }
    
    headers = {'content-type': 'application/json'}
    print("before request")
    print(baseurl)
    print(data)
    
    #response = Request.post(baseurl, data=json.dumps(postdata), headers=headers)
    result = requests.post(baseurl, json=data, headers=headers)
    
    res = makeWebhookFlightScheduleResult(result.json(), destCityInfo.get('engName'), originCityInfo.get('engName'), startTime )
    
    print(result.json())
         
    #print(resultData);
    
    return res


def processAirportCityCodeRequest(city):
    baseurl = "https://azuresearchwithflightsearchdemo.search.windows.net/indexes/airportcityindex/docs/search?api-version=2016-09-01"
    
    data = {
        "search": city
    }
    
    headers = {
        'content-type': 'application/json',
        'Accept': 'application/json',
        'api-key' : '[API-KEY]'
    }
    
    result = requests.post(baseurl, json=data, headers=headers)
    

    #print(result.json());
    
    res = parseAirportCityCode(result.json())
    print(res)
    return res;

def parseAirportCityCode(res):
    
    #print(">>parseAirportCityCode start..")
    
    dataList = res.get('value')
    data = dataList[0]
    #print(data)
    engName = data.get('engName')
    cityCode = data.get('code')
    
    return {
        'engName' : engName,
        'cityCode' : cityCode
    }

#def parseFlightDate(date):
    #
    #date = date.replace('2018', '2017')
    #newDate = date.replace('-', '')
    #
    #return newDate

#FlightStatus Function
def processFlightStatusRequest(req):
        
    parameters = req.get("result").get("parameters")
    
    flightNumber = parameters.get('FlightNumber')
  
    paramDate = parameters.get("FlightDate")
    startDate = parseFlightDate(paramDate)
    baseurl = "http://[base url]/api/flightstatus/" + startDate + "/" + flightNumber
    result = urlopen(baseurl).read()
    data = json.loads(result)

    
    res = makeWebhookFlightStatusResult(data)
    return res

#FAQ
def processFAQEng(req):
    #if req.get("result").get("action") != "actionFlightStatusSearch":
        #return {}
    
    baseurl = "http://[base url]/api/flightstatus/20170614/1117"
    
    result = urlopen(baseurl).read()
    data = json.loads(result)

    print(data);
    
    res = makeWebhookFlightStatusResult(data)
    return res


def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')"




#Make FlightSchedule Result format 
def makeWebhookFlightScheduleResult(data, destName, originName, startTime):
    
    flightList = data.get('flightList')
    flight = {}
    if flightList is None:
        return generateReturnValue('I am sorry, there is no flight schedule you requested')

    for flightVal in flightList:
        departureDatetime = flightVal.get('departureDatetime')
        scheudledDepartureDatetime = departureDatetime.get('scheduled')
        if checkFlightTime(scheudledDepartureDatetime, startTime) == True :
            flight = flightVal
            break

    
    
    #flightList = data.get('flightList')
    #if flightList is None:
    #    return generateReturnValue('I am sorry, there is no flight schedule you requested')

    #flight = flightList[0];
    #if flight is None:
    #    return generateReturnValue('I am sorry, there is no flight schedule you requested')

    
    if flight is None:
        return generateReturnValue('I am sorry, there is no flight schedule you requested')

    speech = makeFlightScheduleSpeech(flight, destName, originName)

    #print(speech)

    return generateReturnMsg(speech, "FlightScheudule")

#makeSpeech
def makeFlightScheduleSpeech(flight, destName, originName):
    
    print("makeFlightScheduleSpeech start..")
    
    status = flight.get('status')
    flightNumber = flight.get('flightNumber')
    
    departureAirportCode = flight.get('departureAirportCode');
    arrivalAirportCode = flight.get('arrvalAirportCode');
    
    arrivalDatetime = flight.get('arrivalDatetime');
    departureDatetime = flight.get('departureDatetime');
    
    scheudledArrivalDatetime = arrivalDatetime.get('scheduled');
    acutalArricvalDatetime = arrivalDatetime.get('actual');
    
    scheudledDepartureDatetime = departureDatetime.get('scheduled');
    acutalDepartureDatetime = departureDatetime.get('actual');
    
    convertedScheudledArrivalDatetime = generateFlightDate(scheudledArrivalDatetime)
    convertedAcutalArricvalDatetime = generateFlightDate(acutalArricvalDatetime)
    
    convertedScheudledDepartureDatetime = generateFlightDate(scheudledDepartureDatetime)
    convertedAcutalDepartureDatetime = generateFlightDate(acutalDepartureDatetime)
    
    speech = 'I searched flight schedule of Korean Air, flight number' + flightNumber + ', from ' + originName + ", to " + destName + \
             ' .The scheduled depart time is ' + convertedScheudledDepartureDatetime + ', and arrival time is ' + convertedScheudledArrivalDatetime
        
    return speech
    

    
    


def makeWebhookFlightStatusResult(data):
    print ("makeWebhookFlightStatusResult")
    flightList = data.get('flightList')
    if flightList is None:
        return generateReturnValue('I am sorry, there is no flight schedule you requested')

    flight = flightList[0];
    if flight is None:
        return generateReturnValue('I am sorry, there is no flight schedule you requested')

    speech = makeFlightStatusSpeech(flight)
    
    print(speech)

    return generateReturnMsg(speech, "FlightStatus")


def makeFlightStatusSpeech(flight):
    
    status = flight.get('status')
    flightNumber = flight.get('flightNumber')
    
    departureAirportCode = flight.get('departureAirportCode');
    arrivalAirportCode = flight.get('arrvalAirportCode');
    
    arrivalDatetime = flight.get('arrivalDatetime');
    departureDatetime = flight.get('departureDatetime');
    
    scheudledArrivalDatetime = arrivalDatetime.get('scheduled');
    acutalArricvalDatetime = arrivalDatetime.get('actual');
    
    scheudledDepartureDatetime = departureDatetime.get('scheduled');
    acutalDepartureDatetime = departureDatetime.get('actual');
    
    convertedScheudledArrivalDatetime = generateFlightDate(scheudledArrivalDatetime)
    convertedAcutalArricvalDatetime = generateFlightDate(acutalArricvalDatetime)
    
    convertedScheudledDepartureDatetime = generateFlightDate(scheudledDepartureDatetime)
    convertedAcutalDepartureDatetime = generateFlightDate(acutalDepartureDatetime)
    
    speech = 'The flight number ' + flightNumber + ' you requested'
    
    if 'code' in status:
        speech += ' departed.'
        speech += ' The scheduled depart time is ' + convertedScheudledDepartureDatetime + ', and arrival time is ' + convertedScheudledArrivalDatetime + '.'
        speech += ' The actual depart time is ' + convertedAcutalDepartureDatetime + ' , and arrival time is ' + convertedAcutalArricvalDatetime + '.'
    else:
        speech += ' have not departed yet.'
        speech += ' The scheduled depart time is ' + convertedScheudledDepartureDatetime + ', and arrival time is ' + convertedScheudledArrivalDatetime + '.'        
    
    return speech
    

def generateReturnValue(str):
    return {
        "speech": str,
        "displayText": str,
        # "data": data,
        # "contextOut": [],
        "data": 
        {
            "google":
            {
                "expectUserResponse": "true",
                "isSsml": "false",
                "noInputPrompts": [],
                'richResponse': {
                    "items":
                    [
                        {
                            "simpleResponse":
                            {
                                "textToSpeech":str,
                                "displayText":str
                            }
                        }
                    ],
                    "suggestions":
                    [
                        {
                            "title":"Yes"
                        },
                        {
                            "title":"No"
                        }
                    ]
                 }
                  
            }
        },
        "source": "flightsearchapiai"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("11Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
