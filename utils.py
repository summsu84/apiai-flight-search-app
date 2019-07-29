'''
Created on 2017. 7. 26.

@author: JJW
'''
import datetime
#from flightSearch.test import generateFlightDate
#from test.test_datetime import DAY


def checkFlightTime(scheduledDepartDate, startTime):
    
    print("CheckFlihtTime")
    departHour = scheduledDepartDate[8:10]
    startTimeHour = startTime.split(':')
    print (departHour)
    print (startTimeHour)
    if departHour == startTimeHour[0]:
        return True
    else:
        return False

def parseFlightDate(date):
    
    date = date.replace('2018', '2017')
    newDate = date.replace('-', '')
    
    return newDate

# 20170720075500 14 digit string --> 2017-07-20 07:55 format
def generateFlightDate(strDate):
    print "generateFlightDate start"
    print strDate
    
    year = strDate[0:4]
    month = strDate[4:6]
    day = strDate[6:8]
    hour = strDate[8:10]
    min = strDate[10:12]
    second = strDate[12:14]
    
    conDateTime = year + '-' + month + '-' + day + ' ' + hour + ':' + min + ':' + second
    

    print(conDateTime)
    return conDateTime
    
def generateReturnMsg(speech, intentType):

    data = {}
    if "FlightStatus" == intentType :
        data = generateFlightStatusMsg(speech)
    else:
        data = generateFlightScheduleMsg(speech)
    
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "data": data,
        "source": "flightsearchapiai"
    }
        
    
    
def generateFlightStatusMsg(speech):
    
    print ("generateFlightStatusMsg Starting..")
    print (speech)
        
    data =  {
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
                                "textToSpeech":speech,
                                "displayText":speech
                            }
                    },
                    {
                        "basicCard":
                            {
                                
                                "title": "Flight Status Information",
                                "formattedText": speech,
                                "image": {
                                    "url": "https://www.google.com/search?q=42",
                                    "accessibilityText": "Image alternate text"
                                },
                                "buttons" :[
                                ]
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
    }
    
    print ("generateFlightStatusMsg Finished..")
    print (data)
    return data
    
    
def generateFlightScheduleMsg(speech):
    
     
    data =  {
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
                                    "textToSpeech":speech,
                                    "displayText":speech
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
            }   
    
    return data
