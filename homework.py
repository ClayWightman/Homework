#!/usr/bin/env python3
import json                     #for converting json objects into python dicts
import os, os.path              #for file naviagation
from datetime import datetime   #for the error logger
import requests                 #for downloading the PDF's by their URL
import time                     #for implementing "busy wait" to cut down on CPU overhead
import mysql.connector          #for connecting to a mySQL database


#Should only be used if table does not already exist.  Included mainly to show the datatypes I used for each json object as well as the structure of my table
#This table uses id as the primary ID.  If a duplicate file is put inside of the .json directory this program will stop at that .json file
def create_table(mycursor):
    mycursor.execute("CREATE TABLE metadata (id VARCHAR(255) NOT NULL, \
        to_name VARCHAR(255), to_company VARCHAR(255), to_address_zip VARCHAR(10), to_address_city VARCHAR(255), to_address_line1 VARCHAR(255), to_address_line2 VARCHAR(255), to_address_state VARCHAR(255), to_address_country VARCHAR(255),\
        from_name VARCHAR(255),from_company VARCHAR(255), from_address_zip VARCHAR(10), from_address_city VARCHAR(255), from_address_line1 VARCHAR(255), from_address_line2 VARCHAR(255), from_address_state VARCHAR(255), from_address_country VARCHAR(255),\
            size VARCHAR(255), object VARCHAR(255), imb_code VARCHAR(255), priority INT, mail_sort VARCHAR(255), mail_type VARCHAR(255), press_proof VARCHAR(255), file_created_at VARCHAR(255), PRIMARY KEY (id))")

#Where the info in the .json file is actually inserted into the database
def insert_in_database(json_dict, mycursor, mydb):
    sql = "INSERT INTO metadata (id,to_name,to_company,to_address_zip,to_address_city,to_address_line1,to_address_line2,to_address_state,to_address_country,from_name,from_company,from_address_zip,from_address_city,from_address_line1,from_address_line2,from_address_state,from_address_country,size,object,imb_code,priority,mail_sort,mail_type,press_proof,file_created_at) "\
        "VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',%s,'%s','%s','%s','%s')"\
             %(json_dict['id'],json_dict['to']['name'],json_dict['to']['company'],json_dict['to']['address_zip'],json_dict['to']['address_city'],json_dict['to']['address_line1'],json_dict['to']['address_line2'],json_dict['to']['address_state'],json_dict['to']['address_country'],\
                 json_dict['from']['name'],json_dict['from']['company'],json_dict['from']['address_zip'],json_dict['from']['address_city'],json_dict['from']['address_line1'],json_dict['from']['address_line2'],json_dict['from']['address_state'],json_dict['from']['address_country'],\
                 json_dict['size'],json_dict['object'],json_dict['imb_code'],\
                 json_dict['priority'],json_dict['mail_sort'],json_dict['mail_type'],json_dict['press_proof'],json_dict['file_created_at'])
    mycursor.execute(sql)
    mydb.commit()
    print(mycursor.rowcount, "record inserted")

#Creates a directory in the same folder as this project which is used to store the PDF files if one does not already exist
def create_pdf_dir(base_path):
    if not os.path.exists(pdf_dir_path):
        print("Creating folder for PDF's")
        os.mkdir(pdf_dir_path)

#Gets the path for the directory full of .json files from the user.  If not a valid path it loops.
def get_json_path():
    path = input("Please enter the path of the directory you wish to track: \n")
    while not os.path.isdir(path):
        path = input("I could not find that directory, please try again\n")
    return path

#determines if the .json file is valid using the json.loads() function.
def is_valid_json_format(file):
    try:
        json_data = json.loads(file)
        return True
    except ValueError as e:
        return False

#Checks the status code of the page the url points to.  This is not perfect as non-pdf pages can return a positive status code, but it at least doesn't try to download from pages that don't exist
def is_valid_pdf_url(pdf_url):
    try:
        r = requests.get(pdf_url)
        return True
    except requests.exceptions.ConnectionError as e:
        return False

#Downloads the PDF (pretty self explanatory)
def download_pdf(pdf_url, pdf_id):
    pdf_file = requests.get(pdf_url)
    open(os.path.join(pdf_dir_path, pdf_id),'wb').write(pdf_file.content)
    

#database setup information.
mydb = mysql.connector.connect(
    host = 'your_hostname',
    user = 'your_username',
    password = 'your_password',
    database = 'your_database'
)
mycursor = mydb.cursor()

#Initialize variables
pdf_count = 0
pdf_dir_path = os.path.join(os.getcwd(), "press_proofs")
err_file_path = os.path.join(os.getcwd(), "error_log.txt")
already_submitted_files = {}
usr_input_path = get_json_path()
create_pdf_dir(pdf_dir_path)
num_files_in_json_dir = len([name for name in os.listdir(usr_input_path)])


#This first block of code is for dealing with files which are already inside of the json directory when the program initializes
for filename in os.listdir(usr_input_path):
    already_submitted_files[filename] = True 
    if filename.endswith(".json"):
        f = open(os.path.join(usr_input_path, filename),'r')
        file_data = f.read()
        if is_valid_json_format(file_data):
            json_data = json.loads(file_data)
            insert_in_database(json_data,mycursor,mydb)
            if is_valid_pdf_url(json_data["press_proof"]):
                download_pdf(json_data["press_proof"], json_data['id'])#download PDF
            else:
                print(filename + " does not have a valid PDF url")
                err_f = open(err_file_path, 'a')
                current_time = datetime.now().strftime("%H:%M:%S")
                err_f.write(current_time + ":  " + filename + " does not have a valid PDF url\n")
                err_f.close()
        else:
            print(filename + " is not in valid .json format")
            err_f = open(err_file_path, 'a')
            current_time = datetime.now().strftime("%H:%M:%S")
            err_f.write(current_time + ":  " + filename + " is not in valid .json format\n")
            err_f.close()
        f.close()
    else:
        print(filename + " does not have the proper .json file extension")
        err_f = open(err_file_path, 'a')
        current_time = datetime.now().strftime("%H:%M:%S")
        err_f.write(current_time + ":  " + filename + " does not have the proper .json file extension\n")


#This second block of code is for files which are added while this program is running
while True:
    if num_files_in_json_dir != len([name for name in os.listdir(usr_input_path)]):
        for filename in os.listdir(usr_input_path): 
            if not filename in already_submitted_files:
                already_submitted_files[filename] = True
                if filename.endswith(".json"):
                    f = open(os.path.join(usr_input_path, filename),'r')
                    file_data = f.read()
                    if is_valid_json_format(file_data):
                        json_data = json.loads(file_data)
                        insert_in_database(json_data,mycursor,mydb)
                        if is_valid_pdf_url(json_data["press_proof"]):
                            download_pdf(json_data["press_proof"], json_data['id'])
                        else:
                            print(filename + " does not have a valid PDF url")
                            err_f = open(err_file_path, 'a')
                            current_time = datetime.now().strftime("%H:%M:%S")
                            err_f.write(current_time + ":  " + filename + " does not have a valid PDF url\n")
                            err_f.close()
                    else:
                        print(filename + " is not in valid .json format")
                        err_f = open(err_file_path, 'a')
                        current_time = datetime.now().strftime("%H:%M:%S")
                        err_f.write(current_time + ":  " + filename + " is not in valid .json format\n")
                        err_f.close()
                    f.close()
                else:
                    print(filename + " does not have the proper .json file extension")
                    err_f = open(err_file_path, 'a')
                    current_time = datetime.now().strftime("%H:%M:%S")
                    err_f.write(current_time + ":  " + filename + " does not have the proper .json file extension\n")
    time.sleep(20)  #Time.sleep is used to cut down on CPU overhead in between checking for new files in the .json directory.  Lower the number for more frequent checks, raise it for less CPU usage



#time complexity O(n)