from flask import Flask, request, jsonify
import psycopg2
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)

metrics = PrometheusMetrics(app)
metrics.info('app_info_login_and_register', 'Application info', version='1.0.0')

@app.before_first_request
def before_first_request_func():

    db = psycopg2.connect(host='db_login', port=5432, user='postgres', password='postgres', dbname='login_info_db')

    cursor = db.cursor()
    cursor.execute(
        """
        CREATE TABLE if not exists users_login_info (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(30) NOT NULL,
                last_name VARCHAR(30) NOT NULL,
                username VARCHAR(30) NOT NULL UNIQUE,
                password VARCHAR(30) NOT NULL,
                registration_timestamp TIMESTAMP NOT NULL

        )
        """)
    if cursor is not None:
        cursor.close()

    db.commit()
    if db is not None:
        db.close()

# Function for adding new line into the database
def addDataToDatabase(firstName, lastName, username, password, registrationTimestamp):

    db = psycopg2.connect(host='db_login', port=5432, user='postgres', password='postgres', dbname='login_info_db')

    cursor = db.cursor()
    cursor.execute("select * from users_login_info where username = %s", (username,))
    record = cursor.fetchall()
    if not record:
        try:
            cursor.execute("INSERT INTO users_login_info(first_name, last_name, username, password, registration_timestamp) VALUES(%s, %s, %s, %s, %s) RETURNING id", (firstName, lastName, username, password, registrationTimestamp))
            lineID = cursor.fetchone()[0]
            db.commit()
        except:
            lineID = -1
    else:
        lineID = -2
    if cursor is not None:
        cursor.close()
    if db is not None:
        db.close()

    return lineID

def is_user_correct(username, password):

    db = psycopg2.connect(host='db_login', port=5432, user='postgres', password='postgres', dbname='login_info_db')
    cursor = db.cursor()
    cursor.execute("select * from users_login_info where username = %s and password = %s", (username, password))
    record = cursor.fetchall()
    if not record:
        return False
    else:
        return True
  

@app.route('/', methods=['POST'])
def take_data():
    
    status = ""
    error = ""

    jsonData = request.get_json()
    command = jsonData['command']
    if command == "CheckLogin":
        username = jsonData['username']
        password = jsonData['password']
        allow = is_user_correct(username, password)
        if allow:
            status = "Success"
            error = "Nothing"
        else:
            status = "Failed"
            error = "Username or Password is incorrect."
    
    elif command == "Register":
        firstName = jsonData['firstname']
        lastName = jsonData['lastname']
        username = jsonData['username']
        password = jsonData['password']
        registrationDate = jsonData['registrationdate']
        registrationTime = jsonData['registrationtime']

        registrationTimestamp = registrationDate + " " + registrationTime
        lineID = addDataToDatabase(firstName, lastName, username, password, registrationTimestamp)

        if lineID == -1:
            status = "Failed"
            error = "Error at adding the new account."
        elif lineID == -2:
            status = "Failed"
            error = "User already exists"
        else:
            status = "Success"
            error = "Nothing"
    
    return jsonify({"status" : status, "error" : error})

if __name__ == "__main__":
    app.run(host="0.0.0.0")