from cmath import e
from bson.objectid import ObjectId
from flask import Flask, render_template, request, jsonify, Response
from pymongo import MongoClient
from flask_cors import CORS
from flask_restful import Api, Resource
from pytz import timezone
import datetime
import bcrypt
import json
import os, shutil
import re
import docx2txt
import pdf2txt
import PyPDF2 
import base64
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import email
import gridfs
from email import encoders
from email.mime.base import MIMEBase
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
import nltk
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('maxent_ne_chunker')
# nltk.download('words')
# nltk.download('stopwords')


app = Flask(__name__)
CORS(app)
api = Api(app)


client = MongoClient(["mongodb://127.0.0.1:27017"])  # Mongodb initialize
# Mongodb initialize
# client = MongoClient(
#     ["mongodb+srv://raviyaduvanshi:%23Jgdtech100@cluster0.yjrlk.mongodb.net/"])
recruitmentManagement = client["Recruitment-Management"]  # Root Database
credentials = recruitmentManagement["Client's_Credentials"]
employees = recruitmentManagement["Employees"]
# Izeetek = client["Izeetek-Solution"]  # Client 1 Db.
testDb = recruitmentManagement["Test-Database"]  # Testing db
fs = gridfs.GridFS(recruitmentManagement)


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
    #   f.save(secure_filename(f.filename))
    #   os.remove(f.filename)
        return 'file uploaded successfully'


class ClientAdmin(Resource):
    def post(self):
        adminJson = request.get_json(force=True)
        userName = adminJson["userName"]
        password = adminJson["password"]
        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        credentials.insert_one({
            "userName": userName,
            "password": hashed_pw
        })

        return jsonify({
            "status code": 200,
            "message": "Hi " + userName + "! you have registered successfully as admin "
        })


api.add_resource(ClientAdmin, '/clientadmin')

# Client 1 Izeetek


def varifyAdmin(userName, password):
    hashed_pw = credentials.find({
        "userName": userName
    })[0]["password"]
    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        False


class LoginAdmin(Resource):
    def post(self):
        loginDeatils = request.get_json(force=True)
        userName = loginDeatils["userName"]
        password = loginDeatils["password"]
        correct_pw = varifyAdmin(userName, password)
        if not correct_pw:
            return jsonify({
                "status code": 302,
                "message": "You have entered an invalid username or password"
            })
        adminId = credentials.find({
            "userName": userName
        })[0]["_id"]

        return jsonify({
            "status code ": 200,
            "message": "Hi " + userName + "! you are logged in successfully.",
            "adminId": str(adminId),
            "_employeeId": str(adminId),
            "loginType": "Admin",
            "userName": userName
        })


api.add_resource(LoginAdmin, "/loginadmin")


class Employees(Resource):
    def post(self, adminId):
        docFile = request.files["docFile"]
        photoFile = request.files["photoFile"]
        # encoded_docFile = base64.b64encode(docFile.read())
        # encoded_photoFile = base64.b64encode(photoFile.read())
        employeeData = request.form['jsonData']
        # print(employeeData)
        employeeJson = json.loads(employeeData)
        # print(employeeJson)

        # images.insert_one({"image": encoded_string})
        # return jsonify(dataJson)
        # employeeJson = request.get_json(force=True)
        employeeName = employeeJson['employeeName']
        userName = employeeJson["userName"]
        gender = employeeJson['gender']
        mobileNumber = employeeJson['mobileNumber']
        personalEmailId = employeeJson['personalEmailId']
        officeEmailId = employeeJson['officeEmailId']
        dob = employeeJson['dob']
        doj = employeeJson['doj']
        designation = employeeJson['designation']
        employeeId = employeeJson['employeeId']
        # accessType = employeeJson['accessType']
        password = employeeJson['userName'] + "10"
        try:
            checkedUserName = employees.find({
                "userName": userName
                })[0]["userName"]

        except:
            checkedUserName = False
        
        try:
            managerId = adminId[24:48]
        except:
            managerId = ""
        
        if checkedUserName:
            return jsonify({
                "message": "Username is already exist.Please choose any other.",
                "statusCode": 302
            })


        employees.insert_one({
            "adminId": adminId[:24],
            "managerId": managerId,
            "employeeName": employeeName,
            "userName": userName,
            "password": password,
            "gender": gender,
            "mobileNumber": mobileNumber,
            "personalEmailId": personalEmailId,
            "officeEmailId": officeEmailId,
            "dob": dob,
            "doj": doj,
            "designation": designation,
            "employeeId": employeeId,
            "active": True
            # "docFile": encoded_docFile,
            # "photoFile": encoded_photoFile
        })

        photoFile.save(secure_filename(photoFile.filename))
        os.rename(photoFile.filename, "{userName}.jpg".format(userName = userName))
        with open("{userName}.jpg".format(userName = userName), 'rb') as f:
            contents = f.read()

        fs.put(contents, filename="{userName}.jpg".format(userName = userName))
        os.remove("{userName}.jpg".format(userName = userName))
        print("{userName}.jpg".format(userName = userName), " is Removed.")

        docFile.save(secure_filename(docFile.filename))
        os.rename(docFile.filename, "{userName}.pdf".format(userName = userName))
        with open("{userName}.pdf".format(userName = userName), 'rb') as f:
            contents = f.read()

        fs.put(contents, filename="{userName}.pdf".format(userName = userName))
        os.remove("{userName}.pdf".format(userName = userName))
        print("{userName}.pdf".format(userName = userName), " is Removed.")

        return jsonify({
            "anouncement": "Employee's data is store in database.",
            "userName": userName,
            "employeeName": employeeName,
            "gender": gender,
            "mobileNumber": mobileNumber,
            "personalEmailId": personalEmailId,
            "officeEmailId": officeEmailId,
            "dob": dob,
            "doj": doj,
            "designation": designation,
            "employeeId": employeeId,
            "active": True,
            "statusCode": 200
        })

    def get(self, adminId):
        allData = employees.find()
        employeeJson = []
        for data in allData:
            designation = data["designation"]
            # if data["adminId"] == adminId and designation == "Recruiter":
            if data["adminId"] == adminId:
                id = data["_id"]
                employeeName = data["employeeName"]
                userName = data["userName"]
                gender = data["gender"]
                dob = data["dob"]
                doj = data["doj"]
                personalEmailId = data["personalEmailId"]
                officeEmailId = data["officeEmailId"]
                mobileNumber = data["mobileNumber"]
                employeeId = data["employeeId"]
                active = data["active"]
                # docFile = data["docFile"]
                # decode_docFile = docFile.decode()
                # docFile_tag = '{0}'.format(decode_docFile)
                # photoFile = data["photoFile"]
                # decode_photoFile = photoFile.decode()
                # photoFile_tag = '{0}'.format(decode_photoFile)
                # return Response(photoFile_tag)
                dataDict = {
                    "id": str(id),
                    "employeeName": employeeName,
                    "userName": userName,
                    "gender": gender,
                    "dob": dob,
                    "doj": doj,
                    "personalEmailId": personalEmailId,
                    "officeEmailId": officeEmailId,
                    "mobileNumber": mobileNumber,
                    "designation": designation,
                    "employeeId": employeeId,
                    "active": active
                    # "photoFile_tag": photoFile_tag,
                    # "docFile_tag": docFile_tag
                }
                employeeJson.append(dataDict)
        print(employeeJson)
        return jsonify(employeeJson)


api.add_resource(Employees, '/employees/<string:adminId>')


def varifyEmployee(userName, password):
    hash_pw = employees.find({
        "userName": userName
    })[0]["password"]
    if password == hash_pw:
        return True
    else:
        return False


class EmployeeLogin(Resource):
    def post(self):
        loginJson = request.get_json(force=True)
        userName = loginJson["userName"]
        password = loginJson["password"]
        correct_pw = varifyEmployee(userName, password)
        if not correct_pw:
            return jsonify({
                "status": 302,
                "message": "You have entered an invalid username or password"
            })
        _id = employees.find({
            "userName": userName
        })[0]["_id"]
        data = employees.find_one({"_id": _id})
        adminId = data["adminId"]
        employee = data["employeeName"]
        userName = data["userName"]
        gender = data["gender"]
        mobileNumber = data["mobileNumber"]
        dob = data["dob"]
        doj = data["doj"]
        designation = data["designation"]
        officeEmailId = data["officeEmailId"]
        active = data["active"]
        print(active)
        if active == False:
            return jsonify({
                "status": 303,
                "message": "Hi {userName} ! Your Id is deactivated. Please contact to your manager.".format(userName = userName)
            })
        return jsonify({
            "adminId": adminId,
            "_employeeId": str(_id),
            "employee": employee,
            "userName": userName,
            "gender": gender,
            "mobileNumber": mobileNumber,
            "dob": dob,
            "doj": doj,
            "loginType": designation,
            "officeEmailId": officeEmailId,
            "status": 200
        })


api.add_resource(EmployeeLogin, "/employeelogin")


class RegisterCompany(Resource):
    def post(self, adminId):
        docFile = request.files["docFile"]
        # encoded_docFile = base64.b64encode(docFile.read())
        companyData = request.form["companyFormJson"]
        companyJson = json.loads(companyData)

        companyName = companyJson['companyName']
        companyURL = companyJson['companyURL']
        location = companyJson['location']
        remarks = companyJson['remarks']
        adminName = credentials.find(
            {"_id": ObjectId(adminId)})[0]["userName"]
        print(adminName)
        adminName = client[adminName]
        adminName["Companies"].insert_one({
            "companyName": companyName,
            "companyURL": companyURL,
            "location": location,
            "remarks": remarks,
            # "corporatePresentation": encoded_docFile
        })
        docFile.save(secure_filename(docFile.filename))
        os.rename(docFile.filename, "{companyName}.pdf".format(companyName = companyName))
        with open("{companyName}.pdf".format(companyName = companyName), 'rb') as f:
            contents = f.read()

        fs.put(contents, filename="{companyName}.pdf".format(companyName = companyName))
        os.remove("{companyName}.pdf".format(companyName = companyName))
        print("{companyName}.pdf".format(companyName = companyName), " is Removed.")

        return jsonify({
            "anouncement": "Company's data is store in database.",
            "companyName": companyName,
            "companyURL": companyURL,
            "location": location,
            "remarks": remarks,
            "status": 200
        })

    def get(self, adminId):
        adminName = credentials.find(
            {"_id": ObjectId(adminId)})[0]["userName"]
        print(adminName)
        adminName = client[adminName]
        allData = adminName["Companies"].find()
        companyJson = []
        for data in allData:
            id = data["_id"]
            companyName = data['companyName']
            companyURL = data['companyURL']
            location = data['location']
            remarks = data['remarks']
            # corporatePresentation = data["corporatePresentation"]
            # decode_corporatePresentation = corporatePresentation.decode()
            # corporatePresentation_tag = '{0}'.format(
            #     decode_corporatePresentation)

            dataDict = {
                "id": str(id),
                "companyName": companyName,
                "companyURL": companyURL,
                "location": location,
                "remarks": remarks,
                # "corporatePresentation": corporatePresentation_tag
            }
            companyJson.append(dataDict)
        # print(companyJson)
        return jsonify(companyJson)


api.add_resource(RegisterCompany, '/registercompany/<string:adminId>')


class RegisterClient(Resource):
    def post(self, adminId):
        docFile = request.files["docFile"]
        clientData = request.form["clientFormJson"]
        clientJson = json.loads(clientData)
        # clientJson = request.get_json(force=True)
        companyName = clientJson['companyName']
        clientName = clientJson['clientName']
        clientURL = clientJson['clientURL']
        branches = clientJson['branches']
        remarks = clientJson['remarks']
        adminName = credentials.find({'_id': ObjectId(adminId)})[0]["userName"]
        print(adminName)
        adminName = client[adminName]
        adminName["Clients"].insert_one({
            "companyName": companyName,
            "clientName": clientName,
            "clientURL": clientURL,
            "branches": branches,
            "remarks": remarks
        })

        docFile.save(secure_filename(docFile.filename))
        os.rename(docFile.filename, "{clientName}.pdf".format(clientName = clientName))
        with open("{clientName}.pdf".format(clientName = clientName), 'rb') as f:
            contents = f.read()

        fs.put(contents, filename="{clientName}.pdf".format(clientName = clientName))
        os.remove("{clientName}.pdf".format(clientName = clientName))
        print("{clientName}.pdf".format(clientName = clientName), " is Removed.")

        return jsonify({
            "anouncement": "Company's data is store in database.",
            "companyName": companyName,
            "clientyName": clientName,
            "clientURL": clientURL,
            "branches": branches,
            "remarks": remarks
        })

    def get(self, adminId):
        adminName = credentials.find({'_id': ObjectId(adminId)})[0]["userName"]
        print(adminName)
        adminName = client[adminName]
        allData = adminName["Clients"].find()
        clientJson = []
        for data in allData:
            id = data["_id"]
            companyName = data['companyName']
            clientName = data['clientName']
            clientURL = data['clientURL']
            branches = data['branches']
            remarks = data['remarks']

            dataDict = {
                "id": str(id),
                "companyName": companyName,
                "clientName": clientName,
                "clientURL": clientURL,
                "branches": branches,
                "remarks": remarks
            }
            clientJson.append(dataDict)
        print(clientJson)
        return jsonify(clientJson)


api.add_resource(RegisterClient, '/registerclient/<string:adminId>')


class Opening(Resource):
    def post(self, adminId):
        
        openingData = request.form['jsonData']
        jsonData = json.loads(openingData)
        employeeType = jsonData['employeeType']
        contractDuration = jsonData['contractDuration']
        domain = jsonData['domain']
        role = jsonData['role']
        location = jsonData['location']
        nop = jsonData['nop']
        companyName = jsonData['companyName']
        clientName = jsonData['clientName']
        experiance = jsonData['experiance']
        budgetRange = jsonData['budgetRange']
        noticePeriod = jsonData['noticePeriod']
        jobDescription = jsonData['jobDescription']
        mandatorySkills = jsonData['mandatorySkills']
        wfh = jsonData['wfh']
        # questions = jsonData['questions']
        try:
            questions = jsonData['questions']
            print("Question")
        except:
            questions = "No questions"
            print(questions) 
        # now = datetime.now()
        # dt_string = now.strftime("%B %d, %Y %H:%M:%S")

        adminName = credentials.find({'_id': ObjectId(adminId[0:24])})[0]["userName"]
        adminName = client[adminName]
        
        try:
            docFile = request.files["docFile"]
            docFile.save(secure_filename(docFile.filename))
            os.rename(docFile.filename, "{role}.pdf".format(role = role))
            with open("{role}.pdf".format(role = role), 'rb') as f:
                contents = f.read()
            
            fs1 = gridfs.GridFS(adminName)
            fs1.put(contents, filename="{role}.pdf".format(role = role))
            os.remove("{role}.pdf".format(role = role))
            print("{role}.pdf".format(role = role), " is Removed.")
        except:
            pass

        adminName["Openings"].insert_one({
            "employeeType": employeeType,
            "contractDuration": contractDuration,
            "domain": domain,
            "dt": '{dt:%B} {dt.day}, {dt.year}'.format(dt=datetime.datetime.now()),
            "role": role,
            "companyName": companyName,
            "clientName": clientName,
            "location": location,
            "experiance": experiance,
            "budgetRange": budgetRange,
            "noticePeriod": noticePeriod,
            "nop": nop,
            "jobDescription": jobDescription,
            "mandatorySkills": mandatorySkills,
            "status": 10,
            "position": "Initiated",
            "wfh": wfh,
            "questions": questions,
            "tlId": adminId[24:],
            "workAllocated": 0,
            "uploadedProfiles": 0,
            "sharedProfiles": 0,
            "internalRejectedProfiles": 0,
            "externalRejectedProfiles": 0
        })
        
        return jsonify({
            "employeeType": employeeType,
            "contractDuration": contractDuration,
            "domain": domain,
            "role": role,
            "companyName": companyName,
            "clientName": clientName,
            "location": location,
            "experiance": experiance,
            "budgetRange": budgetRange,
            "noticePeriod": noticePeriod,
            "nop": nop,
            "jobDescription": jobDescription,
            "mandatorySkills": mandatorySkills,
            "wfh": wfh,
            "questions": questions,
            "message": "Data saved in DB successfully."
        })

    def get(self, adminId):
        adminName = credentials.find({'_id': ObjectId(adminId[:24])})[
            0]["userName"]
        adminName = client[adminName]
        allData = adminName["Openings"].find()
        openingJson = []
        for data in allData:
            dt = data["dt"]
            date_temp = dt.split()
            custom_dt = "{month}, {year}".format(
                month=date_temp[0], year=date_temp[2])
            if dt == adminId[24:] or adminId[24:] == custom_dt:
                id = data['_id']
                role = data['role']
                companyName = data['companyName']
                clientName = data['clientName']
                experiance = data['experiance']
                budgetRange = data['budgetRange']
                noticePeriod = data['noticePeriod']
                jobDescription = data['jobDescription']
                mandatorySkills = data['mandatorySkills']
                wfh = data['wfh']
                questions = data['questions']
                status = data["status"]
                position = data["position"]
                nop = data["nop"]
                domain = data["domain"]
                workAllocated = data["workAllocated"]
                uploadedProfiles = data["uploadedProfiles"]
                sharedProfiles = data["sharedProfiles"]
                internalRejectedProfiles = data["internalRejectedProfiles"]
                externalRejectedProfiles = data["externalRejectedProfiles"]

                dataDict = {
                    "id": str(id),
                    "role": role,
                    "companyName": companyName,
                    "clientName": clientName,
                    "experiance": experiance,
                    "budgetRange": budgetRange,
                    "noticePeriod": noticePeriod,
                    "jobDescription": jobDescription,
                    "mandatorySkills": mandatorySkills,
                    "wfh": wfh,
                    "questions": questions,
                    "status": status,
                    "position": position,
                    "dt": dt,
                    "nop": nop,
                    "domain": domain,
                    "workAllocated": workAllocated,
                    "uploadedProfiles": uploadedProfiles,
                    "sharedProfiles": sharedProfiles,
                    "internalRejectedProfiles": internalRejectedProfiles,
                    "externalRejectedProfiles": externalRejectedProfiles
                }
                openingJson.append(dataDict)
        print(openingJson)
        return jsonify(openingJson)


api.add_resource(Opening, '/opening/<string:adminId>')


class WorkAllocation(Resource):
    def post(self, adminId):
        workJson = request.get_json(force=True)
        recruiterId = workJson['recruiterId']
        openingId = workJson['openingId']
        slot = workJson['slot']
        # now = datetime.now()
        # dt_string = now.strftime("%B %d, %Y %H:%M:%S")
        adminName = credentials.find({'_id': ObjectId(adminId)})[0]["userName"]
        print(adminName)
        adminName = client[adminName]
        openingData = adminName["Openings"].find_one(
            {"_id": ObjectId(openingId)})
        employeeType = openingData["employeeType"]
        contractDuration = openingData["contractDuration"]
        companyName = openingData["companyName"]
        clientName = openingData["clientName"]
        role = openingData["role"]
        requiredExperiance = openingData["experiance"]
        openingLocation = openingData["location"]
        nop = openingData["nop"]
        budgetRange = openingData["budgetRange"]
        noticePeriod = openingData["noticePeriod"]
        jobDescription = openingData["jobDescription"]
        mandatorySkills = openingData["mandatorySkills"]
        wfh = openingData["wfh"]
        questions = openingData["questions"]
        recruiterData = employees.find_one({"_id": ObjectId(recruiterId)})
        recruiterName = recruiterData["employeeName"]
        recruiterMobileNumber = recruiterData["mobileNumber"]
        officeEmailId = recruiterData["officeEmailId"]

        try:
            print("try is running")
            total_data = adminName["Work-Allocation"].find()
            for data in total_data:
                _openingId = data["openingId"]
                _recruiterId = data["recruiterId"]
                if _openingId == openingId and _recruiterId == recruiterId:
                    return jsonify({
                        "message": "You have already assigned task to " + recruiterName + ". Thankyou!",
                        "statusCode": 302
                    })
        except:
            print("excerpt is running")
            print(e)

        adminName["Work-Allocation"].insert_one({
            "openingId": openingId,
            "recruiterId": recruiterId,
            "dt_string": '{dt:%B} {dt.day}, {dt.year}'.format(dt=datetime.datetime.now()),
            "slot": slot,
            "status": 10,
            "slot": slot,
            "recruiterName": recruiterName,
            "recruiterMobileNumber": recruiterMobileNumber,
            "officeEmailId": officeEmailId,
            "employeeType": employeeType,
            "contractDuration": contractDuration,
            "companyName": companyName,
            "clientName": clientName,
            "role": role,
            "openingLocation": openingLocation,
            "nop": nop,
            "recruiterName": recruiterName,
            "requiredExperiance": requiredExperiance,
            "budgetRange": budgetRange,
            "noticePeriod": noticePeriod,
            "jobDescription": jobDescription,
            "mandatorySkills": mandatorySkills,
            "wfh": wfh,
            "questions": questions,
            "position": "Upload profile"
        })

        workAllocated = adminName["Openings"].find(
            {"_id": ObjectId(openingId)})[0]["workAllocated"]

        adminName["Openings"].update_many({
            "_id": ObjectId(openingId)
        },
            {
            "$set": {
                "status": 20,
                "position": "Processing",
                "workAllocated": workAllocated + 1
            }
        })

        return jsonify({
            "recruiterId": recruiterId,
            "openingId": openingId,
            "status code": 200
        })

    def get(self, adminId):
        adminName = credentials.find({'_id': ObjectId(adminId)})[0]["userName"]
        print(adminName)
        adminName = client[adminName]
        workAllData = adminName["Work-Allocation"].find()
        workJson = []
        for data in workAllData:
            id = data['_id']
            openingId = data['openingId']
            recruiterId = data['recruiterId']
            slot = data["slot"]
            date_time = data["dt_string"]
            recruiterName = data["recruiterName"]
            companyName = data["companyName"]
            clientName = data["clientName"]
            role = data["role"]
            status = data["status"]
            dataDict = {
                "workAllocationId": str(id),
                "openingId": openingId,
                "recruiterId": recruiterId,
                "slot": slot,
                "date_time": date_time,
                "recruiterName": recruiterName,
                "companyName": companyName,
                "clientName": clientName,
                "role": role,
                "status": status
            }
            workJson.append(dataDict)
        print(workJson)
        return jsonify(workJson)


api.add_resource(WorkAllocation, '/workallocation/<string:adminId>')


class WorkAllocationListByOpeningId(Resource):
    def get(self, adminId):
        print(adminId[24:48])
        adminName = credentials.find({'_id': ObjectId(adminId[:24])})[
            0]["userName"]
        print(adminName)
        adminName = client[adminName]
        workAllData = adminName["Work-Allocation"].find()
        workJson = []
        for data in workAllData:
            openingId = data['openingId']
            print(openingId)
            recruiterId = data['recruiterId']
            date_time = data["dt_string"]
            date_temp = date_time.split()
            custom_date = "{month}, {year}".format(
                month=date_temp[0], year=date_temp[2])
            status = data["status"]
            print(date_time)
            print("temp : ", custom_date)
            print(adminId[48:])
            if (openingId == adminId[24:48] or recruiterId == adminId[24:48]) and ((adminId[48:] == date_time or adminId[48:] == custom_date)):
                workAllocationId = data["_id"]
                recruiterId = data['recruiterId']
                date_time = data["dt_string"]
                recruiterName = data['recruiterName']
                recruiterMobileNumber = data['recruiterMobileNumber']
                officeEmailId = data['officeEmailId']
                employeeType = data['employeeType']
                contractDuration = data['contractDuration']
                role = data['role']
                openingLocation = data['openingLocation']
                nop = data['nop']
                companyName = data['companyName']
                clientName = data['clientName']
                requiredExperiance = data['requiredExperiance']
                budgetRange = data['budgetRange']
                noticePeriod = data['noticePeriod']
                jobDescription = data['jobDescription']
                mandatorySkills = data['mandatorySkills']
                questions = data["questions"]
                wfh = data['wfh']
                slot = data["slot"]
                status = data["status"]
                dataDict = {
                    "workAllocationId": str(workAllocationId),
                    "openingId": openingId,
                    "recruiterId": recruiterId,
                    "slot": slot,
                    "date_time": date_time,
                    "recruiterName": recruiterName,
                    "recruiterMobileNumber": recruiterMobileNumber,
                    "officeEmailId": officeEmailId,
                    "employeeType": employeeType,
                    "contractDuration": contractDuration,
                    "companyName": companyName,
                    "clientName": clientName,
                    "role": role,
                    "openingLocation": openingLocation,
                    "nop": nop,
                    "recruiterName": recruiterName,
                    "requiredExperiance": requiredExperiance,
                    "budgetRange": budgetRange,
                    "noticePeriod": noticePeriod,
                    "jobDescription": jobDescription,
                    "mandatorySkills": mandatorySkills,
                    "wfh": wfh,
                    "questions": questions,
                    "status": status
                }
                workJson.append(dataDict)
        print(workJson)
        return jsonify(workJson)


api.add_resource(WorkAllocationListByOpeningId,
                 '/workallocationlistbyopeningid/<string:adminId>')


class EmployeeCrud(Resource):
    def get(self, _employeeId):
        data = employees.find_one({'_id': ObjectId(_employeeId)})
        id = data['_id']
        employeeName = data["employeeName"]
        userName = data["userName"]
        gender = data["gender"]
        dob = data["dob"]
        doj = data["doj"]
        personalEmailId = data["personalEmailId"]
        officeEmailId = data["officeEmailId"]
        mobileNumber = data["mobileNumber"]
        designation = data["designation"]
        employeeId = data["employeeId"]
        # photoFile = data["photoFile"]
        # decode_photoFile = photoFile.decode()
        # photoFile_tag = '{0}'.format(decode_photoFile)
        # docFile = data["docFile"]
        # decode_docFile = docFile.decode()
        # docFile_tag = '{0}'.format(decode_docFile)

        dataDict = {
            "id": str(id),
            "employeeName": employeeName,
            "userName": userName,
            "gender": gender,
            "dob": dob,
            "doj": doj,
            "personalEmailId": personalEmailId,
            "officeEmailId": officeEmailId,
            "mobileNumber": mobileNumber,
            "designation": designation,
            "employeeId": employeeId,
            # "photoFile_tag": photoFile_tag,
            # "docFile_tag": docFile_tag
        }
        # print(dataDict)
        return jsonify(dataDict)

    def delete(self, _employeeId):
        # employees.delete_many({'_id': ObjectId(_employeeId)})
        # print('\n # Deletion successful # \n')
        active = _employeeId[24:]
        if active == "true":
            employees.update_many({
            "_id": ObjectId(_employeeId[0:24])
        },
            {
            "$set": {
                "active": False
            }
        })

        else:
            employees.update_many({
            "_id": ObjectId(_employeeId[0:24])
        },
            {
            "$set": {
                "active": True
            }
        })
        return jsonify({'status': 'Data id: ' + _employeeId + ' is updated!'})

    def put(self, _employeeId):

        formData = request.form["updatedJson"]
        updatedJson = json.loads(formData)
        employeeName = updatedJson["employeeName"]
        userName = updatedJson["userName"]
        designation = updatedJson["designation"]
        dob = updatedJson["dob"]
        doj = updatedJson["doj"]
        gender = updatedJson["gender"]
        mobileNumber = updatedJson["mobileNumber"]
        officeEmailId = updatedJson["officeEmailId"]
        personalEmailId = updatedJson["personalEmailId"]

        employees.update_many({"_id": ObjectId(_employeeId)},
        {
            "$set": {
                "employeeName": employeeName,
                "userName": userName,
                "designation": designation,
                "dob": dob,
                "doj": doj,
                "gender": gender,
                "mobileNumber": mobileNumber,
                "officeEmailId": officeEmailId,
                "personalEmailId": personalEmailId
            }
        })

        return jsonify({'status': 'Data id: ' + _employeeId + ' is updated!'})


api.add_resource(EmployeeCrud, "/employee/<string:_employeeId>")


class OpeningCrud(Resource):
    def get(self, adminId, openingId):
        adminName = credentials.find({'_id': ObjectId(adminId)})[0]["userName"]
        print(adminName)
        adminName = client[adminName]
        data = adminName['Openings'].find_one({'_id': ObjectId(openingId)})
        id = data['_id']
        role = data['role']
        companyName = data['companyName']
        clientName = data['clientName']
        experiance = data['experiance']
        budgetRange = data['budgetRange']
        noticePeriod = data['noticePeriod']
        jobDescription = data['jobDescription']
        mandatorySkills = data['mandatorySkills']
        wfh = data['wfh']
        questions = data['questions']
        position = data['position']
        status = data["status"]

        dataDict = {
            "id": str(id),
            "role": role,
            "companyName": companyName,
            "clientName": clientName,
            "experiance": experiance,
            "budgetRange": budgetRange,
            "noticePeriod": noticePeriod,
            "jobDescription": jobDescription,
            "mandatorySkills": mandatorySkills,
            "wfh": wfh,
            "questions": questions,
            "position": position,
            "status": status
        }
        print(dataDict)
        return jsonify(dataDict)


api.add_resource(OpeningCrud, '/opening/<string:adminId>/<string:openingId>')


class UploadProfile(Resource):

    def post(self, adminId):
        # profileJson = request.get_json(force=True)
        cvFile = request.files["docFile"]
        # encoded_cvFile = base64.b64encode(cvFile.read())
        jsonData = request.form['jsonData']
        profileJson = json.loads(jsonData)
        # now = datetime.now()
        # dt_string = now.strftime("%B %d, %Y %H:%M:%S")
        candidateName = profileJson['candidateName']
        emailId = profileJson['emailId']
        mobileNumber = profileJson['mobileNumber']
        skills = profileJson['skills']
        totalExperiance = profileJson['totalExperiance']
        relatedExperiance = profileJson['relatedExperiance']
        currentCompanyName = profileJson["currentCompanyName"]
        cctc = profileJson['cctc']
        ectc = profileJson['ectc']
        np = profileJson['np']
        dos = '{dt:%B} {dt.day}, {dt.year}'.format(dt=datetime.datetime.now())
        currentLocation = profileJson['currentLocation']
        preferredLocation = profileJson["preferredLocation"]
        remarks = profileJson['remarks']
        holdingOffer = profileJson["holdingOffer"]
        offeredCompanyName = profileJson["offeredCompanyName"]
        octc = profileJson["octc"]
        ejd = profileJson["ejd"]
        snp = profileJson["snp"]
        lwd = profileJson["lwd"]
        recruiterId = profileJson["recruiterId"]
        openingId = profileJson["openingId"]
        WorkAllocationId = profileJson["workAllocationId"]


        adminName = credentials.find({'_id': ObjectId(adminId)})[0]["userName"]
        print(adminName)
        adminName = client[adminName]

        recruiterData = employees.find_one({"_id": ObjectId(recruiterId)})
        recruiterName = recruiterData['employeeName']
        recruiterMobileNumber = recruiterData['mobileNumber']
        officeEmailId = recruiterData['officeEmailId']
        print(openingId)
        openingData = adminName["Openings"].find_one({"_id": ObjectId(openingId)})
        employeeType = openingData['employeeType']
        contractDuration = openingData['contractDuration']
        role = openingData['role']
        openingLocation = openingData['location']
        nop = openingData['nop']
        companyName = openingData['companyName']
        clientName = openingData['clientName']
        experiance = openingData['experiance']
        budgetRange = openingData['budgetRange']
        noticePeriod = openingData['noticePeriod']
        jobDescription = openingData['jobDescription']
        mandatorySkills = openingData['mandatorySkills']
        wfh = openingData['wfh']

        workAllocationData = adminName["Work-Allocation"].find_one({"_id": ObjectId(WorkAllocationId)})
        slot = workAllocationData["slot"]
        cvFile.save(os.path.join("Files", "{nameFile}".format(nameFile = cvFile.filename)))
        os.rename("Files/{nameFile}".format(nameFile = cvFile.filename), "Files/{emailId}.pdf".format(emailId = emailId))
                
        with open("Files/{emailId}.pdf".format(emailId = emailId), 'rb') as f:
                contents = f.read()
            
        fs1 = gridfs.GridFS(adminName)
        fs1.put(contents, filename="{emailId}.pdf".format(emailId = emailId))
        os.remove("Files/{emailId}.pdf".format(emailId = emailId))
        print("Files/.{emailId}.pdf".format(emailId = emailId), " is Removed.")
       
        # try:
        #     cvFile.save(os.path.join("Files", "{nameFile}".format(nameFile = cvFile.filename)))
        #     os.rename("Files/{nameFile}".format(nameFile = cvFile.filename), "Files/{emailId}.pdf".format(emailId = emailId))
                
        #     with open("Files/{emailId}.pdf".format(emailId = emailId), 'rb') as f:
        #         contents = f.read()
            
        #     fs1 = gridfs.GridFS(adminName)
        #     fs1.put(contents, filename="{emailId}.pdf".format(emailId = emailId))
        #     os.remove("Files/{emailId}.pdf".format(emailId = emailId))
        #     print("Files/.{emailId}.pdf".format(emailId = emailId), " is Removed.")
        # except:
        #     for filename in os.listdir("Files"):
        #         file_path = os.path.join("Files", filename)
        #         try:
        #             if os.path.isfile(file_path) or os.path.islink(file_path):
        #                 os.unlink(file_path)
        #             elif os.path.isdir(file_path):
        #                 shutil.rmtree(file_path)
        #         except Exception as e:
        #             print("Failed to delete %s. Reason: %s" % (file_path, e))
        #     print("File is Removed.")
            # return jsonify({
            #     "status": 302,
            #     "msg": "Please rename your file. Space is not allowed in filename. Thank you!"
            # })

        adminName["UploadedProfiles"].insert_one({
            "recruiterName": recruiterName,
            "recruiterMobileNumber": recruiterMobileNumber,
            "officeEmailId": officeEmailId,
            "employeeType": employeeType,
            "contractDuration": contractDuration,
            "role": role,
            "openingLocation": openingLocation,
            "nop": nop,
            "companyName": companyName,
            "clientName": clientName,
            "requiredExperiance": experiance,
            "budgetRange": budgetRange,
            "noticePeriod":noticePeriod,
            "jobDescription": jobDescription,
            "mandatorySkills": mandatorySkills,
            "wfh": wfh,
            "candidateName": candidateName,
            "emailId": emailId,
            "mobileNumber": mobileNumber,
            "candidateSkills": skills,
            "totalExperiance": totalExperiance,
            "relatedExperiance": relatedExperiance,
            "currentCompanyName": currentCompanyName,
            "cctc": cctc,
            "ectc": ectc,
            "np": np,
            "dos": dos,
            "currentLocation": currentLocation,
            "preferredLocation": preferredLocation,
            "holdingOffer": holdingOffer,
            "offeredCompanyName": offeredCompanyName,
            "octc": octc,
            "ejd": ejd,
            "snp": snp,
            "lwd": lwd,
            "remarks": remarks,
            "T": True,
            "SFP": True,
            "SWC": False,
            "D": False,
            "SS": False,
            "SR": False,
            "P": False,
            "YTS": False,
            "IS": False,
            "IFP": False,
            "L1-R": False,
            "L1-S": False,
            "L2-IS": False,
            "L2-IFP": False,
            "L2-R": False,
            "L2-S": False,
            "L3-IS": False,
            "L3-IFP": False,
            "L3-R": False,
            "L3-S": False,
            "FR": False,
            "FS": False,
            "OP": False,
            "YTJ": False,
            "DO": False,
            "J": False,
            "profilePosition": "Team Lead approval is required.",
            "openingId": openingId,
            "recruiterId": recruiterId,
            "workAllocationId": WorkAllocationId,
            "slot": slot
        })

        uploadedProfiles = adminName["Openings"].find({
            "_id": ObjectId(openingId)})[0]["uploadedProfiles"]
        # workAllocated = adminName["Openings"].find({
        #     "_id": ObjectId(openingId)})[0]["workAllocated"]
        adminName["Openings"].update_many({
            "_id": ObjectId(openingId)
        },
            {
            "$set": {
                "status": 30,
                "position": "Profile has uploaded by recruiter for this opening.",
                # "workAllocated": workAllocated - 1,
                "uploadedProfiles": uploadedProfiles + 1
            }
        })
        adminName["Work-Allocation"].update_many({
            "_id": ObjectId(WorkAllocationId)
        },
            {
            "$set": {
                "status": 20,
                "position": "You have uploaded profile for this opening."
            }
        })
        return jsonify({
            "candidateName": candidateName,
            "emailId": emailId,
            "mobileNumber": mobileNumber,
            "totalExperiance": totalExperiance,
            "relatedExperiance": relatedExperiance,
            "cctc": cctc,
            "ectc": ectc,
            "np": np,
            "dos": dos,
            "currentLocation": currentLocation,
            "preferredLocation": preferredLocation,
            "remarks": remarks,
            "msg": "Profile is stored in database.",
            "status code": 200
        })

    def get(self, adminId):
        adminName = credentials.find({'_id': ObjectId(adminId[:24])})[
            0]["userName"]
        print(adminName)
        adminName = client[adminName]
        allData = adminName["UploadedProfiles"].find()
        profileJson = []
        for data in allData:
            openingId = data["openingId"]
            recruiterId = data["recruiterId"]
            dos = data['dos']
            date_temp = dos.split()
            _dos = "{month}, {year}".format(
                month=date_temp[0], year=date_temp[2])
            if ((openingId == adminId[24:48] or recruiterId == adminId[24:48]) and (dos == adminId[48:] or _dos == adminId[48:])) or (dos == adminId[24:] or _dos == adminId[24:]):
                id = data['_id']
                recruiterName = data['recruiterName']
                recruiterMobileNumber = data['mobileNumber']
                officeEmailId = data['officeEmailId']
                employeeType = data['employeeType']
                contractDuration = data['contractDuration']
                role = data['role']
                openingLocation = data['openingLocation']
                nop = data['nop']
                companyName = data['companyName']
                clientName = data['clientName']
                requiredExperiance = data['requiredExperiance']
                budgetRange = data['budgetRange']
                noticePeriod = data['noticePeriod']
                jobDescription = data['jobDescription']
                mandatorySkills = data['mandatorySkills']
                wfh = data['wfh']
                slot = data["slot"]
                candidateName = data['candidateName']
                emailId = data['emailId']
                mobileNumber = data['mobileNumber']
                totalExperiance = data['totalExperiance']
                relatedExperiance = data['relatedExperiance']
                currentCompanyName = data["currentCompanyName"]
                cctc = data['cctc']
                ectc = data['ectc']
                np = data['np']
                currentLocation = data['currentLocation']
                preferredLocation = data["preferredLocation"]
                holdingOffer = data["holdingOffer"]
                offeredCompanyName = data["offeredCompanyName"]
                octc = data["octc"]
                ejd = data["ejd"]
                snp = data["snp"]
                lwd = data["lwd"]
                recruiterRemarks = data["remarks"]
                # status = data["status"]
                profilePosition = data["profilePosition"]
                workAllocationId = data["workAllocationId"]
                t = data["T"]
                sfp = data["SFP"]
                swc = data["SWC"]
                d = data["D"]
                ss = data["SS"]
                sr = data["SR"]
                p = data["P"]
                yts = data["YTS"]
                is1 = data["IS"]
                ifp = data["IFP"]
                l1_r = data["L1-R"]
                l1_s = data["L1-S"]
                l2is = data["L2-IS"]
                l2ifp = data["L2-IFP"]
                l2r = data["L2-R"]
                l2s = data["L2-S"]
                l3is = data["L3-IS"]
                l3ifp = data["L3-IFP"]
                l3r = data["L3-R"]
                l3s = data["L3-S"]
                fr = data["FR"]
                fs = data["FS"]
                op = data["OP"]
                ytj = data["YTJ"]
                do = data["DO"]
                j = data["J"]
                # cvFile = data["docFile"]
                # decode_cvFile = cvFile.decode()
                # cvFile_tag = '{0}'.format(decode_cvFile)

                dataDict = {
                    "id": str(id),
                    "recruiterName": recruiterName,
                    "recruiterMobileNumber": recruiterMobileNumber,
                    "officeEmailId": officeEmailId,
                    "employeeType": employeeType,
                    "contractDuration": contractDuration,
                    "role": role,
                    "openingLocation": openingLocation,
                    "nop": nop,
                    "companyName": companyName,
                    "clientName": clientName,
                    "requiredExperiance": requiredExperiance,
                    "budgetRange": budgetRange,
                    "noticePeriod":noticePeriod,
                    "jobDescription": jobDescription,
                    "mandatorySkills": mandatorySkills,
                    "wfh": wfh,
                    "candidateName": candidateName,
                    "emailId": emailId,
                    "mobileNumber": mobileNumber,
                    "totalExperiance": totalExperiance,
                    "relatedExperiance": relatedExperiance,
                    "currentCompanyName": currentCompanyName,
                    "cctc": cctc,
                    "ectc": ectc,
                    "dos": dos,
                    "currentLocation": currentLocation,
                    "preferredLocation": preferredLocation,
                    "holdingOffer": holdingOffer,
                    "offeredCompanyName": offeredCompanyName,
                    "octc": octc,
                    "ejd": ejd,
                    "snp": snp,
                    "lwd": lwd,
                    "np": np,
                    "slot": slot,
                    # "status": status,
                    "profilePosition": profilePosition,
                    "recruiterRemarks": recruiterRemarks,
                    "recruiterId": recruiterId,
                    "openingId": openingId,
                    "workAllocationId": workAllocationId,
                    "t": t,
                    "sfp" : sfp,
                    "swc": swc,
                    "ss": ss,
                    "d": d,
                    "sr": sr,
                    "p": p,
                    "yts" :yts,
                    "is1" : is1,
                    "ifp" : ifp,
                    "l1_r": l1_r,
                    "l1_s": l1_s,
                    "l2is": l2is,
                    "l2ifp": l2ifp,
                    "l2r": l2r,
                    "l2s": l2s,
                    "l3is": l3is,
                    "l3ifp": l3ifp,
                    "l3r": l3r,
                    "l3s": l3s,
                    "fr": fr,
                    "fs": fs,
                    "op": op,
                    "ytj": ytj,
                    "do": do,
                    "j": j
                    # "cvFile": cvFile_tag
                }
                profileJson.append(dataDict)
        print(profileJson)
        return jsonify(profileJson)

    def put(self, adminId):
        jsonData = request.get_json(force=True)
        filterType = jsonData["value"]
        print(filterType)
        adminName = credentials.find({'_id': ObjectId(adminId[:24])})[
            0]["userName"]
        print(adminName)
        adminName = client[adminName]
        # adminId[24:48]) and (dos == adminId[48:] or _dos == adminId[48:]):
        filteredData = []

        try:
            if jsonData["openingId"]:
                mdos = adminId[24:]
                allData = adminName["UploadedProfiles"].find({"openingId": jsonData["openingId"]})
        except:
            if adminId[48:]:
             mdos = adminId[48:]
             allData = adminName["UploadedProfiles"].find({"recruiterId": adminId[24:48]})
            else:
                mdos = adminId[24:]
                allData = adminName["UploadedProfiles"].find()

        for data in allData:
            _filterType = data[filterType]
            print(_filterType)
            print(_filterType)
            openingId = data["openingId"]
            recruiterId = data["recruiterId"]
            dos = data['dos']
            date_temp = dos.split()
            _dos = "{month}, {year}".format(
                month=date_temp[0], year=date_temp[2])
            if _filterType and (dos == mdos or _dos == mdos):
                id = data['_id']
                recruiterName = data['recruiterName']
                recruiterMobileNumber = data['mobileNumber']
                officeEmailId = data['officeEmailId']
                employeeType = data['employeeType']
                contractDuration = data['contractDuration']
                role = data['role']
                openingLocation = data['openingLocation']
                nop = data['nop']
                companyName = data['companyName']
                clientName = data['clientName']
                requiredExperiance = data['requiredExperiance']
                budgetRange = data['budgetRange']
                noticePeriod = data['noticePeriod']
                jobDescription = data['jobDescription']
                mandatorySkills = data['mandatorySkills']
                wfh = data['wfh']
                slot = data["slot"]
                candidateName = data['candidateName']
                emailId = data['emailId']
                mobileNumber = data['mobileNumber']
                totalExperiance = data['totalExperiance']
                relatedExperiance = data['relatedExperiance']
                currentCompanyName = data["currentCompanyName"]
                cctc = data['cctc']
                ectc = data['ectc']
                np = data['np']
                currentLocation = data['currentLocation']
                preferredLocation = data["preferredLocation"]
                holdingOffer = data["holdingOffer"]
                offeredCompanyName = data["offeredCompanyName"]
                octc = data["octc"]
                ejd = data["ejd"]
                snp = data["snp"]
                lwd = data["lwd"]
                recruiterRemarks = data["remarks"]
                profilePosition = data["profilePosition"]
                workAllocationId = data["workAllocationId"]

                dataDict = {
                    "id": str(id),
                    "recruiterName": recruiterName,
                    "recruiterMobileNumber": recruiterMobileNumber,
                    "officeEmailId": officeEmailId,
                    "employeeType": employeeType,
                    "contractDuration": contractDuration,
                    "role": role,
                    "openingLocation": openingLocation,
                    "nop": nop,
                    "companyName": companyName,
                    "clientName": clientName,
                    "requiredExperiance": requiredExperiance,
                    "budgetRange": budgetRange,
                    "noticePeriod":noticePeriod,
                    "jobDescription": jobDescription,
                    "mandatorySkills": mandatorySkills,
                    "wfh": wfh,
                    "candidateName": candidateName,
                    "emailId": emailId,
                    "mobileNumber": mobileNumber,
                    "totalExperiance": totalExperiance,
                    "relatedExperiance": relatedExperiance,
                    "currentCompanyName": currentCompanyName,
                    "cctc": cctc,
                    "ectc": ectc,
                    "dos": dos,
                    "currentLocation": currentLocation,
                    "preferredLocation": preferredLocation,
                    "holdingOffer": holdingOffer,
                    "offeredCompanyName": offeredCompanyName,
                    "octc": octc,
                    "ejd": ejd,
                    "snp": snp,
                    "lwd": lwd,
                    "np": np,
                    "slot": slot,
                    "profilePosition": profilePosition,
                    "recruiterRemarks": recruiterRemarks,
                    "recruiterId": recruiterId,
                    "openingId": openingId,
                    "workAllocationId": workAllocationId
                }
                filteredData.append(dataDict)
        print(filteredData)
        return jsonify(filteredData)


api.add_resource(
    UploadProfile, '/uploadprofile/<string:adminId>')

class ProfileCrud(Resource):
    def put(self, adminId):
        jsonData = request.get_json(force=True)
        try:
            firstValue = jsonData["firstValue"]
            secondValue = jsonData["secondValue"]
            thirdValue = jsonData["thirdValue"]
            fourthValue = jsonData["fourthValue"]
            print(firstValue, secondValue)
            adminName = credentials.find({'_id': ObjectId(adminId[:24])})[
                0]["userName"]
            print(adminName)
            adminName = client[adminName]
            adminName["UploadedProfiles"].update_many({"_id":ObjectId(adminId[24:])},
            {
                "$set":{
                    firstValue: False,
                    secondValue: True,
                    thirdValue: True,
                    fourthValue: True
                }
            })
        except:
            firstValue = jsonData["firstValue"]
            secondValue = jsonData["secondValue"]
            print(firstValue, secondValue)
            adminName = credentials.find({'_id': ObjectId(adminId[:24])})[
                0]["userName"]
            print(adminName)
            adminName = client[adminName]
            adminName["UploadedProfiles"].update_many({"_id":ObjectId(adminId[24:])},
            {
                "$set":{
                    firstValue: False,
                    secondValue: True,
                }
            })
        
        return jsonify({
            "status": 200,
            "message": "Profile's status is updated."
        })

api.add_resource(ProfileCrud, "/profilecrud/<string:adminId>")



def extract_text_from_docx(docx_path):
    txt = docx2txt.process(docx_path)
    if txt:
        return txt.replace('\t', ' ')
    return None
 
 
def extract_names(txt):
    person_names = []
 
    for sent in nltk.sent_tokenize(txt):
        for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
            if hasattr(chunk, 'label') and chunk.label() == 'PERSON':
                person_names.append(
                    ' '.join(chunk_leave[0] for chunk_leave in chunk.leaves())
                )
 
    return person_names

SKILLS_DB = [
    'mysql',
    'ruby',
    'machine learning',
    'deep learning',
    'pyspark',
    'java',
    'c',
    'linux',
    'mongodb',
    'data structure'
    'data science',
    'python',
    'word',
    'excel',
    'English',
]
 
 
def extract_skills(input_text):
    print("strart1")
    stop_words = set(nltk.corpus.stopwords.words('english'))
    word_tokens = nltk.tokenize.word_tokenize(input_text)
    print("strart2")
    filtered_tokens = [w for w in word_tokens if w not in stop_words]
    filtered_tokens = [w for w in word_tokens if w.isalpha()]
    bigrams_trigrams = list(map(' '.join, nltk.everygrams(filtered_tokens, 2, 3)))
    print("strart3")
    found_skills = set()
 
    for token in filtered_tokens:
        if token.lower() in SKILLS_DB:
            found_skills.add(token)
    print("strart4")
    for ngram in bigrams_trigrams:
        if ngram.lower() in SKILLS_DB:
            found_skills.add(ngram)
    print("End")
    return list(found_skills)





class CandidateResume(Resource):
    def post(self, adminId):
        if 'file' not in request.files:
            return jsonify({
                "note1": "Key name must be file",
                "note2": "Ex. file = resume.docs"
            })

        file = request.files['file']
        # file.save(secure_filename(f.filename))

        if file.filename == '':
            return jsonify({
                "note1": " Maan gye hadd bevkoof ho",
                "note2": "Who will select file?"
            })

        if os.path.splitext(file.filename)[1] == '.docx':
            file_text = docx2txt.process(file)

            patternForEmail = re.compile(
                r'[a-zA-Z0-9-\.]+@[a-zA-Z-\.]*\.(com|edu|net)')
            matchesForEmail = patternForEmail.finditer(file_text)
            for email in matchesForEmail:
                emailId = email.group(0)

            patternforMob = re.compile(r'\d\d\d\d\d\d\d\d\d\d\d\d')
            matchesForMob = patternforMob.finditer(file_text)

            patternforMob1 = re.compile(r'\d\d\d\d\d\d\d\d\d\d')
            matchesForMob1 = patternforMob1.finditer(file_text)

            if len(list(patternforMob.finditer(file_text))) > 0:
                # Mob number with country code +911234567890
                for mob in matchesForMob:
                    phone = mob.group(0)[::-1][0:10][::-1]
            else:
                # Mob number without country code 1234567890
                for mob1 in matchesForMob1:
                    phone = mob1.group(0)

            """candidates.insert_one({
                "emailId": emailId,
                "mobileNumber": phone,
                'fileType': file.filename
            })
"""
            text = extract_text_from_docx(file)
            names = extract_names(text)
        
            if names:
                print(names[0])

            skills = extract_skills(text)
            print(skills) 

            adminName = credentials.find({'_id': ObjectId(adminId[:24])})[
            0]["userName"]
            print(adminName)
            adminName = client[adminName]
            try:
                duplicateEmailId = adminName["UploadedProfiles"].find({'emailId': emailId})[0]["emailId"]
            except:
                duplicateEmailId = False
            
            if duplicateEmailId:
                return jsonify({
                    "status": 302,
                    "msg": "This candidate is already in database."
                })

            return jsonify({
                "candidateName": names[0],
                "emailId": emailId,
                "mobileNumber": phone,
                "skills": skills
            })   


        else:
            return jsonify({
                "fileType": os.path.splitext(file.filename)[1],
                "note": "samjh nhi aarha hai tumhe abhi sirf docx file upload karo."
            })

    # def get(self):
    #     allData = candidates.find()
    #     candidatesJson = []
    #     for data in allData:
    #         id = data["_id"]
    #         email = data["email"]
    #         mobile = data["mobile"]
    #         fileType = data["fileType"]

    #         dataDict = {
    #             "id": str(id),
    #             "email": email,
    #             "mobile": mobile,
    #             "fileType": fileType
    #         }
    #         candidatesJson.append(dataDict)
    #     print(candidatesJson)
    #     return jsonify(candidatesJson)


api.add_resource(CandidateResume, '/candidateresume/<string:adminId>')

# class DailyWorkReport(Resource):
#     def get(self, adminId):
#         adminName = credentials.find({'_id': ObjectId(adminId)})[0]["userName"]
#         adminName = client[adminName]
#         adminName[]


class CandidateMail(Resource):
    def post(self):
        resumeFile = request.files["resumeFile"]
        # resumeFile.save(secure_filename(resumeFile.filename))
        resumeFile.save(os.path.join("Files", "{nameFile}".format(nameFile = resumeFile.filename)))
        print("saved")

        jsonData = request.form['jsonData']
        emailJson = json.loads(jsonData)
        senderEmail = emailJson['senderEmail']
        print("________________________________")
        print(senderEmail)
        domain = senderEmail.split('@')[1]
        print(domain)
        print("___________________________")
        senderPass = emailJson['senderPass']
        to = emailJson['candidateMail']

        jsonCc = request.form['ccEmails']
        emailCc = json.loads(jsonCc)
        cc = ','.join(emailCc)

        jsonBcc = request.form['bccEmails']
        emailBcc = json.loads(jsonBcc)
        bcc = ','.join(emailBcc)

        print(to, emailCc, emailBcc)
        compose = emailJson['compose']

        subject = "Greetings from Izeetek Solution! Open positions are waiting for you!"
        body = ""
        sender_email = senderEmail
        password = senderPass

        rcpt = cc.split(",") + bcc.split(",") + [to]

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = to
        message["Subject"] = subject
        message["Cc"] = cc
        message["Bcc"] = bcc

        text = compose
        part1 = MIMEText(text, "plain")
        message.attach(part1)
        message.attach(MIMEText(body, "plain"))

        filename = resumeFile.filename
        with open("Files/{file}".format(file = filename), "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )

        message.attach(part)
        text = message.as_string()

        context = ssl.create_default_context()

        # with smtplib.SMTP_SSL("mail.jgdtec.com", 465, context=context) as server:
        #     # with smtplib.SMTP_SSL("smtp.outlook.office365.com", 465, timeout=120, context=context) as server:
        #     server.login(sender_email, password)
        #     server.sendmail(sender_email, rcpt, text)
        if domain == "jgdtec.com":
            with smtplib.SMTP_SSL("mail.jgdtec.com", 465, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, rcpt, text)

        else:
            with smtplib.SMTP_SSL("mail.izeetek.com", 465, context=context) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, rcpt, text)

        # os.remove(resumeFile.filename)
        os.remove("Files/{nameFile}".format(nameFile = resumeFile.filename))
        print("{nameFile}".format(nameFile = resumeFile.filename), " is Removed.")
       

        return jsonify({
            "msg": "An email has been sent to candidate.",
            "status": 200
        })


api.add_resource(CandidateMail, '/candidatemail')


class ApprovedProfiles(Resource):
    def post(self, adminId):
        approvedProfileId = request.form["approvedProfileId"]
        adminName = credentials.find({'_id': ObjectId(adminId)})[0]["userName"]
        print(adminName)
        adminName = client[adminName]

        adminName["UploadedProfiles"].update_many({
            "_id": ObjectId(approvedProfileId)
        },
            {
            "$set": {
                "status": 20,
                "position": "Approved by teamlead."
            }
        })
        return jsonify({
            "status code": 200,
            "message": "This profile is approved."
        })


api.add_resource(ApprovedProfiles, "/approvedprofile/<string:adminId>")


class RejectedProfile(Resource):

    def post(self, adminId):

        rejectedProfileId = request.form["rejectedProfileId"]
        jsonData = request.form["jsonData"]
        filterData = json.loads(jsonData)
        ir = filterData["ir"]
        er = filterData["er"]
        print(rejectedProfileId)
        # profileJson = json.loads(rejectedJson)
        adminName = credentials.find({'_id': ObjectId(adminId)})[0]["userName"]
        print(adminName)
        adminName = client[adminName]
        dos = '{dt:%B} {dt.day}, {dt.year}'.format(dt=datetime.datetime.now())
        profileJson = adminName["UploadedProfiles"].find_one(
            {'_id': ObjectId(rejectedProfileId)})
        candidateName = profileJson['candidateName']
        emailId = profileJson['emailId']
        mobileNumber = profileJson['mobileNumber']
        totalExperiance = profileJson['totalExperiance']
        relatedExperiance = profileJson['relatedExperiance']
        currentCompanyName = profileJson["currentCompanyName"]
        cctc = profileJson['cctc']
        ectc = profileJson['ectc']
        np = profileJson['np']
        dos = '{dt:%B} {dt.day}, {dt.year}'.format(dt=datetime.datetime.now())
        currentLocation = profileJson['currentLocation']
        preferredLocation = profileJson["preferredLocation"]
        remarks = profileJson['remarks']
        holdingOffer = profileJson["holdingOffer"]
        offeredCompanyName = profileJson["offeredCompanyName"]
        octc = profileJson["octc"]
        ejd = profileJson["ejd"]
        snp = profileJson["snp"]
        lwd = profileJson["lwd"]
        recruiterId = profileJson["recruiterId"]
        openingId = profileJson["openingId"]
        WorkAllocationId = profileJson["workAllocationId"]

        recruiterData = employees.find_one({"_id": ObjectId(recruiterId)})
        recruiterName = recruiterData['employeeName']
        recruiterMobileNumber = recruiterData['mobileNumber']
        officeEmailId = recruiterData['officeEmailId']
        print(openingId)
        openingData = adminName["Openings"].find_one({"_id": ObjectId(openingId)})
        employeeType = openingData['employeeType']
        contractDuration = openingData['contractDuration']
        role = openingData['role']
        openingLocation = openingData['location']
        nop = openingData['nop']
        companyName = openingData['companyName']
        clientName = openingData['clientName']
        experiance = openingData['experiance']
        budgetRange = openingData['budgetRange']
        noticePeriod = openingData['noticePeriod']
        jobDescription = openingData['jobDescription']
        mandatorySkills = openingData['mandatorySkills']
        wfh = openingData['wfh']

        adminName["RejectedProfiles"].insert_one({
            "recruiterName": recruiterName,
            "recruiterMobileNumber": recruiterMobileNumber,
            "officeEmailId": officeEmailId,
            "employeeType": employeeType,
            "contractDuration": contractDuration,
            "role": role,
            "openingLocation": openingLocation,
            "nop": nop,
            "companyName": companyName,
            "clientName": clientName,
            "requiredExperiance": experiance,
            "budgetRange": budgetRange,
            "noticePeriod":noticePeriod,
            "jobDescription": jobDescription,
            "mandatorySkills": mandatorySkills,
            "wfh": wfh,
            "candidateName": candidateName,
            "emailId": emailId,
            "mobileNumber": mobileNumber,
            "totalExperiance": totalExperiance,
            "relatedExperiance": relatedExperiance,
            "currentCompanyName": currentCompanyName,
            "cctc": cctc,
            "ectc": ectc,
            "np": np,
            "dos": dos,
            "currentLocation": currentLocation,
            "preferredLocation": preferredLocation,
            "holdingOffer": holdingOffer,
            "offeredCompanyName": offeredCompanyName,
            "octc": octc,
            "ejd": ejd,
            "snp": snp,
            "lwd": lwd,
            "remarks": remarks,
            "SR": True,
            "IR": ir,
            "ER": er,
            "profilePosition": "Team Lead approval is required.",
            "openingId": openingId,
            "recruiterId": recruiterId,
            "workAllocationId": WorkAllocationId
        })

        # internalRejectedProfiles = adminName["Openings"].find({
        #     "_id": ObjectId(openingId)})[0]["internalRejectedProfiles"]
        # uploadedProfiles = adminName["Openings"].find({
        #     "_id": ObjectId(openingId)})[0]["uploadedProfiles"]

        # sharedProfiles = adminName["Openings"].find({
        #     "_id": ObjectId(openingId)})[0]["sharedProfiles"]

        # adminName["Openings"].update_many({
        #     "_id": ObjectId(openingId)
        # },
        #     {
        #     "$set": {
                # "uploadedProfiles": uploadedProfiles - 1,
                # "sharedProfiles": sharedProfiles - 1,
                # "internalRejectedProfiles": internalRejectedProfiles + 1
        #     }
        # })

        adminName["UploadedProfiles"].delete_many(
            {'_id': ObjectId(rejectedProfileId)})
        return jsonify({
            'action': 'Data id: ' + rejectedProfileId + ' is deleted!',
            "msg": "Rejected Profile is stored in database.",
            "status code": 200
        })

    def get(self, adminId):
        adminName = credentials.find({'_id': ObjectId(adminId[:24])})[
            0]["userName"]
        print(adminName)
        adminName = client[adminName]
        allData = adminName["RejectedProfiles"].find()
        profileJson = []
        for data in allData:
            openingId = data["openingId"]
            dos = data['dos']
            date_temp = dos.split()
            custom_dos = "{month}, {year}".format(
                month=date_temp[0], year=date_temp[2])
            if openingId == adminId[24:48] and (adminId[48:] == dos or adminId[48:] == custom_dos):
                id = data['_id']
                candidateName = data['candidateName']
                emailId = data['emailId']
                mobileNumber = data['mobileNumber']
                totalExperiance = data['totalExperiance']
                relatedExperiance = data['relatedExperiance']
                cctc = data['cctc']
                ectc = data['ectc']
                np = data['np']
                currentLocation = data["currentLocation"]
                preferredLocation = data["preferredLocation"]
                remarks = data['remarks']
                recruiterId = data["recruiterId"]
                profilePosition = data["profilePosition"]
                sr = data["SR"]

                dataDict = {
                    "id": str(id),
                    "candidateName": candidateName,
                    "emailId": emailId,
                    "mobileNumber": mobileNumber,
                    "totalExperiance": totalExperiance,
                    "relatedExperiance": relatedExperiance,
                    "cctc": cctc,
                    "ectc": ectc,
                    "dos": dos,
                    "currentLocation": currentLocation,
                    "preferredLocation": preferredLocation,
                    "np": np,
                    "remarks": remarks,
                    "recruiterId": recruiterId,
                    "openingId": openingId,
                    "sr": sr,
                    "position": profilePosition
                }
                profileJson.append(dataDict)
        print(profileJson)
        return jsonify(profileJson)

    def put(self, adminId):
        jsonData = request.get_json(force=True)
        filterType = jsonData["filterType"]
        print(filterType)
        adminName = credentials.find({'_id': ObjectId(adminId[:24])})[
            0]["userName"]
        print(adminName)
        adminName = client[adminName]
        # adminId[24:48]) and (dos == adminId[48:] or _dos == adminId[48:]):
        filteredData = []
        if adminId[48:]:
            mdos = adminId[48:]
            allData = adminName["RejectedProfiles"].find({"recruiterId": adminId[24:48]})
        else:
            mdos = adminId[24:]
            allData = adminName["RejectedProfiles"].find()
        for data in allData:
            _filterType = data[filterType]
            print(_filterType)
            openingId = data["openingId"]
            recruiterId = data["recruiterId"]
            dos = data['dos']
            date_temp = dos.split()
            _dos = "{month}, {year}".format(
                month=date_temp[0], year=date_temp[2])
            if _filterType and (dos == mdos or _dos == mdos):
                id = data['_id']
                recruiterName = data['recruiterName']
                recruiterMobileNumber = data['mobileNumber']
                officeEmailId = data['officeEmailId']
                employeeType = data['employeeType']
                contractDuration = data['contractDuration']
                role = data['role']
                openingLocation = data['openingLocation']
                nop = data['nop']
                companyName = data['companyName']
                clientName = data['clientName']
                requiredExperiance = data['requiredExperiance']
                budgetRange = data['budgetRange']
                noticePeriod = data['noticePeriod']
                jobDescription = data['jobDescription']
                mandatorySkills = data['mandatorySkills']
                wfh = data['wfh']
                candidateName = data['candidateName']
                emailId = data['emailId']
                mobileNumber = data['mobileNumber']
                totalExperiance = data['totalExperiance']
                relatedExperiance = data['relatedExperiance']
                currentCompanyName = data["currentCompanyName"]
                cctc = data['cctc']
                ectc = data['ectc']
                np = data['np']
                currentLocation = data['currentLocation']
                preferredLocation = data["preferredLocation"]
                holdingOffer = data["holdingOffer"]
                offeredCompanyName = data["offeredCompanyName"]
                octc = data["octc"]
                ejd = data["ejd"]
                snp = data["snp"]
                lwd = data["lwd"]
                recruiterRemarks = data["remarks"]
                profilePosition = data["profilePosition"]
                workAllocationId = data["workAllocationId"]

                dataDict = {
                    "id": str(id),
                    "recruiterName": recruiterName,
                    "recruiterMobileNumber": recruiterMobileNumber,
                    "officeEmailId": officeEmailId,
                    "employeeType": employeeType,
                    "contractDuration": contractDuration,
                    "role": role,
                    "openingLocation": openingLocation,
                    "nop": nop,
                    "companyName": companyName,
                    "clientName": clientName,
                    "requiredExperiance": requiredExperiance,
                    "budgetRange": budgetRange,
                    "noticePeriod":noticePeriod,
                    "jobDescription": jobDescription,
                    "mandatorySkills": mandatorySkills,
                    "wfh": wfh,
                    "candidateName": candidateName,
                    "emailId": emailId,
                    "mobileNumber": mobileNumber,
                    "totalExperiance": totalExperiance,
                    "relatedExperiance": relatedExperiance,
                    "currentCompanyName": currentCompanyName,
                    "cctc": cctc,
                    "ectc": ectc,
                    "dos": dos,
                    "currentLocation": currentLocation,
                    "preferredLocation": preferredLocation,
                    "holdingOffer": holdingOffer,
                    "offeredCompanyName": offeredCompanyName,
                    "octc": octc,
                    "ejd": ejd,
                    "snp": snp,
                    "lwd": lwd,
                    "np": np,
                    "profilePosition": profilePosition,
                    "recruiterRemarks": recruiterRemarks,
                    "recruiterId": recruiterId,
                    "openingId": openingId,
                    "workAllocationId": workAllocationId
                }
                filteredData.append(dataDict)
        print(filteredData)
        return jsonify(filteredData)


api.add_resource(
    RejectedProfile, '/rejectedprofile/<string:adminId>')



class JoinedProfile(Resource):

    def post(self, adminId):

        joinedProfileId = request.form["joinedProfileId"]
        jsonData = request.form["jsonData"]
        filterData = json.loads(jsonData)
        j = filterData["j"]
        do = filterData["do"]
        print(joinedProfileId)
        # profileJson = json.loads(rejectedJson)
        adminName = credentials.find({'_id': ObjectId(adminId)})[0]["userName"]
        print(adminName)
        adminName = client[adminName]
        dos = '{dt:%B} {dt.day}, {dt.year}'.format(dt=datetime.datetime.now())
        profileJson = adminName["UploadedProfiles"].find_one(
            {'_id': ObjectId(joinedProfileId)})
        candidateName = profileJson['candidateName']
        emailId = profileJson['emailId']
        mobileNumber = profileJson['mobileNumber']
        totalExperiance = profileJson['totalExperiance']
        relatedExperiance = profileJson['relatedExperiance']
        currentCompanyName = profileJson["currentCompanyName"]
        cctc = profileJson['cctc']
        ectc = profileJson['ectc']
        np = profileJson['np']
        dos = '{dt:%B} {dt.day}, {dt.year}'.format(dt=datetime.datetime.now())
        currentLocation = profileJson['currentLocation']
        preferredLocation = profileJson["preferredLocation"]
        remarks = profileJson['remarks']
        holdingOffer = profileJson["holdingOffer"]
        offeredCompanyName = profileJson["offeredCompanyName"]
        octc = profileJson["octc"]
        ejd = profileJson["ejd"]
        snp = profileJson["snp"]
        lwd = profileJson["lwd"]
        recruiterId = profileJson["recruiterId"]
        openingId = profileJson["openingId"]
        WorkAllocationId = profileJson["workAllocationId"]

        recruiterData = employees.find_one({"_id": ObjectId(recruiterId)})
        recruiterName = recruiterData['employeeName']
        recruiterMobileNumber = recruiterData['mobileNumber']
        officeEmailId = recruiterData['officeEmailId']
        print(openingId)
        openingData = adminName["Openings"].find_one({"_id": ObjectId(openingId)})
        employeeType = openingData['employeeType']
        contractDuration = openingData['contractDuration']
        role = openingData['role']
        openingLocation = openingData['location']
        nop = openingData['nop']
        companyName = openingData['companyName']
        clientName = openingData['clientName']
        experiance = openingData['experiance']
        budgetRange = openingData['budgetRange']
        noticePeriod = openingData['noticePeriod']
        jobDescription = openingData['jobDescription']
        mandatorySkills = openingData['mandatorySkills']
        wfh = openingData['wfh']

        adminName["JoinedProfiles"].insert_one({
            "recruiterName": recruiterName,
            "recruiterMobileNumber": recruiterMobileNumber,
            "officeEmailId": officeEmailId,
            "employeeType": employeeType,
            "contractDuration": contractDuration,
            "role": role,
            "openingLocation": openingLocation,
            "nop": nop,
            "companyName": companyName,
            "clientName": clientName,
            "requiredExperiance": experiance,
            "budgetRange": budgetRange,
            "noticePeriod":noticePeriod,
            "jobDescription": jobDescription,
            "mandatorySkills": mandatorySkills,
            "wfh": wfh,
            "candidateName": candidateName,
            "emailId": emailId,
            "mobileNumber": mobileNumber,
            "totalExperiance": totalExperiance,
            "relatedExperiance": relatedExperiance,
            "currentCompanyName": currentCompanyName,
            "cctc": cctc,
            "ectc": ectc,
            "np": np,
            "dos": dos,
            "currentLocation": currentLocation,
            "preferredLocation": preferredLocation,
            "holdingOffer": holdingOffer,
            "offeredCompanyName": offeredCompanyName,
            "octc": octc,
            "ejd": ejd,
            "snp": snp,
            "lwd": lwd,
            "remarks": remarks,
            "J": j,
            "DO": do,
            "profilePosition": "Team Lead approval is required.",
            "openingId": openingId,
            "recruiterId": recruiterId,
            "workAllocationId": WorkAllocationId
        })

        # internalRejectedProfiles = adminName["Openings"].find({
        #     "_id": ObjectId(openingId)})[0]["internalRejectedProfiles"]
        # uploadedProfiles = adminName["Openings"].find({
        #     "_id": ObjectId(openingId)})[0]["uploadedProfiles"]

        # sharedProfiles = adminName["Openings"].find({
        #     "_id": ObjectId(openingId)})[0]["sharedProfiles"]

        # adminName["Openings"].update_many({
        #     "_id": ObjectId(openingId)
        # },
        #     {
        #     "$set": {
                # "uploadedProfiles": uploadedProfiles - 1,
                # "sharedProfiles": sharedProfiles - 1,
                # "internalRejectedProfiles": internalRejectedProfiles + 1
        #     }
        # })

        adminName["UploadedProfiles"].delete_many(
            {'_id': ObjectId(joinedProfileId)})
        return jsonify({
            'action': 'Data id: ' + joinedProfileId + ' is deleted!',
            "msg": "Rejected Profile is stored in database.",
            "status code": 200
        })

    def get(self, adminId):
        adminName = credentials.find({'_id': ObjectId(adminId[:24])})[
            0]["userName"]
        print(adminName)
        adminName = client[adminName]
        allData = adminName["JoinedProfiles"].find()
        profileJson = []
        for data in allData:
            openingId = data["openingId"]
            dos = data['dos']
            date_temp = dos.split()
            custom_dos = "{month}, {year}".format(
                month=date_temp[0], year=date_temp[2])
            if openingId == adminId[24:48] and (adminId[48:] == dos or adminId[48:] == custom_dos):
                id = data['_id']
                candidateName = data['candidateName']
                emailId = data['emailId']
                mobileNumber = data['mobileNumber']
                totalExperiance = data['totalExperiance']
                relatedExperiance = data['relatedExperiance']
                cctc = data['cctc']
                ectc = data['ectc']
                np = data['np']
                currentLocation = data["currentLocation"]
                preferredLocation = data["preferredLocation"]
                remarks = data['remarks']
                recruiterId = data["recruiterId"]
                profilePosition = data["profilePosition"]
                j = data["J"]

                dataDict = {
                    "id": str(id),
                    "candidateName": candidateName,
                    "emailId": emailId,
                    "mobileNumber": mobileNumber,
                    "totalExperiance": totalExperiance,
                    "relatedExperiance": relatedExperiance,
                    "cctc": cctc,
                    "ectc": ectc,
                    "dos": dos,
                    "currentLocation": currentLocation,
                    "preferredLocation": preferredLocation,
                    "np": np,
                    "remarks": remarks,
                    "recruiterId": recruiterId,
                    "openingId": openingId,
                    "j": j,
                    "position": profilePosition
                }
                profileJson.append(dataDict)
        print(profileJson)
        return jsonify(profileJson)

    def put(self, adminId):
        jsonData = request.get_json(force=True)
        filterType = jsonData["filterType"]
        print(filterType)
        adminName = credentials.find({'_id': ObjectId(adminId[:24])})[
            0]["userName"]
        print(adminName)
        adminName = client[adminName]
        # adminId[24:48]) and (dos == adminId[48:] or _dos == adminId[48:]):
        filteredData = []
        if adminId[48:]:
            mdos = adminId[48:]
            allData = adminName["JoinedProfiles"].find({"recruiterId": adminId[24:48]})
        else:
            mdos = adminId[24:]
            allData = adminName["JoinedProfiles"].find()
        for data in allData:
            _filterType = data[filterType]
            print(_filterType)
            openingId = data["openingId"]
            recruiterId = data["recruiterId"]
            dos = data['dos']
            date_temp = dos.split()
            _dos = "{month}, {year}".format(
                month=date_temp[0], year=date_temp[2])
            if _filterType and (dos == mdos or _dos == mdos):
                id = data['_id']
                recruiterName = data['recruiterName']
                recruiterMobileNumber = data['mobileNumber']
                officeEmailId = data['officeEmailId']
                employeeType = data['employeeType']
                contractDuration = data['contractDuration']
                role = data['role']
                openingLocation = data['openingLocation']
                nop = data['nop']
                companyName = data['companyName']
                clientName = data['clientName']
                requiredExperiance = data['requiredExperiance']
                budgetRange = data['budgetRange']
                noticePeriod = data['noticePeriod']
                jobDescription = data['jobDescription']
                mandatorySkills = data['mandatorySkills']
                wfh = data['wfh']
                candidateName = data['candidateName']
                emailId = data['emailId']
                mobileNumber = data['mobileNumber']
                totalExperiance = data['totalExperiance']
                relatedExperiance = data['relatedExperiance']
                currentCompanyName = data["currentCompanyName"]
                cctc = data['cctc']
                ectc = data['ectc']
                np = data['np']
                currentLocation = data['currentLocation']
                preferredLocation = data["preferredLocation"]
                holdingOffer = data["holdingOffer"]
                offeredCompanyName = data["offeredCompanyName"]
                octc = data["octc"]
                ejd = data["ejd"]
                snp = data["snp"]
                lwd = data["lwd"]
                recruiterRemarks = data["remarks"]
                profilePosition = data["profilePosition"]
                workAllocationId = data["workAllocationId"]

                dataDict = {
                    "id": str(id),
                    "recruiterName": recruiterName,
                    "recruiterMobileNumber": recruiterMobileNumber,
                    "officeEmailId": officeEmailId,
                    "employeeType": employeeType,
                    "contractDuration": contractDuration,
                    "role": role,
                    "openingLocation": openingLocation,
                    "nop": nop,
                    "companyName": companyName,
                    "clientName": clientName,
                    "requiredExperiance": requiredExperiance,
                    "budgetRange": budgetRange,
                    "noticePeriod":noticePeriod,
                    "jobDescription": jobDescription,
                    "mandatorySkills": mandatorySkills,
                    "wfh": wfh,
                    "candidateName": candidateName,
                    "emailId": emailId,
                    "mobileNumber": mobileNumber,
                    "totalExperiance": totalExperiance,
                    "relatedExperiance": relatedExperiance,
                    "currentCompanyName": currentCompanyName,
                    "cctc": cctc,
                    "ectc": ectc,
                    "dos": dos,
                    "currentLocation": currentLocation,
                    "preferredLocation": preferredLocation,
                    "holdingOffer": holdingOffer,
                    "offeredCompanyName": offeredCompanyName,
                    "octc": octc,
                    "ejd": ejd,
                    "snp": snp,
                    "lwd": lwd,
                    "np": np,
                    "profilePosition": profilePosition,
                    "recruiterRemarks": recruiterRemarks,
                    "recruiterId": recruiterId,
                    "openingId": openingId,
                    "workAllocationId": workAllocationId
                }
                filteredData.append(dataDict)
        print(filteredData)
        return jsonify(filteredData)


api.add_resource(
    JoinedProfile, '/joinedprofile/<string:adminId>')


class SharedProfile(Resource):

    def post(self, adminId):
        uploadedProfileId = request.form["sharedProfileId"]
        print(uploadedProfileId)
        # profileJson = json.loads(rejectedJson)
        # now = datetime.now()
        # dt_string = now.strftime("%B %d, %Y %H:%M:%S")

        adminName = credentials.find({'_id': ObjectId(adminId)})[0]["userName"]
        print(adminName)
        adminName = client[adminName]
        sharedProfileData = adminName["UploadedProfiles"].find_one(
            {'_id': ObjectId(uploadedProfileId)})
        
        recruiterName = sharedProfileData["recruiterName"]
        recruiterMobileNumber = sharedProfileData["recruiterMobileNumber"]
        officeEmailId = sharedProfileData["officeEmailId"]
        employeeType = sharedProfileData["employeeType"]
        contractDuration = sharedProfileData["contractDuration"]
        role = sharedProfileData["role"]
        openingLocation = sharedProfileData["openingLocation"]
        nop = sharedProfileData["nop"]
        companyName = sharedProfileData["companyName"]
        clientName = sharedProfileData["clientName"]
        requiredExperiance = sharedProfileData["requiredExperiance"]
        budgetRange = sharedProfileData["budgetRange"]
        noticePeriod = sharedProfileData["noticePeriod"]
        jobDescription = sharedProfileData["jobDescription"]
        mandatorySkills = sharedProfileData["mandatorySkills"]
        wfh = sharedProfileData["wfh"]
        slot = sharedProfileData["slot"]
        candidateName = sharedProfileData["candidateName"]
        emailId = sharedProfileData["emailId"]
        mobileNumber = sharedProfileData["mobileNumber"]
        totalExperiance = sharedProfileData["totalExperiance"]
        relatedExperiance = sharedProfileData["relatedExperiance"]
        currentCompanyName = sharedProfileData["currentCompanyName"]
        cctc = sharedProfileData["cctc"]
        ectc = sharedProfileData["ectc"]
        np = sharedProfileData["np"]
        currentLocation = sharedProfileData["currentLocation"]
        preferredLocation = sharedProfileData["preferredLocation"]
        holdingOffer = sharedProfileData["holdingOffer"]
        offeredCompanyName = sharedProfileData["offeredCompanyName"]
        octc = sharedProfileData["octc"]
        ejd = sharedProfileData["ejd"]
        snp = sharedProfileData["snp"]
        lwd = sharedProfileData["lwd"]
        recruiterRemarks = sharedProfileData["remarks"]
        recruiterId = sharedProfileData["recruiterId"]
        openingId = sharedProfileData["openingId"]
        workAllocationId = sharedProfileData["workAllocationId"]

        # adminName["SharedProfiles"].insert_one({
        #     "recruiterName": recruiterName,
        #     "recruiterMobileNumber": recruiterMobileNumber,
        #     "officeEmailId": officeEmailId,
        #     "employeeType": employeeType,
        #     "contractDuration": contractDuration,
        #     "role": role,
        #     "openingLocation": openingLocation,
        #     "nop": nop,
        #     "companyName": companyName,
        #     "clientName": clientName,
        #     "requiredExperiance": requiredExperiance,
        #     "budgetRange": budgetRange,
        #     "noticePeriod":noticePeriod,
        #     "jobDescription": jobDescription,
        #     "mandatorySkills": mandatorySkills,
        #     "wfh": wfh,
        #     "slot": slot,
        #     "candidateName": candidateName,
        #     "emailId": emailId,
        #     "mobileNumber": mobileNumber,
        #     "totalExperiance": totalExperiance,
        #     "relatedExperiance": relatedExperiance,
        #     "currentCompanyName": currentCompanyName,
        #     "cctc": cctc,
        #     "ectc": ectc,
        #     "np": np,
        #     "currentLocation": currentLocation,
        #     "preferredLocation": preferredLocation,
        #     "position": "Team Lead approval is required.",
        #     "holdingOffer": holdingOffer,
        #     "offeredCompanyName": offeredCompanyName,
        #     "octc": octc,
        #     "ejd": ejd,
        #     "snp": snp,
        #     "lwd": lwd,
        #     "recruiterRemarks": recruiterRemarks,
        #     "dos": '{dt:%B} {dt.day}, {dt.year}'.format(dt=datetime.datetime.now()),
        #     "position": "Shared with client",
        #     "status": 10,
        #     "recruiterId": recruiterId,
        #     "openingId": openingId,
        #     "workAllocationId": workAllocationId,
        #     "uploadedProfileId": uploadedProfileId
        # })

        # uploadedProfiles = adminName["Openings"].find({
        #     "_id": ObjectId(openingId)})[0]["uploadedProfiles"]

        # sharedProfiles = adminName["Openings"].find({
        #     "_id": ObjectId(openingId)})[0]["sharedProfiles"]

        adminName["Openings"].update_many({
            "_id": ObjectId(openingId)
        },
            {
            "$set": {
                "status": 40,
                "position": "Profile has shared with client by teamlead for this opening.",
                # "uploadedProfiles": uploadedProfiles - 1,
                # "sharedProfiles": sharedProfiles + 1,
            }
        })

        adminName["Work-Allocation"].update_many({
            "openingId": openingId,
            "recruiterId": recruiterId
        },
            {
            "$set": {
                "status": 30,
                "position": "Profile has shared with client by teamlead for this opening.",
            }
        })

        # adminName["UploadedProfiles"].delete_many(
        #     {'_id': ObjectId(uploadedProfileId)})

        adminName["UploadedProfiles"].update_many({
            "_id": ObjectId(uploadedProfileId)
        },
            {
            "$set": {
                "profilePosition": "Profile has shared with client by teamlead for this opening.",
                "SWC": True,
                "SFP": False
            }
        })

        return jsonify({
            'action': 'Data id: ' + uploadedProfileId + ' is deleted!',
            "msg": "Shared Profile is stored in database.",
            "status code": 200
        })

    def get(self, adminId):
        adminName = credentials.find({'_id': ObjectId(adminId[:24])})[
            0]["userName"]
        print(adminName)
        adminName = client[adminName]
        allData = adminName["UploadedProfiles"].find()
        profileJson = []
        for data in allData:
            swc = data["SWC"]
            openingId = data["openingId"]
            dos = data['dos']
            date_temp = dos.split()
            custom_dos = "{month}, {year}".format(
                month=date_temp[0], year=date_temp[2])
            # print("openingId:", adminId[24:48], "custom:", custom_dos, "dos:", dos, "indate:", adminId[48:])
            if swc and (openingId == adminId[24:48] and (adminId[48:] == dos or adminId[48:] == custom_dos)):
                id = data['_id']
                recruiterName = data['recruiterName']
                recruiterMobileNumber = data['mobileNumber']
                officeEmailId = data['officeEmailId']
                employeeType = data['employeeType']
                contractDuration = data['contractDuration']
                role = data['role']
                openingLocation = data['openingLocation']
                nop = data['nop']
                companyName = data['companyName']
                clientName = data['clientName']
                requiredExperiance = data['requiredExperiance']
                budgetRange = data['budgetRange']
                noticePeriod = data['noticePeriod']
                jobDescription = data['jobDescription']
                mandatorySkills = data['mandatorySkills']
                wfh = data['wfh']
                slot = data["slot"]
                candidateName = data['candidateName']
                emailId = data['emailId']
                mobileNumber = data['mobileNumber']
                totalExperiance = data['totalExperiance']
                relatedExperiance = data['relatedExperiance']
                currentCompanyName = data["currentCompanyName"]
                cctc = data['cctc']
                ectc = data['ectc']
                np = data['np']
                currentLocation = data['currentLocation']
                preferredLocation = data["preferredLocation"]
                holdingOffer = data["holdingOffer"]
                offeredCompanyName = data["offeredCompanyName"]
                octc = data["octc"]
                ejd = data["ejd"]
                snp = data["snp"]
                lwd = data["lwd"]
                recruiterRemarks = data["remarks"]
                # status = data["status"]
                position = data["profilePosition"]
                recruiterId = data["recruiterId"]
                workAllocationId = data["workAllocationId"]

                dataDict = {
                    "id": str(id),
                    "recruiterName": recruiterName,
                    "recruiterMobileNumber": recruiterMobileNumber,
                    "officeEmailId": officeEmailId,
                    "employeeType": employeeType,
                    "contractDuration": contractDuration,
                    "role": role,
                    "openingLocation": openingLocation,
                    "nop": nop,
                    "companyName": companyName,
                    "clientName": clientName,
                    "requiredExperiance": requiredExperiance,
                    "budgetRange": budgetRange,
                    "noticePeriod":noticePeriod,
                    "jobDescription": jobDescription,
                    "mandatorySkills": mandatorySkills,
                    "wfh": wfh,
                    "candidateName": candidateName,
                    "emailId": emailId,
                    "mobileNumber": mobileNumber,
                    "totalExperiance": totalExperiance,
                    "relatedExperiance": relatedExperiance,
                    "currentCompanyName": currentCompanyName,
                    "cctc": cctc,
                    "ectc": ectc,
                    "dos": dos,
                    "currentLocation": currentLocation,
                    "preferredLocation": preferredLocation,
                    "holdingOffer": holdingOffer,
                    "offeredCompanyName": offeredCompanyName,
                    "octc": octc,
                    "ejd": ejd,
                    "snp": snp,
                    "lwd": lwd,
                    "np": np,
                    "slot": slot,
                    # "status": status,
                    "position": position,
                    "recruiterRemarks": recruiterRemarks,
                    "recruiterId": recruiterId,
                    "openingId": openingId,
                    "workAllocationId": workAllocationId,
                }
                profileJson.append(dataDict)
        print(profileJson)
        return jsonify(profileJson)


api.add_resource(
    SharedProfile, '/sharedprofile/<string:adminId>')


class ScheduleTask(Resource):
    def post(self, adminId):
        scheduledForm = request.form["scheduledForm"]
        scheduledJson = json.loads(scheduledForm)
        # scheduledJson = request.get_json(force=True)
        date = scheduledJson["date"]
        task = scheduledJson["task"]
        employeeId = scheduledJson["employeeId"]
        employeeName= scheduledJson["userName"]
        # now = datetime.now()
        # dt_string = now.strftime("%B %d, %Y %H:%M:%S")

        try:
            docFile = request.files["docFile"]
            docFile.save(secure_filename(docFile.filename))
            os.rename(docFile.filename, "{employeeName}{date}.pdf".format(employeeName = employeeName, date = date))
            with open("{employeeName}{date}.pdf".format(employeeName = employeeName, date = date), 'rb') as f:
                contents = f.read()
            
            fs1 = gridfs.GridFS(adminName)
            fs1.put(contents, filename="{employeeName}{date}.pdf".format(employeeName = employeeName, date = date))
            os.remove("{employeeName}{date}.pdf".format(employeeName = employeeName, date = date))
            print("{employeeName}{date}.pdf".format(employeeName = employeeName, date = date), " is Removed.")


        except:
            print("No file.")

        adminName = credentials.find({'_id': ObjectId(adminId[:24])})[
            0]["userName"]
        print(adminName)
        adminName = client[adminName]
        adminName["Schedule-Task"].insert_one({
            "date": date,
            "task": task,
            "status": "Pending",
            "dt": '{dt:%B} {dt.day}, {dt.year}'.format(dt=datetime.datetime.now()),
            "employeeId": employeeId
        })

        return jsonify({
            "date": date,
            "task": task,
            "status": "Pending",
            "dt": '{dt:%B} {dt.day}, {dt.year}'.format(dt=datetime.datetime.now()),
            "statusCode": 200
        })

    def get(self, adminId):
        adminName = credentials.find({'_id': ObjectId(adminId[:24])})[
            0]["userName"]
        print(adminName)
        adminName = client[adminName]
        allData = adminName["Schedule-Task"].find()
        scheduledJson = []
        for data in allData:
            employeeId = data["employeeId"]
            if employeeId == adminId[24:]:
                _id = data["_id"]
                date = data["date"]
                task = data["task"]
                status = data["status"]
                dt = data["dt"]

                dataDict = {
                    "id": str(_id),
                    "date": date,
                    "task": task,
                    "status": status,
                    "dt": dt,
                    "employeeId": employeeId
                }
                scheduledJson.append(dataDict)

        print(scheduledJson)
        return jsonify(scheduledJson)

    def put(self, adminId):
        scheduledJson = request.get_json(force=True)

        # status = request.args.get('status')
        # print(status)
        # taskId = request.args.get('taskId')
        # print(taskId)
        status = scheduledJson["status"]
        taskId = scheduledJson["taskId"]
        # now = datetime.now()
        # dt_string = now.strftime("%B %d, %Y %H:%M:%S")

        adminName = credentials.find({'_id': ObjectId(adminId[:24])})[
            0]["userName"]
        print(adminName)
        adminName = client[adminName]
        adminName["Schedule-Task"].update_many({
            "_id": ObjectId(taskId)
        },
            {
            "$set": {
                "status": status,
                "dt": '{dt:%B} {dt.day}, {dt.year}'.format(dt=datetime.datetime.now())
            }
        })
        return jsonify({
            "statusCode": 200,
            "message": "Updated !"
        })


api.add_resource(ScheduleTask, '/scheduletask/<string:adminId>')


class TestApi(Resource):
    def post(self):
        jsonData = request.get_json(True)
        ind_time = datetime.datetime.now(timezone("Asia/Kolkata")
                                         ).strftime('%Y-%m-%d %H:%M:%S.%f')
        lightStatus = jsonData["lightStatus"]
        testDb.insert_one({
            "datetime": ind_time,
            "lightStatus": lightStatus
        })
        return jsonify({
            "server-status": 200,
            "message": "Data is storted in database. Thankyou !",
            "datetime": ind_time,
            "lightStatus": lightStatus
        })

    def get(self):
        allData = testDb.find()
        jsonData = []
        for data in allData:
            _id = data["_id"]
            date_time = data["datetime"]
            lightStatus = data["lightStatus"]
            dataDict = {
                "id": str(_id),
                "date": date_time,
                "lightStatus": lightStatus
            }
            jsonData.append(dataDict)
        print(jsonData)
        return jsonify(jsonData)


api.add_resource(TestApi, "/embeddedapi")


class AddDomain(Resource):
    def post(self, adminId):
        domainJson = request.form["domainJson"]
        domainData = json.loads(domainJson)
        domain = domainData["domain"]
        subDomains = request.form["subDomain"]

        adminName = credentials.find({'_id': ObjectId(adminId[:24])})[
            0]["userName"]
        print(adminName)
        adminName = client[adminName]
        isExist = adminName["Domains"].find_one({"domain": domain})
        if isExist:
            adminName["Domains"].update_one({"domain": domain},{
                "$set":{
                    "subDomains": subDomains,
                    "dt": '{dt:%B} {dt.day}, {dt.year}'.format(dt=datetime.datetime.now())
                    }
                })
                
            return jsonify({
            "status": 201,
            "msg": "This domain is already exist.So it's updated."
            })

        else:
            adminName["Domains"].insert_one({
            "domain": domain,
            "subDomains": subDomains,
            "dt": '{dt:%B} {dt.day}, {dt.year}'.format(dt=datetime.datetime.now())
            })
            return jsonify({
            "status": 200,
            "msg": "This new domain {dom} is added.Thanks !".format(dom = domain)
            })


    def get(self, adminId):
        adminName = credentials.find({'_id': ObjectId(adminId[:24])})[
            0]["userName"]
        print(adminName)
        adminName = client[adminName]
        if adminId[24:]:
            subDomains= adminName["Domains"].find(
                {"_id": ObjectId(adminId[24:])})[0]["subDomains"]
            print(subDomains)
            return jsonify(subDomains)
        else:
            allData = adminName["Domains"].find()
            domainsJson = []
            for data in allData:
                _id = data["_id"]
                domains = data["domain"]
                print(domains)
                dataDict = {
                    "id": str(_id),
                    "domains": domains
                }
                domainsJson.append(dataDict)

            print(domainsJson)
            return jsonify(domainsJson)


api.add_resource(AddDomain, "/domains/<string:adminId>")

class FileHandling(Resource):
    def get(self, userName):
        file_ = recruitmentManagement.fs.files.find_one({
            'filename': "{}.jpg".format(userName)
        })
        file_id = file_['_id']
        wrapper = fs.get(file_id)
        response = Response(wrapper, content_type="")
        return response


api.add_resource(FileHandling, "/filehandling/<string:userName>")

class DocHandling(Resource):
    def get(self, adminId):
        print(adminId[24:])
        adminName = credentials.find({'_id': ObjectId(adminId[:24])})[
            0]["userName"]
        print(adminName)
        adminName = client[adminName]
        fs1 = gridfs.GridFS(adminName)
        file_ = adminName.fs.files.find_one({
            'filename': "{}.pdf".format(adminId[24:])
        })
        file_id = file_['_id']
        wrapper = fs1.get(file_id)
        response = Response(wrapper, content_type="application/pdf")
        print(type(response))
        return response


api.add_resource(DocHandling, "/dochandling/<string:adminId>")

class UserDocHandling(Resource):
    def get(self, userName):
        print(userName)
        file_ = recruitmentManagement.fs.files.find_one({
            'filename': "{}.pdf".format(userName)
        })
        file_id = file_['_id']
        wrapper = fs.get(file_id)
        response = Response(wrapper, content_type="application/pdf")
        print(type(response))
        return response


api.add_resource(UserDocHandling, "/userdochandling/<string:userName>")

class ScheduleDocHandling(Resource):
    def get(self, userName):
        file_ = recruitmentManagement.fs.files.find_one({
            'filename': "{}.pdf".format(userName)
        })
        file_id = file_['_id']
        wrapper = fs.get(file_id)
        response = Response(wrapper, content_type="application/pdf")
        print(type(response))
        return response


api.add_resource(ScheduleDocHandling, "/scheduleDochandling/<string:userName>")

class CompanyCrud(Resource):
    def get(self, adminId):
        adminName = credentials.find(
            {"_id": ObjectId(adminId[:24])})[0]["userName"]
        print(adminName)
        adminName = client[adminName]
        allData = adminName["Companies"].find_one({"_id": ObjectId(adminId[24:])})
        jsonData = []
        
        companyName = allData["companyName"]
        companyUrl = allData["companyURL"]
        location = allData["location"]
        remarks = allData["remarks"]
        dataDict = {
            "companyName": companyName,
            "companyUrl": companyUrl,
            "location": location,
            "remarks": remarks,
            "status": 200
        }
        jsonData.append(dataDict)
        print(jsonData)
        return jsonify(jsonData)

api.add_resource(CompanyCrud, "/companycrud/<string:adminId>")

class ClientCrud(Resource):
    def get(self, adminId):
        adminName = credentials.find(
            {"_id": ObjectId(adminId[:24])})[0]["userName"]
        print(adminName)
        adminName = client[adminName]
        allData = adminName["Clients"].find_one({"_id": ObjectId(adminId[24:])})
        jsonData = []
        
        companyName = allData["companyName"]
        clientName = allData["clientName"]
        clientUrl = allData["clientURL"]
        branches = allData["branches"]
        remarks = allData["remarks"]
        dataDict = {
            "companyName": companyName,
            "clientName": clientName,
            "clientUrl": clientUrl,
            "location": branches,
            "remarks": remarks,
            "status": 200
        }
        jsonData.append(dataDict)
        print(jsonData)
        return jsonify(jsonData)

api.add_resource(ClientCrud, "/clientcrud/<string:adminId>")


class OutlookEmail(Resource):
    def post(self):
        import win32com.client as win32

        jsonData = request.form['jsonData']
        emailJson = json.loads(jsonData)
        to = emailJson['candidateMail']

        olApp = win32.Dispatch('Outlook.Application')
        mailItem = olApp.CreateItem(0)
        mailItem.Subject = 'Recruitement Management'
        mailItem.BodyFormat = 1
        mailItem.Body = ""
        mailItem.To = to
        mailItem.Sensitivity = 2
        # mailItem.Attachments.Add('C:\\Users\\DELL\\Desktop\\JGDTech\\test\\gridFS\\Java.pdf')
        
        mailItem.CC = 'dhanpati.sahu@jgdtec.com'
        mailItem.BCC = 'ai@izeetek.com'
        # optional (account you want to use to send the email)
        # mailItem._oleobj_.Invoke(*(64209, 0, 8, 0, olNS.Accounts.Item('<email@gmail.com')))
        mailItem.Display(True)
        mailItem.Save()
        mailItem.Send()

        return jsonify({
            "message": "Email sent to candidate."
        })


api.add_resource(OutlookEmail, "/outlookmail")

class AddLocation(Resource):
    def post(self, adminId):
        locationJson = request.form["locationJson"]
        locationData = json.loads(locationJson)
        location = locationData["location"]

        adminName = credentials.find({'_id': ObjectId(adminId[:24])})[
            0]["userName"]
        print(adminName)
        adminName = client[adminName]

        isExistLocation = adminName["Locations"].find_one({"location": location})
        print(isExistLocation)
        if isExistLocation:
            return jsonify({
                "status": 302,
                "msg": "{loc} is already exist.".format(loc = location)
                })
        else:
            adminName["Locations"].insert_one({
                "location": location,
                "dt": '{dt:%B} {dt.day}, {dt.year}'.format(dt=datetime.datetime.now())
            })
            return jsonify({
            "status": 200,
            "msg": "New location {loc} is added.".format(loc = location)
            })

    def get(self, adminId):
        adminName = credentials.find({'_id': ObjectId(adminId)})[
            0]["userName"]
        print(adminName)
        adminName = client[adminName]
        allData = adminName["Locations"].find()
        locationsJson = []
        for data in allData:
            _id = data["_id"]
            location = data["location"]
            print(location)
            dataDict = {
                "id": str(_id),
                "location": location
            }
            locationsJson.append(dataDict)

        print(locationsJson)
        return jsonify(locationsJson)


api.add_resource(AddLocation, "/locations/<string:adminId>")

class RandomFileAdding(Resource):
    def post(self, userName):
        docFile = request.files["file"]

        docFile.save(secure_filename(docFile.filename))
        os.rename(docFile.filename, "{userName}.pdf".format(userName = userName))

        with open("{userName}.pdf".format(userName = userName), 'rb') as f:
            contents = f.read()

        fs.put(contents, filename="{userName}.pdf".format(userName = userName))
        os.remove("{userName}.pdf".format(userName = userName))
        print("{userName}.pdf".format(userName = userName), " is Removed.")

api.add_resource(RandomFileAdding, "/randomfile/<string:userName>")


if __name__ == "__main__":
    app.run(debug=True)
