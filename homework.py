import json
import os, os.path
from datetime import datetime
import requests
import time
import mysql.connector
import db_config
#Only need to connect if actually adding to server
mydb = mysql.connector.connect(
    host = db_config.host,
    user = db_config.user,
    password = db_config.password,
    database = db_config.database
)
mycursor = mydb.cursor()

#/home/clay/Programs/homework/json_files
pdf_count = 0
pdf_dir_path = os.path.join(os.getcwd(), "press_proofs")
err_file_path = os.path.join(os.getcwd(), "error_log.txt")
already_submitted_files = {}#dictionary to keep track of files already scanned.
#======Gets a valid path to the directory from the user======

def insert_in_database(json_dict, mycursor, mydb):
    #Well now i know, use '%s' for values which are strings and %s (without quotation marks) for integers.  (youve gotta be kidding me)  I'll double check this with a clean example because w3schools is showing something different.
    sql = "INSERT INTO metadata (id,size,object,imb_code,priority,mail_sort,mail_type,press_proof,file_created_at) "\
        "VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s')"\
             %(json_dict['id'],json_dict['size'],json_dict['object'],json_dict['imb_code'],\
                 json_dict['priority'],json_dict['mail_sort'],json_dict['mail_type'],json_dict['press_proof'],json_dict['file_created_at'])
             #Spent way too long trying to get string formatter %s to work.  Still not sure why it wouldn't.  Use this instead.
    print(sql)
    mycursor.execute(sql)
    mydb.commit()
    print("info inserted correctly")
    print(mycursor.rowcount, "record inserted")

def create_pdf_dir(base_path):
    if not os.path.exists(pdf_dir_path):
        os.mkdir(pdf_dir_path)

def get_json_path():
    path = input("Please enter the path of the directory you wish to track: \n")
    while not os.path.isdir(path):
        path = input("I could not find that directory, please try again\n")
    return path

def is_valid_json_format(file):
    try:
        json_data = json.loads(file)
        return True
    except ValueError as e:
        return False

def is_valid_pdf_url(pdf_url):
    r = requests.get(pdf_url)
    if r.status_code == requests.codes.ok:
        return True
    else:
        return False

def download_pdf(pdf_url, pdf_id):
    pdf_file = requests.get(pdf_url)
    open(os.path.join(pdf_dir_path, pdf_id),'wb').write(pdf_file.content)


"""
This first block of code is for dealing with files which are already
inside of the json directory when the program initializes
"""

usr_input_path = get_json_path()
create_pdf_dir(pdf_dir_path)
num_files_in_json_dir = len([name for name in os.listdir(usr_input_path)])
for filename in os.listdir(usr_input_path):
    already_submitted_files[filename] = True 
    if filename.endswith(".json"):
        f = open(os.path.join(usr_input_path, filename),'r')
        file_data = f.read()
        if is_valid_json_format(file_data):
            json_data = json.loads(file_data)
            print(filename + " is in a valid .json format")
            #Put info into in database
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

"""
This second block of code is for files which are added while this program is running
"""

print("Number of files is " + str(num_files_in_json_dir))
while True: #Maybe use watchdog?  Maybe use threading (Check bookmark blog)
    if num_files_in_json_dir != len([name for name in os.listdir(usr_input_path)]): #maybe change != to >
        for filename in os.listdir(usr_input_path): 
            if not filename in already_submitted_files: #Look into making this faster.  Might be able to do a lookup and see if it return null?  Otherwise might as well just use an array (looked into it, may have broke it) Might also be worth looking into querying the database to see if the value already exists.  Not sure about time complexity of that though
                already_submitted_files[filename] = True
                if filename.endswith(".json"):
                    f = open(os.path.join(usr_input_path, filename),'r')
                    file_data = f.read()
                    if is_valid_json_format(file_data):
                        json_data = json.loads(file_data)
                        print(filename + " is in a valid .json format")
                        #Put Info into database
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
    time.sleep(20)  #This is to avoid too much CPU overhead, but its still just a temporary solution.













#TODO
#Make sure your code is protected from sql injection?  (Maybe since JSON is likey user created?)
#Probably make the database relational for nested .json objects
#Change the database to a SQL database
#Test this code on a windows machine.  There might be an unexpected area where my paths don't work as expected (Thanks to windows dang backslashes!)
#Make the event listener for a change in number of files more CPU efficient.  Python has a "Watchdog" class which might be worth looking into, as well as threading (Check your bookmarks)
#Make a seperate file holding information about which files have already been scanned in, that way if you close and restart the program it doesn't 
#   auto push already uploaded files to the database
#Check with Andrew and see if I should make each ID unique (Right now it will take any ID to the database and not treat it as a unique identifier)





#toDONE
#Add a folder to my gitignore which contains sensitive database information
#Make the program more modular.  See what sections can be their own functions, its too garbled right now.
#actually upload the JSON objects to a database.  I'm still not sure if i should use noSQL or SQL databases though. (I ended up using MongoDB Atlas because its free and I am more familiar with it)
#Get the directory to track from the usr
#scan and upload all files already existing in the json_directory to the database
#Save all existing json files "press_proof" PDF to a folder
#monitor the directory for any changes (Sort of done, not great but right now im using "while with sleep" as a temp fix)
#if any changes are made to the directory add all new files to the database.  (Should i remove entries that are removed from the directory?)
#Add any new "press_proof" PDF's to a folder
#Add some lines of code to create directories and files if they don't already exist, and to keep them if they already do. (Such as the PDF directory and the err_log file.)

#Notes
"""
Threading wont work as im not waiting for a calculation to finish, i'm waiting for a change to be made to a directory
I think this could be done with the 'watchdog' python module, but I believe that only works on linux.  I might need to make this script OS specific.
"""