# Api.ai - flight-search app webhook implementation in Python

This is flight search webhook integrated with Api.ai which is convesration platform by google.
This provides three function such as flight status, flight schedule, flight FAQ.
The process is as bellow:

---------				---------------------				-------------
|		|	webhook		|					|	web service	|			|
| Api.Ai|	--------->	|   flight-search  	|	-------->	| External	|
|		|	response	|   back-end app	|	response	| Service	|
|		|	<---------	|					|	<--------	|			|
---------				---------------------				-------------

1) Api.Ai request post /webhoook url of flight-search app by containing intent action such as flight status, flight scheudle, or FAQ.
2) Flight-searchlight-search back-end app process intent action of request and call function by it.
3) Based on function, it request external web service to get flight status or flight schedule information.
4) External service response result to flight-search back-end app.
5) Flight-search back-end app response the result of webhook, and then send client generated message based on response.


## Flight Status Function

This function is to request flight status information.

```python
def processFlightStatusRequest(req):
        
    parameters = req.get("result").get("parameters")
    
    flightNumber = parameters.get('FlightNumber')
  
    paramDate = parameters.get("FlightDate")
    startDate = parseFlightDate(paramDate)
    baseurl = "[This is airline web service base url]" + startDate + "/" + flightNumber
    result = urlopen(baseurl).read()
    data = json.loads(result)

    
    res = makeWebhookFlightStatusResult(data)
    return res
	
```

## Flight Schedule Function

This function is to request flight schedule information based on origin city, depart city and date

```python
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
	
```




