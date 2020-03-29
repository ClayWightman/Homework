import json
import os, os.path
from datetime import datetime
import requests
import time
#/home/clay/Programs/homework/json_files
pdf_count = 0
pdf_dir_path = os.path.join(os.getcwd(), "press_proofs")
err_file_path = os.path.join(os.getcwd(), "error_log.txt")
already_submitted_files = {}#directory to keep track of files already scanned.
#======Gets a valid path to the directory from the user======
usr_input_path = input("Please enter the path of the directory you wish to track:\n")
while not os.path.isdir(usr_input_path):
    usr_input_path = input("I could not find that directory, please try again")
num_files_in_json_dir = len([name for name in os.listdir(usr_input_path)])
#The initial "dealing with" of the files in the directory when it is linked
for filename in os.listdir(usr_input_path):
    already_submitted_files[filename] = True 
    if filename.endswith(".json"):
        f = open(os.path.join(usr_input_path, filename),'r')
        json_from_file = f.read()
#======Try except block is used to check if the json formatting is valid======
        try:
            json_in_python = json.loads(json_from_file) 
            print(filename + " is a valid .json file")
            pdf_url = json_in_python["press_proof"]
            pdf_file = requests.get(pdf_url)
            open(os.path.join(pdf_dir_path, "pdf" + str(pdf_count)),'wb').write(pdf_file.content)
            pdf_count += 1
            #TODO: upload json_object to database
        except ValueError as e:
            print()
            print(filename + " is not in valid .json format")
            err_f = open(err_file_path, 'a')
            current_time = datetime.now().strftime("%H:%M:%S")
            err_f.write(current_time + ":  " +filename + " is not in valid .json format")
            err_f.close()
        f.close()
    else:
        print(filename + " does not have the proper .json file extension")
        err_f = open(err_file_path, 'a')
        current_time = datetime.now().strftime("%H:%M:%S")
        err_f.write(current_time + ":  " + filename + " does not have the proper .json file extension")


print("Number of files is " + str(num_files_in_json_dir))
while true: #Maybe use watchdog?  Maybe use threading (Check bookmark blog)
    if num_files_in_json_dir != len([name for name in os.listdir(usr_input_path)]):
        for filename in os.listdir(usr_input_path): 
            if not already_submitted_files[filename]: #This might give an error since i'm not sure what it gives if the key doesn't exist
                already_submitted_files[filename] = True
                if filename.endswith(".json"):
                    f = open(os.path.join(usr_input_path, filename),'r')
                    json_from_file = f.read()

                    try:
                        json_in_python = json.loads(json_from_file)
                        print(filename + " is a valid .json file")
                        pdf_url = json_in_python["press_proof"]
                        pdf_file = requests.get(pdf_url) #Might need an if for this and above code if PDF file = null

                        open(os.path.join(pdf_dir_path, "pdf" + str(pdf_count)),'wb').write(pdf_file.content)
                        pdf_count += 1
                        #TODO: upload json_object to database
                    except ValueError as e:
                        print()
                        print(filename + " is not in valid .json format")
                        err_f= open(err_file_path, 'a')
                        current_time = datetime.now().strftime("%H:%M:%S")
                        err_f.write(current_time + ":  " + filename+" is not in valid .json format")
                        err_f.close()
                    f.close()
                else:
                    print(filename + " does not have the proper .json file extension")
                    err_f = open(err_file_path, 'a')
                    current_time = datetime.now().strftime("%H:%M:%S")
                    err_f.write(current_time + ":  " + filename + " does not have the proper .json file extension")
    time.sleep(20)  #This is to avoid too much CPU overhead, but its still just a temporary solution.













#TODO
#actually upload the JSON objects to a database.  I'm still not sure if i should use noSQL or SQL databases though.
#Make the event listener for a change in number of files more CPU efficient.  Python has a "Watchdog" class which might be worth looking into, as well as threading (Check your bookmarks)
#Make the program more modular.  See what sections can be their own functions, its to garbled right now.
#Make a seperate file holding information about which files have already been scanned in, that way if you close and restart the program it doesn't 
#   auto push already uploaded files to the database
#Add some lines of code to create directories and files if they don't already exist, and to keep them if they already do. (Such as the PDF directory and the err_log file.)



#toDONE
#Get the directory to track from the usr
#scan and upload all files already existing in the json_directory to the database
#Save all existing json files "press_proof" PDF to a folder
#monitor the directory for any changes (Sort of done, not great but right now im using "while with sleep" as a temp fix)
#if any changes are made to the directory add all new files to the database.  (Should i remove entries that are removed from the directory?)
#Add any new "press_proof" PDF's to a folder
