from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

db = None

@app.before_first_request
def before_first_request_func():

    global db
    db = psycopg2.connect(host='db_login', port=5432, user='postgres', password='postgres', dbname='login_info_db')
    #db = psycopg2.connect(host='127.0.0.1', port=5432, user='postgres', password='postgres', dbname='login_info_db')

    cursor = db.cursor()
    cursor.execute(
        """
        CREATE TABLE if not exists users_login_info (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(30) NOT NULL,
                last_name VARCHAR(30) NOT NULL,
                username VARCHAR(30) NOT NULL UNIQUE,
                password VARCHAR(30) NOT NULL,
                registration_date DATE NOT NULL,
                registration_time TIME NOT NULL

        )
        """)
    cursor.close()
    db.commit()
    if db is not None:
        db.close()

# Function for adding new line into the database
def addDataToDatabase(firstName, lastName, username, password, registrationDate, registrationTime):
    global db
    db = psycopg2.connect(host='db_login', port=5432, user='postgres', password='postgres', dbname='login_info_db')
    #db = psycopg2.connect(host='127.0.0.1', port=5432, user='postgres', password='postgres', dbname='login_info_db')
    cursor = db.cursor()
    cursor.execute("select * from users_login_info where username = %s", (username,))
    record = cursor.fetchall()
    if not record:
        try:
            cursor.execute("INSERT INTO users_login_info(first_name, last_name, username, password, registration_date, registration_time) VALUES(%s, %s, %s, %s, %s, %s) RETURNING id", (firstName, lastName, username, password, registrationDate, registrationTime))
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
    global db
    db = psycopg2.connect(host='db_login', port=5432, user='postgres', password='postgres', dbname='login_info_db')
    cursor = db.cursor()
    cursor.execute("select * from users_login_info where username = %s and password = %s", (username, password))
    record = cursor.fetchall()
    if not record:
        return False
    else:
        return True

"""
@app.route('/', methods=['GET'])
def check_login():
    
    jsonData = request.get_json()
    username = jsonData['Username']
    password = jsonData['Password']
    allow = is_user_correct(username, password)
    if allow:
        return jsonify({'Result' : "OK", "Username" : username, "Password" : password})
    else:
        return jsonify({'Result' : "NOT OK", "Username" : username, "Password" : password})
"""    

@app.route('/', methods=['POST'])
def take_data():
    
    status = ""
    error = ""

    jsonData = request.get_json()
    command = jsonData['Command']
    if command == "CheckLogin":
        username = jsonData['Username']
        password = jsonData['Password']
        allow = is_user_correct(username, password)
        if allow:
            status = "Success"
            error = "Nothing"
        else:
            status = "Failed"
            error = "Username or Password is incorrect."
    
    elif command == "Register":
        firstName = jsonData['FirstName']
        lastName = jsonData['LastName']
        username = jsonData['Username']
        password = jsonData['Password']
        registrationDate = jsonData['RegistrationDate']
        registrationTime = jsonData['RegistrationTime']
        lineID = addDataToDatabase(firstName, lastName, username, password, registrationDate, registrationTime)

        if lineID == -1:
            status = "Failed"
            error = "Error at adding the new account."
        elif lineID == -2:
            status = "Failed"
            error = "User already exists"
        else:
            status = "Success"
            error = "Nothing"
    
    return jsonify({"Status" : status, "Error" : error})
    #return jsonify({'Result' : aux, 'FirstName' : firstName, 'LastName' : lastName, 'Username' : username, 'Password' : password, 'RegistrationDate' : registrationDate, 'RegistrationTime' : registrationTime, 'LineID' : lineID})

if __name__ == "__main__":
    app.run(host="0.0.0.0")