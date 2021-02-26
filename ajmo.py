from flask import Flask, render_template, json, request, redirect, session, jsonify
from flask import Markup
from flask_mysqldb import MySQL
from flask import session, request
from flask import make_response, abort
from datetime import datetime
from datetime import date
import json
import requests
import datetime as dt

mysql = MySQL()
app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_USER'] = 'telemetryuser'
app.config['MYSQL_PASSWORD'] = 'telemetryuser123'
app.config['MYSQL_DB'] = 'telemetryDB'
app.config['MYSQL_HOST'] = 'localhost'
mysql.init_app(app)


@app.route('/')
def main():
    return render_template('index.html')

@app.route('/temperature')
def chartTemperature():
    # labels = ['19:48:56', '19:58:56', '20:08:56', '20:18:56', '20:28:56', '20:38:56']
    # data = [36.7, 36.8, 36.6, 36.5, 36.4, 36.9]
    labels, data = get_todays_measurements("Temperature")
    return render_template('temperature.html', labels=labels, data=data)

@app.route('/heartrate')
def chartHeartrate():
    return render_template('heartrate.html')

@app.route('/battery')
def chartBattery():
    return render_template('battery.html')


@app.route('/map')
def chartMap():
    return render_template('map.html')

@app.route('/api/telemetry/measurement', methods=['POST'])
def post_measurement():
    if not request.json or not 'DeviceId' in request.json:
        abort(400)
    else:
        content = request.json
    measurement = {
        'DeviceId' : content['DeviceId'],
        'SensorName' : content['SensorName'],
        'SensorValue' : content['SensorValue'],
        'CreatedOn' : datetime.now()
    }
    return add_measurement(measurement)

@app.route('/api/telemetry/measurement', methods=['GET'])
def get_measurement():
    content = request.args
    if not content or not content.get('DeviceId') or not content.get('SensorName'):
        abort(400)
    else:
        conn = mysql.connect
        cursor =conn.cursor()

        cmd = "SELECT DeviceId, CreatedOn, SensorValue FROM Measurement WHERE SensorName = %s AND CreatedOn >= %s AND CreatedOn < %s"
        params = (content.get('SensorName'), content.get('dateFrom'), content.get('dateTo'))
        cursor.execute(cmd, params)
        rows = cursor.fetchall()

        data = list()

        for row in rows:
            data.append({"DeviceId": row[0], "CreatedOn": row[1], "SensorValue": str(row[2])})

        return jsonify(data)

@app.route('/api/telemetry/devices', methods=['GET'])
def get_devices():
    conn = mysql.connect
    cursor =conn.cursor()

    cursor.execute("SELECT DeviceId, Name, latitude, longitude FROM Device")
    rows = cursor.fetchall()

    data = list()

    for row in rows:
        data.append({"DeviceId": row[0], "Name": row[1], "latitude": str(row[2]), "longitude": str(row[3])})

    return jsonify(data)

def add_measurement(data):
    conn = mysql.connect
    cursor =conn.cursor()
    try:
        cmd = "INSERT INTO Measurement (DeviceId, SensorName, SensorValue, CreatedOn) VALUES (%s, %s, %s, %s)"
        params = (data["DeviceId"], data["SensorName"], data["SensorValue"], data["CreatedOn"])
        cursor.execute(cmd, params)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print ("Error: unable to fetch items", e)
    return "200"

def get_todays_measurements(sensorName):
    today = date.today()
    date_from = datetime(today.year, today.month, today.day, 0, 0, 0).strftime('%Y-%m-%d %H:%M:%S')
    date_to = datetime(today.year, today.month, today.day, 23, 59, 59).strftime('%Y-%m-%d %H:%M:%S')
    args = '?' + "DeviceId=1&" + "dateFrom=" + date_from + '&' + "dateTo=" + date_to + '&' + "SensorName=" + sensorName
    GET_URL = "http://algebra-iot-zbodulja.westeurope.cloudapp.azure.com/api/telemetry/measurement" + args
    r = requests.get(url=GET_URL)
    if(r.status_code == 200):
        data = json.loads(r.json())
        labels = list()
        labels = [parse_datetime_to_time(measurement["CreatedOn"]) for measurement in data]
        sensor_data = [measurement["SensorValue"] for measurement in data]
        
        return labels, sensor_data
        
        
    else:
        print("Error " + str(r.status_code))
        return list(), list()

def parse_datetime_to_time(date_time):
    date_time_obj = dt.datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
    return date_time_obj.strftime('%H:%M:%S')
    
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)

