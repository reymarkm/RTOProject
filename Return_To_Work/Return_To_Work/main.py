from flask import Flask, render_template, redirect, url_for, request, session
from flask_mysqldb import MySQL
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from datetime import date
import MySQLdb.cursors
import re
import json
import requests
import bs4
import time
import urllib




app = Flask(__name__)
app.secret_key = '04131999'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'N0virus1'
app.config['MYSQL_DB'] = 'rto'

mysql = MySQL(app)

@app.route("/", methods=['GET', 'POST'])
def home():
    error = None
    if request.method == 'POST':
        inputuser = request.form['username']
        inputpassword = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE Username = %s AND Password = %s', (inputuser, inputpassword))
        # Fetch one record and return result
        account = cursor.fetchone()

        if account is not None:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['A_ID']
            session['username'] = account['Username']
            # Assign each value of fetched value into variables
            user = str(account['Username'])
            password = str(account['Password'])
            # Redirect to home page
            error = 'Welcome %s!' % (user)
            #return redirect(url_for('about'))
            return render_template('userProfile.html',error=error)
        else:
            # Account doesnt exist or username/password incorrect
            error = 'Incorrect Username/Password.'

    # Show the login form with message (if any)
    return render_template('index.html',error=error)
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        inputuser = request.form['username']
        inputpassword = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE Username = %s AND Password = %s', (inputuser, inputpassword))
        # Fetch one record and return result
        account = cursor.fetchone()

        if account is not None:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['A_ID']
            session['username'] = account['Username']
            # Assign each value of fetched value into variables
            user = str(account['Username'])
            password = str(account['Password'])
            # Redirect to home page
            error = 'Welcome %s!' % (user)
            #return redirect(url_for('about'))
            return render_template('userProfile.html',error=error)
        else:
            # Account doesnt exist or username/password incorrect
            error = 'Incorrect Username/Password.'

    # Show the login form with message (if any)
    return render_template('index.html',error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        inputFName = request.form['FName']
        inputLName = request.form['LName']
        inputEmail = request.form['Email']
        inputUName = request.form['UName']
        inputPWord = request.form['PWord']
        inputCPWord = request.form['CPWord']
        inputPNumber = request.form['PNumber']
        inputAddress = request.form['Address']
        inputCity = request.form['City']
        inputProvince = request.form['Province']
        if request.form.get('High') == '1':
            inputHigh = 1
        else:
            inputHigh = 0
        if request.form.get('Slight') == '1':
            inputSlight = 1
        else:
            inputSlight = 0
        if request.form.get('LHigh') == '1':
            inputLHigh = 1
        else:
            inputLHigh = 0
        if request.form['willingness'] == 'True':
            inputWillingness = 1
        else:
            inputWillingness = 0
        inputProdMachine = request.form['prodMachine']
        inputTranspo = request.form['transpoAvail']
        inputDepartment = request.form['Department']
        inputTeam = request.form['Team']
        today = date.today()
        inputDate = today.strftime("%Y/%m/%d")

        if inputPWord == inputCPWord:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM accounts WHERE Username = %s AND Password = %s', (inputUName,inputPWord))
            user_exists = cursor.fetchone()
            if user_exists:
                error='A user with the same Username already exists in the database.'
            else:
                cursor.execute('INSERT INTO accounts (Username,Password) values (%s,%s)', (inputUName,inputPWord))
                mysql.connection.commit()
                cursor.execute('INSERT INTO rto (FirstName,LastName,Email,Barangay,City,Province,High_Risk,Slight_Risk,Living_With_High_Risk,Production_Machine,Transportation_Availability,Department,Team,Wilingness,Last_Update) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', (inputFName,inputLName,inputEmail,inputAddress,inputCity,inputProvince,int(inputHigh),int(inputSlight),int(inputLHigh),inputProdMachine,inputTranspo,inputDepartment,inputTeam,int(inputWillingness),inputDate))
                mysql.connection.commit()
        else:
            error = 'Password does not match.'

    return render_template("register.html",error=error)


@app.route("/about")
def about():
    return render_template("About.html")

@app.route("/update", methods=['GET', 'POST'])
def update():
    link = "https://api.covidph.info/api/summary/v4/residence/province"
    r = requests.get(link)
    test = r.json()
    for num in test:
        holder = str(num).replace("\'", "\"")
        result = json.loads(holder)
        areaid = result['areaId']
        Province = result['name']
        Count = result['count']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM province WHERE areaid = %s AND province = %s AND provincecasecount = %s', (areaid, Province, Count))
        flag1 = cursor.fetchone()
        if flag1 is not None:
            cursor.close()
        else:
            cursor.execute('SELECT * FROM province WHERE areaid = %s AND province = %s', (areaid, Province))
            flag2 = cursor.fetchone()
            if flag2 is not None:
                cursor.execute('UPDATE province SET provincecasecount=%s WHERE areaid=%s AND province=%s', (Count, areaid, Province))
                mysql.connection.commit()
            else:
                cursor.execute('INSERT INTO province (areaid,province,provincecasecount) values (%s,%s,%s)', (areaid, Province, Count))
                mysql.connection.commit()
        cursor.close


    link1 = "https://api.covidph.info/api/summary/v4/residence/city"
    r1 = requests.get(link1)
    test1 = r1.json()
    for num in test1:
        print(num['name'])
        holder1 = str(num).replace("\'", "\"")
        holder2 = holder1.replace("T\"Boli","T\'Boli")
        holder3 = holder2.replace("T\"BOLI","T\'BOLI")
        holder4 = holder3.replace("M\"Lang","M\'Lang")
        holder5 = holder4.replace("M\"LANG","M\'LANG")
        result1 = json.loads(holder5)
        areaid = result1['subAreaOfAreaId']
        City = result1['name']
        Count = result1['count']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM city WHERE subareaid = %s AND city = %s AND citycasecount = %s', (areaid, City, Count))
        flag1 = cursor.fetchone()
        if flag1 is not None:
            cursor.close()
        else:
            cursor.execute('SELECT * FROM city WHERE subareaid = %s AND city = %s', (areaid, City))
            flag2 = cursor.fetchone()
            if flag2 is not None:
                cursor.execute('UPDATE city SET citycasecount=%s WHERE subareaid=%s AND city=%s', (Count, areaid, City))
                mysql.connection.commit()
            else:
                cursor.execute('INSERT INTO city (subareaid,city,citycasecount) values (%s,%s,%s)', (areaid, City, Count))
                mysql.connection.commit()
        cursor.close

    return render_template("update.html",error=test)

if __name__ == "__main__":
    app.run(debug=True)