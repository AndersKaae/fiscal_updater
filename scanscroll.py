import requests
import json
import traceback
#from database import Store_Object_List
from datetime import datetime

server = 'http://distribution.virk.dk/registreringstekster/registreringstekst'
server = 'http://distribution.virk.dk/offentliggoerelser/_search'

def DTConv(date_string):
    if date_string != None:
        dateformat = "2022-05-16T07:57:55.000Z"
        dateformat = '%Y-%m-%dT%H:%M:%S.%fZ'
        dateObject = datetime.strptime(date_string, dateformat)
    else:
        dateObject = date_string
    return dateObject

def StartScroll(date):
    headers = {'Content-Type': 'application/json',}
    #query = '{ "query":{"bool":{"must":[{"match":{"sidstOpdateret":"' + str(date) + '"}}]} }, "size":100}'
    query = '{ "query":{"bool":{ "must": [{ "match": { "sidstOpdateret": "' + str(date) + '"}}]}}, "size":100}'
    url = 'http://distribution.virk.dk/offentliggoerelser/_search?scroll=1m'
    response = requests.post(url, headers=headers, data=query)
    results = json.loads(response.text)
    return results

def ContinueScroll(scroll_id):
    headers = {'Content-Type': 'application/json',}
    query = '{"scroll":"1m","scroll_id":"' + str(scroll_id) + '"}'
    url = 'http://distribution.virk.dk/_search/scroll'
    response = requests.post(url, headers=headers, data=query)
    results = json.loads(response.text)
    return results

def StopScroll(scroll_id):
    headers = {'Content-Type': 'application/json',}
    query = '{"scroll_id": "' + str(scroll_id) + '"}'
    url = 'http://distribution.virk.dk/_search/scroll '
    response = requests.delete(url, headers=headers, data=query)
    results = response.text
    return results

def CreateObjectList(json_list, objectList):
    for objects in json_list:
        objectList.append(objects)
    return objectList

def ProcessDay(date):
    objectList = []
    number_scroll = 0
    results = StartScroll(date)
    scroll_id = results['_scroll_id']
    objectList = CreateObjectList(results['hits']['hits'], objectList)
    while len(results['hits']['hits']) > 0:
        number_scroll = number_scroll + 1
        #print(number_scroll)
        results = ContinueScroll(scroll_id)
        objectList = CreateObjectList(results['hits']['hits'], objectList)
    StopScroll(scroll_id)
    return objectList

#ProcessDay('2022-07-08')