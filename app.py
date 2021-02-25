from flask import Flask
from flask import jsonify
from flask_mysqldb import MySQL
from flask import request
import datetime
import json
import decimal

class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal) or isinstance(obj, (datetime.date, datetime.datetime)): 
            return str(obj)
        return super(Encoder, self).default(obj)

mysql = MySQL()
app  = Flask(__name__)
app.json_encoder = Encoder

app.config['MYSQL_USER'] = 'telemetryuser'
app.config['MYSQL_PASSWORD'] = 'telemetryuser123'
app.config['MYSQL_DB'] = 'telemetryDB'
app.config['MYSQL_HOST']  ='localhost'
mysql.init_app(app)

@app.route('/api/telemetry/get', methods=['GET'])
def get_all():
    data = request.get_json()
    print(data)

    conn = mysql.connect
    cursor = conn.cursor()

    cmd = "SELECT * FROM Measurement WHERE CreatedOn > %s AND CreatedOn < %s AND DeviceId = %s AND SensorName = %s"
    params = (data["dateFrom"], data["dateTo"], data["DeviceId"], data["SensorName"])

    cursor.execute(cmd, params)
    rows = cursor.fetchall()

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'measurements': rows})
    # return json.dumps(rows, cls = Encoder)


@app.route('/api/telemetry/post', methods=['POST'])
def insert_measurement():
    new_measurement = request.get_json()
    print(new_measurement)

    conn = mysql.connect
    cursor = conn.cursor()


    # createdOn = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cmd = "INSERT INTO Measurement (DeviceId, SensorName, SensorValue, CreatedOn) VALUES (%s, %s, %s, %s)"
    params = (new_measurement["DeviceId"], new_measurement['SensorName'], new_measurement['SensorValue'], new_measurement["CreatedOn"])

    cursor.execute(cmd, params)

    conn.commit()
    cursor.close()
    conn.close()

    return "200"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
