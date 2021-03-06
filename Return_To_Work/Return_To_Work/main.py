from flask import Flask, render_template, redirect, url_for, request, session, jsonify
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
from math import sin, cos, sqrt, atan2, radians
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
    if session.get('errorlogin') is not None:
        error = str(session['errorlogin'])
    else:
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
            cursor.execute('SELECT * FROM rto WHERE ID = %s' % (str(account['A_ID'])))
            temp = cursor.fetchone()
            session['team'] = temp['Team']
            session['errorlogin'] = None
            cursor.close()
            if str(account['Role']) == 'User':
                return redirect(url_for('userprofile',error=error))
            if str(account['Role']) == 'Manager':
                update()
                return redirect(url_for('manager'))
        else:
            # Account doesnt exist or username/password incorrect
            error = 'Incorrect Username/Password.'
            session['errorlogin'] = error
            cursor.close()
            return render_template('index.html',error=error)
    # Show the login form with message (if any)
    return render_template('index.html')
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if session.get('errorlogin') is not None:
        error = str(session['errorlogin'])
    else:
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
            cursor.execute('SELECT * FROM rto WHERE ID = %s' % (str(account['A_ID'])))
            temp = cursor.fetchone()
            session['team'] = temp['Team']
            session['errorlogin'] = None
            cursor.close()
            if str(account['Role']) == 'User':
                return redirect(url_for('userprofile',error=error))
            if str(account['Role']) == 'Manager':
                update()
                return redirect(url_for('manager'))
        else:
            # Account doesnt exist or username/password incorrect
            error = 'Incorrect Username/Password.'
            session['errorlogin'] = error
            cursor.close()
            return render_template('index.html',error=error)
    # Show the login form with message (if any)
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    error = None

    if session.get('errorreg') is not None:
        error = str(session['errorreg'])
    else:
        error = None

    #Get Cities
    temp = cursor.execute('SELECT * FROM city ORDER BY city ASC')   
    tempcity = cursor.fetchall()
    lista = list()
    listx = list()
    for x in tempcity:
        lista.append(x['city']) 
        listx.append(x['idcity'])

    #Get Cities Area ID
    temp = cursor.execute('SELECT subareaid FROM city ORDER BY city ASC')   
    tempcity = cursor.fetchall()
    listaa = list()
    for x in tempcity:
        dummya = str(x['subareaid']).replace(".", "")
        dummyb = dummya.replace("_1", "")
        listaa.append(dummyb) 

    #Get Provinces
    temp = cursor.execute('SELECT province FROM province ORDER BY province ASC')   
    tempcity = cursor.fetchall()
    listb = list()
    for x in tempcity:
        listb.append(x['province']) 

    #Get Provinces' Area ID
    temp = cursor.execute('SELECT areaid FROM province ORDER BY province ASC')   
    tempcity = cursor.fetchall()
    listbb = list()
    for x in tempcity:
        dummyc = str(x['areaid']).replace(".", "")
        dummyd = dummyc.replace("_1", "")
        listbb.append(dummyd) 

    if request.method == 'POST':       
        inputFName = request.form['FName']
        inputLName = request.form['LName']
        inputEmail = request.form['Email']
        inputUName = request.form['UName']
        if inputUName == ' ':
            error = 'Username cannot be blank.'
            session['errorreg'] = error
            cursor.close()
            return redirect(url_for('register',error=error))
        inputPWord = request.form['PWord']
        if inputPWord == '':
            error = 'Password cannot be blank.'
            session['errorreg'] = error
            cursor.close()
            return redirect(url_for('register',error=error))
        inputCPWord = request.form['CPWord']
        inputAccountRole = 'User'
        inputBarangay = request.form['Barangay']
        inputCityID = request.form['City']
        cursor.execute('SELECT * FROM city WHERE idcity = %s', [inputCityID]) 
        tempCity = cursor.fetchone()
        inputCity = str(tempCity['city'])
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
        if request.form['wilingness'] == 'True':
            inputWillingness = 1
        else:
            inputWillingness = 0
        inputProdMachine = request.form['prodMachine']
        inputTranspo = request.form['transpoAvail']
        inputDepartment = request.form['Department']
        inputTeam = request.form['Team']
        today = date.today()
        inputDate = today.strftime("%Y/%m/%d")
        inputProcessed = 0

        #Compute Distance from Barangay to RBC
        container = '%s, %s, %s', (inputBarangay,inputCity,inputProvince)
        tempresult = str(container).replace("#", "")
        result = str(tempresult).replace(" ", "+")
        link = "https://maps.googleapis.com/maps/api/geocode/json?&address=%s&key=AIzaSyA2voIMNubql1et8Uei3ZCLPipEXeXiLk0" % result
        r = requests.get(link)
        error = r.json()
        temp = error['results']
        temp1 = temp[0]

        #Distance Matrix API
        origin = "%s,%s" % (temp1['geometry']['location']['lat'],temp1['geometry']['location']['lng'])
        destination = "14.590148,121.067947"
        link2 = "https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins=%s&destinations=%s&mode=driving&key=AIzaSyC2zlaHWthM3MOraTlpAGw7hBF6T8RnmPU" % (origin,destination)
        r2 = requests.get(link2)
        dummy = r2.json()
        dummy1 = dummy['rows']
        dummy2 = dummy1[0]
        dummy3 = dummy2['elements']
        dummy4 = dummy3[0]
        APIDistance = dummy4['distance']['text']
        APIDistance = str(APIDistance.replace(",",""))
        CalculateDistance = round(float(str(APIDistance).replace(" km","")),2)

        if inputPWord == inputCPWord:
            #Check if record already exists
            cursor.execute('SELECT * FROM accounts WHERE Username = %s', [inputUName])
            user_exists = cursor.fetchone()
            if user_exists:
                error='A user with the same Username already exists in the database.'
                session['errorreg'] = error
                cursor.close()
                return redirect(url_for('register',error=error))
            else:
                #Add Account into DB
                cursor.execute('INSERT INTO accounts (Username,Password,Role) values (%s,%s,%s)', (inputUName,inputPWord,inputAccountRole))
                mysql.connection.commit()
                #Add details into DB
                cursor.execute('INSERT INTO rto (FirstName,LastName,Email,Barangay,City,CityID,Province,High_Risk,Slight_Risk,Living_With_High_Risk,Production_Machine,Transportation_Availability,Department,Team,Wilingness,Last_Update,Processed,Distance,RTO) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', (inputFName,inputLName,inputEmail,inputBarangay,inputCity,int(inputCityID),inputProvince,int(inputHigh),int(inputSlight),int(inputLHigh),inputProdMachine,inputTranspo,inputDepartment,inputTeam,int(inputWillingness),inputDate,int(inputProcessed),CalculateDistance,0))
                mysql.connection.commit()
                cursor.close()
                session['errorreg'] = None
                return redirect(url_for('login'))
        else:
            error = 'Password does not match.'
            session['errorreg'] = error
            cursor.close()
            return render_template("register.html",error=error,list1=zip(lista,listaa,listx),list2=zip(listb,listbb))

    return render_template("register.html",error=error,list1=zip(lista,listaa,listx),list2=zip(listb,listbb))

@app.route("/userprofile", methods=['GET', 'POST'])
def userprofile():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    error = None
    Holder = None
    userID = str(session['id'])

    if session.get('errorprofile') is not None:
        error = str(session['errorprofile'])
    else:
        error = None
    

    #Get Cities
    temp = cursor.execute('SELECT * FROM city ORDER BY city ASC')   
    tempcity = cursor.fetchall()
    lista = list()
    listx = list()
    for x in tempcity:
        lista.append(x['city']) 
        listx.append(x['idcity'])

    #Get Cities Area ID
    temp = cursor.execute('SELECT subareaid FROM city ORDER BY city ASC')   
    tempcity = cursor.fetchall()
    listaa = list()
    for x in tempcity:
        dummya = str(x['subareaid']).replace(".", "")
        dummyb = dummya.replace("_1", "")
        listaa.append(dummyb) 

    #Get Provinces
    temp = cursor.execute('SELECT province FROM province ORDER BY province ASC')   
    tempcity = cursor.fetchall()
    listb = list()
    for x in tempcity:
        listb.append(x['province']) 

    #Get Provinces' Area ID
    temp = cursor.execute('SELECT areaid FROM province ORDER BY province ASC')   
    tempcity = cursor.fetchall()
    listbb = list()
    for x in tempcity:
        dummyc = str(x['areaid']).replace(".", "")
        dummyd = dummyc.replace("_1", "")
        listbb.append(dummyd) 

    if request.method == 'GET':
        cursor.execute('SELECT * FROM accounts WHERE A_ID = %s' % (userID))
        account = cursor.fetchone()
        cursor.execute('SELECT * FROM rto WHERE ID = %s' % (userID))
        RTORecord = cursor.fetchone()

        inputFName = RTORecord['FirstName']
        inputLName = RTORecord['LastName']
        inputEmail = RTORecord['Email']
        inputUName = account['Username']
        inputPWord = account['Password']
        inputCPWord = inputPWord
        inputBarangay = RTORecord['Barangay']
        inputCity = RTORecord['CityID']
        inputProvince = RTORecord['Province']
        inputHigh = RTORecord['High_Risk']
        inputSlight = RTORecord['Slight_Risk']
        inputLHigh = RTORecord['Living_With_High_Risk']
        inputWilingness = RTORecord['Wilingness']
        inputProdMachine = RTORecord['Production_Machine']
        inputTranspo = RTORecord['Transportation_Availability']
        inputDepartment = RTORecord['Department']
        inputTeam = RTORecord['Team']

      
        Holder = list()
        Holder.append(inputFName)
        Holder.append(inputLName)
        Holder.append(inputEmail)
        Holder.append(inputUName)
        Holder.append(inputPWord)
        Holder.append(inputCPWord)
        Holder.append(inputBarangay)
        Holder.append(inputCity)
        Holder.append(inputProvince)
        Holder.append(inputHigh)
        Holder.append(inputSlight)
        Holder.append(inputLHigh)
        Holder.append(inputWilingness)
        Holder.append(inputProdMachine)
        Holder.append(inputTranspo)
        Holder.append(inputDepartment)
        Holder.append(inputTeam)
       
    if request.method == 'POST': 
        mode = request.form['modes']
        if mode == 'Update':
            inputFName = request.form['FName']
            inputLName = request.form['LName']
            inputEmail = request.form['Email']
            inputUName = request.form['UName']
            if inputUName == ' ':
                error = 'Username cannot be blank.'
                session['errorreg'] = error
                cursor.close()
                return redirect(url_for('register',error=error))
            inputPWord = request.form['PWord']
            if inputPWord == '':
                error = 'Password cannot be blank.'
                session['errorprofile'] = error
                cursor.close()
                return redirect(url_for('userprofile',error1=error))
            inputCPWord = request.form['CPWord']
            inputBarangay = request.form['Barangay']
            inputCityID = request.form['City']
            cursor.execute('SELECT * FROM city WHERE idcity = %s', [inputCityID]) 
            tempCity = cursor.fetchone()
            inputCity = str(tempCity['city'])
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
            if request.form['wilingness'] == 'True':
                inputWillingness = 1
            else:
                inputWillingness = 0
            inputProdMachine = request.form['prodMachine']
            inputTranspo = request.form['transpoAvail']
            inputDepartment = request.form['Department']
            inputTeam = request.form['Team']
            today = date.today()
            inputDate = today.strftime("%Y/%m/%d")
            inputProcessed = 0

            #Compute Distance from Barangay to RBC
            container = '%s, %s, %s', (inputBarangay,inputCity,inputProvince)
            tempresult = str(container).replace("#", "")
            result = str(tempresult).replace(" ", "+")
            link = "https://maps.googleapis.com/maps/api/geocode/json?&address=%s&key=AIzaSyA2voIMNubql1et8Uei3ZCLPipEXeXiLk0" % result
            r = requests.get(link)
            error = r.json()
            temp = error['results']
            temp1 = temp[0]

            #Distance Matrix API
            origin = "%s,%s" % (temp1['geometry']['location']['lat'],temp1['geometry']['location']['lng'])
            destination = "14.590148,121.067947"
            link2 = "https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins=%s&destinations=%s&mode=driving&key=AIzaSyC2zlaHWthM3MOraTlpAGw7hBF6T8RnmPU" % (origin,destination)
            r2 = requests.get(link2)
            dummy = r2.json()
            dummy1 = dummy['rows']
            dummy2 = dummy1[0]
            dummy3 = dummy2['elements']
            dummy4 = dummy3[0]
            APIDistance = dummy4['distance']['text']
            APIDistance = str(APIDistance.replace(",",""))
            CalculateDistance = round(float(str(APIDistance).replace(" km","")),2)

            if inputPWord == inputCPWord:
                cursor.execute('SELECT * FROM accounts WHERE Username = %s', [inputUName])
                print(inputUName)
                user_exists = cursor.fetchone()
                if user_exists:
                    cursor.execute('SELECT * FROM accounts WHERE Username=%s AND A_ID=%s', (inputUName,str(session['id'])))
                    same_user = cursor.fetchone()
                    if same_user:
                        #Add Account into DB
                        cursor.execute('UPDATE accounts SET Password=%s, Username=%s WHERE A_ID=%s', (inputPWord,inputUName,str(session['id'])))
                        mysql.connection.commit()
                        #Add details into DB 
                        cursor.execute('UPDATE rto SET FirstName=%s, LastName=%s, Email=%s, Barangay=%s, City=%s, CityID=%s, Province=%s, High_Risk=%s, Slight_Risk=%s, Living_With_High_Risk=%s, Production_Machine=%s, Transportation_Availability=%s, Department=%s, Team=%s, Wilingness=%s, Last_Update=%s, Processed=%s, Distance=%s WHERE ID=%s', (inputFName,inputLName,inputEmail,inputBarangay,inputCity,int(inputCityID),inputProvince,int(inputHigh),int(inputSlight),int(inputLHigh),inputProdMachine,inputTranspo,inputDepartment,inputTeam,int(inputWillingness),inputDate,int(inputProcessed),CalculateDistance,int(userID)))
                        mysql.connection.commit()
                        cursor.close()
                        session['errorprofile'] = None
                        return redirect(url_for('userprofile'))
                    else:
                        error = 'A user with the same Username already exists in the database.'
                        cursor.close()
                        session['errorprofile'] = error
                        return redirect(url_for('userprofile'))
                else:
                    #Add Account into DB
                    cursor.execute('UPDATE accounts SET Password=%s, Username=%s WHERE A_ID=%s', (inputPWord,inputUName,str(session['id'])))
                    mysql.connection.commit()
                    #Add details into DB 
                    cursor.execute('UPDATE rto SET FirstName=%s, LastName=%s, Email=%s, Barangay=%s, City=%s, CityID=%s, Province=%s, High_Risk=%s, Slight_Risk=%s, Living_With_High_Risk=%s, Production_Machine=%s, Transportation_Availability=%s, Department=%s, Team=%s, Wilingness=%s, Last_Update=%s, Processed=%s, Distance=%s WHERE ID=%s', (inputFName,inputLName,inputEmail,inputBarangay,inputCity,int(inputCityID),inputProvince,int(inputHigh),int(inputSlight),int(inputLHigh),inputProdMachine,inputTranspo,inputDepartment,inputTeam,int(inputWillingness),inputDate,int(inputProcessed),CalculateDistance,int(userID)))
                    mysql.connection.commit()
                    cursor.close()
                    session['errorprofile'] = None
                    return redirect(url_for('userprofile'))
            else:
                error = 'Password does not match.'
                cursor.close()
                session['errorprofile'] = error
                return redirect(url_for('userprofile'))

        if mode == 'Logout':
            tmp = []
            tmp = session.keys()
            for x in tmp:
                session['%s' % x] = None
            return redirect(url_for('login'))

    return render_template("userProfile.html",error=error,list1=zip(lista,listaa,listx),list2=zip(listb,listbb),c=Holder)

@app.route("/update", methods=['GET', 'POST'])
def update():
    #Get Data from Source (Provinces)
    link = "https://api.covidph.info/api/summary/v4/residence/province"
    r = requests.get(link)
    test = r.json()
    for result in test:
        areaid = result['areaId']
        Province = result['name']
        Count = result['count']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #Add Data to DB
        cursor.execute('SELECT * FROM province WHERE areaid = %s AND province = %s AND provincecasecount = %s', (areaid, Province, Count))
        flag1 = cursor.fetchone()
        if flag1 is not None:
            cursor.close()
        else:
            #Check if Data already exists in DB
            cursor.execute('SELECT * FROM province WHERE areaid = %s AND province = %s', (areaid, Province))
            flag2 = cursor.fetchone()
            if flag2 is not None:
                #Update existing Data
                cursor.execute('UPDATE province SET provincecasecount=%s WHERE areaid=%s AND province=%s', (Count, areaid, Province))
                mysql.connection.commit()
            else:
                #Add New Data
                cursor.execute('INSERT INTO province (areaid,province,provincecasecount) values (%s,%s,%s)', (areaid, Province, Count))
                mysql.connection.commit()
        cursor.close


    #Get Data from Source (Cities)
    link1 = "https://api.covidph.info/api/summary/v4/residence/city"
    r1 = requests.get(link1)
    test1 = r1.json()
    for result1 in test1:
        areaid = result1['subAreaOfAreaId']
        City = result1['name']
        Count = result1['count']
        Status = result1['quarantineLevel']
        print(result1['name'])
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #Add Data to DB
        cursor.execute('SELECT * FROM city WHERE subareaid = %s AND city = %s AND citycasecount = %s', (areaid, City, Count))
        flag1 = cursor.fetchone()
        if flag1 is not None:
            cursor.close()
        else:
            #Check if Data already exists in DB
            cursor.execute('SELECT * FROM city WHERE subareaid = %s AND city = %s', (areaid, City))
            flag2 = cursor.fetchone()
            if flag2 is not None:
                #Update existing Data
                cursor.execute('UPDATE city SET citycasecount=%s WHERE subareaid=%s AND city=%s', (Count, areaid, City))
                mysql.connection.commit()
            else:
                #Add New Data
                cursor.execute('INSERT INTO city (subareaid,city,citycasecount,citystatus) values (%s,%s,%s,%s)', (areaid, City, Count, Status))
                mysql.connection.commit()
        cursor.close

    return render_template("update.html",error=test)

@app.route("/manager", methods=['GET', 'POST'])
def manager():
    Holder = list()
    Output = None
    listCheckbox = list()

    temperror = []
    if session.get('errorweights') is not None:
        error = session['errorweights']
    else:
        error = None

    if request.method == 'GET':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM weights')
        container = cursor.fetchone()
        Holder.append(str(container['ECQ']))
        Holder.append(str(container['MECQ']))
        Holder.append(str(container['GCQ']))
        Holder.append(str(container['MGCQ']))
        Holder.append(str(container['WilingnessYes']))
        Holder.append(str(container['WilingnessNo']))
        Holder.append(str(container['HighRisk']))          
        Holder.append(str(container['SlightRisk']))
        Holder.append(str(container['LivingWithRisk']))
        Holder.append(str(container['Desktop']))
        Holder.append(str(container['Laptop']))            
        Holder.append(str(container['DTOverallWeight']))
        Holder.append(str(container['ProductionMachineOverallWeight']))
        Holder.append(str(container['HealthRiskOverallWeight']))
        Holder.append(str(container['WilingnessOverallWeight']))
        Holder.append(str(container['CityStatusOverallWeight']))

        cursor.execute('SELECT * FROM rto WHERE Team=%s', [str(session['team'])])
        #cursor.execute('SELECT * FROM rto')
        container = cursor.fetchall()
        listName = list()
        listAddress = list()
        listRiskLevel = list()
        listProductionMachine = list()
        listTransportation = list()
        listTeam = list()
        listRTO = list()
        listWiling = list()
        listID = list()
        listRTOValue = list()
        for x in container:
            cursor.execute('SELECT * FROM city WHERE idcity = %s', [str(x['CityID'])])
            cityinfo = cursor.fetchone()
            getUserID = str(x['ID'])
            getCity = str(cityinfo['city'])
            getCityStatus = str(cityinfo['citystatus'])
            getProvince = str(x['Province'])
            getHighRisk = int(x['High_Risk'])
            getSlightRisk = int(x['Slight_Risk'])
            getLivingWithRisk = int(x['Living_With_High_Risk'])
            getProductionMachine = str(x['Production_Machine'])
            getTransportation = str(x['Transportation_Availability'])
            getDepartment = str(x['Department'])
            getTeam = str(x['Team'])
            getWilingness = int(x['Wilingness'])
            getDistance = int(x['Distance'])
            getProcessed = int(x['Processed'])
            getRTO = int(x['RTO'])

            if getProcessed == 0:
            
                #FORMULA FOR CALCULATION HERE...
                StatusWeight = 0
                WilingnessWeight = 0
                RiskWeight = 100
                MachineWeight = 0
                DTWeight = 0

                TranspoWeight = 0
                LocationScore = 0

                cursor.execute('SELECT * FROM weights')
                Weights = cursor.fetchone()
            
                if getTransportation == 'Mass Transportation':
                    TranspoWeight = 0.5
                if getTransportation == 'Private Vehicle':
                    TranspoWeight = 1
                LocationScore = (int(Weights['DistanceFromRBC']) - getDistance)/int(Weights['DistanceFromRBC'])
                DTWeight = float((TranspoWeight*LocationScore))
            
                if getProductionMachine == 'Laptop':
                    MachineWeight = float((int(Weights['Laptop']))/100)
                if getProductionMachine == 'Desktop':
                    MachineWeight = float((int(Weights['Desktop']))/100)

                if getHighRisk == 1 and RiskWeight != 0:
                    temp = 100 - int(Weights['HighRisk'])
                    RiskWeight = RiskWeight - temp
                    if RiskWeight < 0:
                        RiskWeight = 0
                if getSlightRisk == 1 and RiskWeight != 0:
                    temp = 100 - int(Weights['SlightRisk'])
                    RiskWeight = RiskWeight - temp
                    if RiskWeight < 0:
                        RiskWeight = 0
                if getLivingWithRisk == 1 and RiskWeight != 0:
                    temp = 100 - int(Weights['LivingWithRisk'])
                    RiskWeight = RiskWeight - temp
                    if RiskWeight < 0:
                        RiskWeight = 0
                RiskWeight = float(RiskWeight/100)

                if getWilingness == 1:
                    WilingnessWeight = float(int(Weights['WilingnessYes'])/100)
                else:
                    WilingnessWeight = float(int(Weights['WilingnessNo'])/100)
                if getCityStatus == 'General Community Quarantine':
                    StatusWeight = float(int(Weights['GCQ'])/100)
                if getCityStatus == 'Modified General Community Quarantine':
                    StatusWeight = float(int(Weights['MECQ'])/100)
                if getCityStatus == 'Enhanced Community Quarantine':
                    StatusWeight = float(int(Weights['ECQ'])/100)

                Final = round(((DTWeight*float(int(Weights['DTOverallWeight'])/100)) + (MachineWeight*float(int(Weights['ProductionMachineOverallWeight'])/100)) + (RiskWeight*float(int(Weights['HealthRiskOverallWeight'])/100)) + (WilingnessWeight*float(int(Weights['WilingnessOverallWeight'])/100)) + (StatusWeight*float(int(Weights['CityStatusOverallWeight'])/100)))*100,1)
                if Final < 0:
                    Final = 0

            Name = '%s %s' % (x['FirstName'],x['LastName'])
            listName.append(str(Name))
            Address = '%s, %s, %s' % (x['Barangay'],x['City'],x['Province'])
            listAddress.append(str(Address))
            RiskLevel = '%s%%' % str(Final)
            listRiskLevel.append(str(RiskLevel))
            listProductionMachine.append(str(x['Production_Machine']))
            listTransportation.append(str(x['Transportation_Availability']))
            Team = '%s / %s' % (str(x['Department']),str(x['Team']))
            listTeam.append(str(Team))
            RTO = None
            if getRTO == 1:
                RTO = str(x['RTODate'])
            else:
                RTO = '-'
            listRTO.append(RTO)
            Wiling = None
            if str(x['Wilingness']) == '1':
                Wiling = 'Yes'
            if str(x['Wilingness']) == '0':
                Wiling = 'No'
            listWiling.append(Wiling)
            listCheckbox.append('check%s' % str(getUserID))
            listRTOValue.append(str(getRTO))
            Output = zip(listName,listAddress,listRiskLevel,listProductionMachine,listTransportation,listTeam,listRTO,listWiling,listCheckbox,listRTOValue)
        cursor.close()




    if request.method == 'POST':
        mode = request.form['modes']
        if mode == 'Save':
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            inputECQ = int(request.form['ECQ'])
            inputGCQ = int(request.form['GCQ'])
            inputMECQ = int(request.form['MECQ'])
            inputMGCQ = int(request.form['MGCQ'])
            inputWYes = int(request.form['WYes'])
            inputWNo = int(request.form['WNo'])
            inputHighRisk = int(request.form['HighRisk'])
            inputSlightRisk = int(request.form['SlightRisk'])
            inputLivingWithRisk = int(request.form['LivingWithRisk'])
            inputDesktop = int(request.form['Desktop'])
            inputLaptop = int(request.form['Laptop'])
            inputODT = int(request.form['ODT'])
            inputOWilingness = int(request.form['OWilingness'])
            inputOProductionMachine = int(request.form['OProductionMachine'])
            inputOCityStatus = int(request.form['OCityStatus'])
            inputORisk = int(request.form['ORisk'])

            if (inputWYes+inputWNo) != 100 or (inputECQ+inputGCQ+inputMECQ+inputMGCQ) != 100 or (inputDesktop+inputLaptop) != 100 or (inputHighRisk+inputSlightRisk+inputLivingWithRisk) != 100 or (inputODT+inputOWilingness+inputOProductionMachine+inputOCityStatus+inputORisk) != 100:
                if (inputWYes+inputWNo) != 100:
                    temperror.append('Wilingness Score')
                if (inputECQ+inputGCQ+inputMECQ+inputMGCQ) != 100:
                    temperror.append('Community Quarantine Measures Score')
                if (inputDesktop+inputLaptop) != 100:
                    temperror.append('Production Machine Score')
                if (inputHighRisk+inputSlightRisk+inputLivingWithRisk) != 100:
                    temperror.append('Health Risk Score')
                if (inputODT+inputOWilingness+inputOProductionMachine+inputOCityStatus+inputORisk) != 100:
                    temperror.append('Overall Weights')
                temp = ", ".join(temperror)
                error = 'All Scores/Weights must add up to strictly 100. (%s)' % temp
                session['errorweights'] = error
                return redirect(url_for('manager',error=error))

            cursor.execute('UPDATE weights SET ECQ=%s, GCQ=%s, MECQ=%s, MGCQ=%s, WilingnessYes=%s, WilingnessNo=%s, HighRisk=%s, SlightRisk=%s, LivingWithRisk=%s, Desktop=%s, Laptop=%s, DTOverallWeight=%s, ProductionMachineOverallWeight=%s, HealthRiskOverallWeight=%s, WilingnessOverallWeight=%s, CityStatusOverallWeight=%s WHERE weightID=1', (inputECQ,inputGCQ,inputMECQ,inputMGCQ,inputWYes,inputWNo,inputHighRisk,inputSlightRisk,inputLivingWithRisk,inputDesktop,inputLaptop,inputODT,inputOProductionMachine,inputORisk,inputOWilingness,inputOCityStatus))
            mysql.connection.commit()
            cursor.close()
            session['errorweights'] = None
            return redirect(url_for('manager'))

        if mode == 'Update':
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM rto')
            container = cursor.fetchall()
            for x in container:
                if request.form.get('check%s' % str(x['ID'])) == '1':
                    RTO = int(request.form['check%s' % str(x['ID'])])
                    today = date.today()
                    inputDate = today.strftime("%Y/%m/%d")
                    if RTO == 1:
                        cursor.execute('UPDATE rto SET RTO=1, RTODate=%s WHERE ID=%s', (inputDate,int(x['ID'])))
                        mysql.connection.commit()
                else:
                    cursor.execute('UPDATE rto SET RTO=0, RTODate=%s WHERE ID=%s', (None,int(x['ID'])))
                    mysql.connection.commit()   
            cursor.close()
            return redirect(url_for('manager'))
    
        if mode == 'Export':
            return redirect(url_for('manager'))

        if mode == 'Logout':
            tmp = []
            tmp = session.keys()
            for x in tmp:
                session['%s' % x] = None
            return redirect(url_for('login'))

    return render_template('employeelist.html',Info=Output,a=Holder,error=error)


@app.route("/calculate", methods=['GET', 'POST'])
def calculate():
    
    return NONE

@app.route("/Test", methods=['GET', 'POST'])
def Test():
    error = None
    if request.method == 'GET':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        ListResult = list()
        #cursor.execute('SELECT * FROM rto WHERE Team = %s', (str(session['id'])))
        cursor.execute('SELECT * FROM rto WHERE Team = %s', [str(session['team'])])
        container = cursor.fetchall()

        for x in container:
            cursor.execute('SELECT * FROM city WHERE idcity = %s', [str(x['CityID'])])
            cityinfo = cursor.fetchone()
            getUserID = str(x['ID'])
            getCity = str(cityinfo['city'])
            getCityStatus = str(cityinfo['citystatus'])
            getProvince = str(x['Province'])
            getHighRisk = int(x['High_Risk'])
            getSlightRisk = int(x['Slight_Risk'])
            getLivingWithRisk = int(x['Living_With_High_Risk'])
            getProductionMachine = str(x['Production_Machine'])
            getTransportation = str(x['Transportation_Availability'])
            getDepartment = str(x['Department'])
            getTeam = str(x['Team'])
            getWilingness = int(x['Wilingness'])
            getDistance = int(x['Distance'])
            getProcessed = int(x['Processed'])

            if getProcessed == 0:
            
                #FORMULA FOR CALCULATION HERE...
                StatusWeight = 0
                WilingnessWeight = 0
                RiskWeight = 100
                MachineWeight = 0
                DTWeight = 0

                TranspoWeight = 0
                LocationScore = 0

                cursor.execute('SELECT * FROM weights')
                Weights = cursor.fetchone()
            
                if getTransportation == 'Mass Transportation':
                    TranspoWeight = 0.5
                if getTransportation == 'Private Vehicle':
                    TranspoWeight = 1
                LocationScore = (30 - getDistance)/30
                DTWeight = float((TranspoWeight*LocationScore))
            
                if getProductionMachine == 'Laptop':
                    MachineWeight = float((int(Weights['Laptop']))/100)
                if getProductionMachine == 'Desktop':
                    MachineWeight = float((int(Weights['Desktop']))/100)

                if getHighRisk == 1 and RiskWeight != 0:
                    temp = 100 - int(Weights['HighRisk'])
                    RiskWeight = RiskWeight - temp
                    if RiskWeight < 0:
                        RiskWeight = 0
                if getSlightRisk == 1 and RiskWeight != 0:
                    temp = 100 - int(Weights['SlightRisk'])
                    RiskWeight = RiskWeight - temp
                    if RiskWeight < 0:
                        RiskWeight = 0
                if getLivingWithRisk == 1 and RiskWeight != 0:
                    temp = 100 - int(Weights['LivingWithRisk'])
                    RiskWeight = RiskWeight - temp
                    if RiskWeight < 0:
                        RiskWeight = 0
                RiskWeight = float(RiskWeight/100)

                if getWilingness == 1:
                    WilingnessWeight = float(int(Weights['WilingnessYes'])/100)
                else:
                    WilingnessWeight = float(int(Weights['WilingnessNo'])/100)

                if getCityStatus == 'General Community Quarantine':
                    StatusWeight = float(int(Weights['GCQ'])/100)
                if getCityStatus == 'Modified General Community Quarantine':
                    StatusWeight = float(int(Weights['MECQ'])/100)
                if getCityStatus == 'Enhanced Community Quarantine':
                    StatusWeight = float(int(Weights['ECQ'])/100)

                Final = round(((DTWeight*float(int(Weights['DTOverallWeight'])/100)) + (MachineWeight*float(int(Weights['ProductionMachineOverallWeight'])/100)) + (RiskWeight*float(int(Weights['HealthRiskOverallWeight'])/100)) + (WilingnessWeight*float(int(Weights['WilingnessOverallWeight'])/100)) + (StatusWeight*float(int(Weights['CityStatusOverallWeight'])/100)))*100,1)
                Name = '%s %s' % (x['FirstName'],x['LastName'])
                ListResult.append('%s: %s' % (Name,Final))

        cursor.close()
        error = ListResult
    return render_template('Test.html',error=error)


if __name__ == "__main__":
    app.run(debug=True)
