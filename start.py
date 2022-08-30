import requests
import json
import sys
from datetime import date, timedelta, datetime
from database import Get_Rebuild_Date, Save_Json_To_DB, Store_Progress
from scanscroll import ProcessDay
from time import sleep

def Get_JSON_Date(page, date, pagesize): # Retrieves companys where last updated on date
    headers = {'Content-Type': 'application/json',}
    query = '{ "from":' + str(page) + ', "size":' + str(pagesize) + ', "query": { "bool": { "must": [{ "match": { "sidstOpdateret": "' + str(date) + '"}}]}}}'
    response = requests.get('http://distribution.virk.dk/offentliggoerelser/_search', headers=headers, data=query)
    results = json.loads(response.text)
    return results
    
def Process_JSON(json_data):
    for object in json_data:
        sagsnummer = object['_source']['sagsNummer']
        cvr = object['_source']['cvrNummer']
        startDato = object['_source']['regnskab']['regnskabsperiode']['startDato']
        slutDato = object['_source']['regnskab']['regnskabsperiode']['slutDato']
        url = None
        for item in object['_source']['dokumenter']:
            if item['dokumentMimeType'] == 'application/xml' and item['dokumentType'] == 'AARSRAPPORT':
                url = item['dokumentUrl']
        Save_Json_To_DB(sagsnummer, cvr, startDato, slutDato, url)

def GetStartingDate():
    cmd_arg = ""
    end_date = date.today() - timedelta(days=3)
    if len(sys.argv) > 1:
        cmd_arg = sys.argv[1]
    if cmd_arg == '-c':
        date_to_process = Get_Rebuild_Date()
        print('Continuing rebuild from ' + str(date_to_process))
    elif cmd_arg == '-n':
        date_to_process = date.today()
        print('Starting a fresh rebuild...')
        end_date = date.today() - timedelta(days=365*40)
    else:
        date_to_process = date.today()
        end_date = date.today() - timedelta(days=3)
    return date_to_process, end_date

def Subtract_One_Day(date_to_process):
    if isinstance(date_to_process, str) == True:
        date_to_process = datetime.strptime(date_to_process, '%Y-%m-%d')
        date_to_process = date_to_process.date()
    date_to_process = date_to_process - timedelta(days=1)
    return date_to_process    


def Main():
    date_to_process, end_date = GetStartingDate()
    while True:
        print('Processing: ' + str(date_to_process))
        objectList = ProcessDay(date_to_process)
        Process_JSON(objectList)
        date_to_process = Subtract_One_Day(date_to_process)
        Store_Progress(date_to_process)
        if  date_to_process < end_date:
            break

if __name__ == '__main__':
    loop = True
    while loop == True: 
        Main()
        print(f"Restarting loop 6000 seconds...")
        sleep(6000)  