import requests
import json
from datetime import datetime

GET_URL = "http://algebra-iot-zbodulja.westeurope.cloudapp.azure.com/api/telemetry/get"
GET_PARAMS = {"Time": "2021-02-24 23:03:08"}

POST_URL = "http://algebra-iot-zbodulja.westeurope.cloudapp.azure.com/api/telemetry/post"
POST_PARAMS = {"DeviceId": "1", "SensorName": "Temperature", "SensorValue":"35.7", "CreatedOn": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

def get_request():
    r = requests.get(url=GET_URL, json=GET_PARAMS)
    if(r.status_code == 200):
        data = r.json()
        print(data)
        
    else:
        print("Error " + str(r.status_code))


def post_request():
    r = requests.post(url=POST_URL, json=POST_PARAMS)
    if(r.status_code == 200):
        print("Posted data successfully")
    
    else:
        print("Error " + str(r.status_code))

if __name__ == "__main__":
    # get_request()
    post_request()