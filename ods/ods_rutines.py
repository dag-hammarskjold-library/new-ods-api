########################################################################
# imports
########################################################################

from datetime import datetime
import re
from pymongo import MongoClient
import requests
from decouple import config
import urllib3
import json
import requests
from dlx import DB
from ods.config_dlx import Config
from dlx.file import File, Identifier
from dlx.marc import BibSet, Query,Condition,AuthSet
import os
import platform
import base64
import time
from pathlib import Path

########################################################################
# setup urllib3
########################################################################

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

########################################################################
# List of languages definition
########################################################################

LANGUAGES=["AR","ZH","EN","FR","RU","ES","DE"]

########################################################################
# definition of the credentials of the ODS API
########################################################################

base_url = config("base_url")
username = config("username")
password = config("password")
client_id = config("client_id")
client_secret = config("client_secret")

########################################################################
# management of the JobNumber
########################################################################

client = MongoClient(config("CONN"))
my_database = client["undlFiles"] 

########################################################################
# function managing the creation of the logs depending of the context
########################################################################

def add_log(date_log:str,user_connected:str,action_log:str)-> int:
    
    try:
        
        # setup the database and the collection
        my_collection = my_database["ods_action_logs_collection"]

        # creation of the log object
        my_log = {
            "user": user_connected,
            "action": action_log,
            "date": date_log
        }
        
        # save the log in the database
        my_collection.insert_one(my_log)
        
        return 0
        
    except:

        return -1

########################################################################
# encode base64
########################################################################

def get_encode_base64()-> str:
  text=f"{username}:{password}:{client_id}:{client_secret}"
  # Encode the input text to base64
  encoded_bytes = base64.b64encode(text.encode('utf-8'))
  # Convert the bytes to a string
  encoded_string = encoded_bytes.decode('utf-8')
  return encoded_string


####################################################################################################################################        
# check if a docsymbol exists already
####################################################################################################################################        

def check_if_docsymbol_exists(my_docsymbol:str)-> bool:
  """
  The idea of this function is to check if one jobnumber exits already.
  Inorder to achieve this goal we will call the loading symbol route 
  to check if we have a match result not nul.
  """
  # init the variable
  find_occurence=False
  
  job_numbers=[]
  
  # display result
  if ods_get_loading_symbol(my_docsymbol)["body"]["meta"]["matches"]>0:
    find_occurence=True
    # retrieve job numbers as well
    job_numbers=ods_get_loading_symbol(my_docsymbol)["body"]["data"][0]["job_numbers"]

  # returning a tuple with the information required  
  return find_occurence,job_numbers

####################################################################################################################################        
# check if a job number exists already
####################################################################################################################################        

def check_if_job_number_exists(my_job_number:str):
  """
  The idea of this function is to check if one jobnumber exits already.
  Inorder to achieve this goal we will call the loading symbol route 
  to check if we have a match result not nul.
  """
  # init the variable
  find_occurence=False
  
  # display result
  if ods_get_loading_search(my_job_number)["body"]["meta"]["matches"]>0:
    find_occurence=True
  
  return find_occurence
  
####################################################################################################################################        
# create a job number using a batch
####################################################################################################################################        

def get_job_number(my_docsymbol:str,my_language:str)->dict:

  try:

    # get the collection
    my_collection = my_database["ods_jobnumber_collection"]
    
    # get the last value
    number_of_records=my_collection.estimated_document_count()

    # if the collection is empty        
    if number_of_records == 0:

      my_number=900000
      
      found_number=False
      jobnumber_to_insert=""
      
      # loop to check if the number exists
      while found_number==False:

        jobnumber_to_insert="NX" + str(my_number)
        result=check_if_job_number_exists(jobnumber_to_insert)
        if (result==False):
          found_number=True
        else:
          my_number=my_number+1
                    
      # the collection is empty
      data = {
          "created_date": datetime.now(), 
          "jobnumber_value":jobnumber_to_insert,
          "docsymbol": my_docsymbol,
          "language":my_language
      }

      # save the record in the database
      resultat=my_collection.insert_one(data)

      # return the jobnumber
      return data
    
    # if the collection is not empty     
    if number_of_records !=0:

      # get the job number of the last record
      last_record=my_collection.find().limit(1).sort([('$natural',-1)])
      
      # retrieve last_record_number value
      last_record_number=0 
      for doc in last_record:
          last_record_number=doc["jobnumber_value"]

      last_record =int(last_record_number[2:]) + 1
      found_number=False
      jobnumber_to_insert="NX" + str(last_record)
      
      # loop to check if the number exists
      while found_number==False:

        result= check_if_job_number_exists(jobnumber_to_insert)

        if result==False:
          found_number=True
        else:
          last_record=last_record+1
          jobnumber_to_insert="NX" + str(last_record)        
      
      data = {
          "created_date": datetime.now(), 
          "jobnumber_value":jobnumber_to_insert,
          "docsymbol": my_docsymbol,
          "language":my_language
      }
        
                    
      # save the log in the database
      my_collection.insert_one(data)
      return data
      
  except:
    
    result={
        "result":"NOK",
        "jobnumber":"",
        "id":""
    }

    return result

####################################################################################################################################                
#release job number not used
####################################################################################################################################        

def release_job_number(jobnumber:str):
  
  try:
    # get the collection
    my_collection = my_database["ods_jobnumber_collection"]

    record = {
        "jobnumber_value": jobnumber,
    }
    
    # delete the job number
    results=my_collection.delete_one(record)
    
    if (results.deleted_count >0 ):
    
      # send back a message
      return json.dumps({"message":"jobnumber released!!!"})
    
    else : 
      
      # send back a message
      return json.dumps({"message":"jobnumber not found in the database!!!"})      
      
  except:

    # send back a message
    return json.dumps({"message":"jobnumber not released!!!"})


########################################################################
# call the API for getting the Token every time : /api/auth/token
########################################################################

def get_token()->str:

  url = f"{base_url}api/auth/token?username={username}&password={password}&client_id={client_id}&client_secret={client_secret}"
  payload0 = {}
  headers0 = {
    'Authorization': f'Basic {get_encode_base64()}'
  }
  response = requests.request("GET", url, headers=headers0, data=payload0,verify=False)
  json_data = json.loads(response.text)
  return json_data["token"]

########################################################################
# call the API for loading the symbols : /api/loading/symbol
########################################################################

def ods_get_loading_symbol(my_param:str):

  # get the token
  my_token=get_token()
  
  # build the url
  url1=config("base_url") + "api/loading/symbol?s=" + my_param
  
  # build the payload
  payload={}
  
  # build the header
  headers = {
          "authorization":  "Access {}".format(my_token),
          }
  
  # get the response 
  response = requests.request("GET", url1, headers=headers, data=payload,verify=False)
  
  # return the response
  return response.json()

######################################################################################
# call the API for loading the symbols using search endpoint : /api/loading/search
######################################################################################

def ods_get_loading_search(my_param):

  # get the token
  my_token=get_token()
  
  # build the url
  url1=config("base_url") + "api/loading/search?k=" + my_param
  
  # build the payload
  payload={}
  
  # build the header
  headers = {
          "authorization":  "Access {}".format(my_token),
          }
  
  # get the response 
  response = requests.request("GET", url1, headers=headers, data=payload,verify=False)
  
  # return the response
  return response.json()

########################################################################
# Getting data from central database
########################################################################


def escape_characters(input_string, chars_to_escape):
  for char in chars_to_escape:
      input_string = input_string.replace(char, f'\\{char}')
  return input_string

def get_tcodes(subject):
  query = Query(
            Condition(
                tag='150',
                subfields={'a': re.compile(str(subject).upper())}
                )
          )

  authset = AuthSet.from_query(query, projection={'035':1,'150':1})

  for auth in authset:
      val_035a=auth.get_values('035','a')
      val_035a=''.join([str for str in val_035a if str[0] in {'T', 'P'}] )
  return val_035a

def get_data_from_cb(symbols):
  
  lst=[]
  try:
    DB.connect(Config.connect_string, database="undlFiles")
    symbol=escape_characters(symbols,"()")
    query = Query.from_string("symbol:/^"+symbol+"$/") 
    document_symbol=""
    distribution=""
    area="UNDOC"
    publication_date=""
    release_date=datetime.now().strftime('%d/%m/%y')
    sessions=""
    title_en=""
    agendas=""
    subjects=""
    tcodes=""

    for bib in BibSet.from_query(query):
        document_symbol=bib.get_values('191', 'a')
        distribution=bib.get_value('091', 'a')
        publication_date=bib.get_value('269','a')
        release_date=datetime.now().strftime('%d/%m/%y')
        sessions=' '.join(bib.get_values('191','c'))
        
        if publication_date !='':
          try:
            publication_date=datetime.strptime(publication_date, '%Y-%m-%d').strftime('%d/%m/%y')
          except:
            publication_date=datetime.strptime(publication_date[0:4], '%Y').strftime('%y')
        title_en=bib.get_value('245', 'a')+" "+bib.get_value('245', 'b')
        agendas=' '.join(bib.get_values('991','b'))
        tcodes=','.join([get_tcodes(subject) for subject in bib.get_values('650','a')])                         
        datamodel={"symbol":document_symbol[0],"distribution":distribution,"area": area, "publication_date":publication_date, 
                "release_date":release_date, "sessions":sessions, "title":title_en, "agendas":agendas, "subjects":subjects, "tcodes":tcodes}
        lst.append(datamodel)

    return lst
  
  except:

    return lst
########################################################################
# create / update metadata  
########################################################################

def ods_create_update_metadata(my_symbol):
  
  # a refactoring should be done to avoid DRY
  
  # call the api to know if this symbol exists already (1 if the symbol exists 0 otherwise)
  my_matche=ods_get_loading_symbol(my_symbol)["body"]["meta"]["matches"]
  
  if ods_get_loading_symbol(my_symbol)["body"]["data"]:
    my_job_numbers=ods_get_loading_symbol(my_symbol)["body"]["data"][0]["job_numbers"]

  if my_matche==0: # the symbol is new we can create 
    # get the data from central DB
    datamodel=get_data_from_cb(my_symbol)
    
    if len(datamodel)>0:
      # assign the values from central database to local variables
      my_symbol=datamodel[0]["symbol"]
      my_distribution=datamodel[0]["distribution"]
      my_area=datamodel[0]["area"]
      my_publication_date= datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
      my_release_date= datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
      my_sessions=datamodel[0]["sessions"]
      my_title=datamodel[0]["title"]
      my_agendas=datamodel[0]["agendas"]
      my_subjects=datamodel[0]["subjects"]
      my_tcodes=[]
      my_tcodes.append(datamodel[0]["tcodes"])
      
      # get the token
      my_token=get_token()

      # definition of the header
      headers = {
              "authorization":  "Access {}".format(my_token),
              }
          
      # build the url
      url = config("base_url") + "api/loading/symbol"

      # retrieving the data and assignment
      symbols=  [f"{my_symbol}","",""]   
      sessions= [f"{my_sessions}","",""]
      agendas=  [f"{my_agendas}","",""]   

      
      # setting the jubnumbers for each language dynamycally
      jobnumbers=[]
      counter=0
      for counter in range(7):
        recup=get_job_number(my_symbol,LANGUAGES[counter])
        jobnumbers.append(recup["jobnumber_value"])
      
      print(jobnumbers)

      # define payload
      payload ={
                "symbols":symbols,
                "sessions":sessions,
                "agendas": agendas,
                "area": my_area, 
                "distribution":my_distribution, 
                "tcodes": my_tcodes,
                "publicationDate": my_publication_date,
                "perLanguage": {
                  LANGUAGES[0]: { 
                          "jobNumber": jobnumbers[0],
                          "releaseDate": my_release_date, 
                          "title": "",
                          "fullText":""
                          },
                  LANGUAGES[1]: { 
                          "jobNumber": jobnumbers[1],
                          "releaseDate": my_release_date, 
                          "title": "" ,
                          "fullText":""
                          },  
                  LANGUAGES[2]: { 
                          "jobNumber": jobnumbers[2],
                          "releaseDate":my_release_date, 
                          "title":my_title,
                          "fullText":""
                          },  
                  LANGUAGES[3]: { 
                          "jobNumber": jobnumbers[3],
                          "releaseDate":my_release_date, 
                          "title": "" ,
                          "fullText":""
                          },  
                  LANGUAGES[4]: { 
                          "jobNumber": jobnumbers[4],
                          "releaseDate":my_release_date, 
                          "title": "" ,
                          "fullText":""
                          },  
                  LANGUAGES[5]: { 
                          "jobNumber": jobnumbers[5],
                          "releaseDate":my_release_date, 
                          "title": "" ,
                          "fullText":""
                          },
                  LANGUAGES[6]: { 
                          "jobNumber": jobnumbers[6],
                          "releaseDate":my_release_date,
                          "title": "" ,
                          "fullText":""
                          }    
                    }
                }
        
      # define file
      files = {
        'data': (None,json.dumps(payload),'application/json'),
      }

      res = requests.post(url, headers=headers,files=files,verify=False)
      data=res.json()
      data["status"]=1
      data["update"]=False 
      return data
        
    else :
      result={}
      result["status"]=0
      result["update"]=False
      return result

  else : # the symbol is not new it's an update
    # get the data from central DB
    datamodel=get_data_from_cb(my_symbol)
    
    if len(datamodel)>0:
      # assign the values from central database to local variables
      my_symbol=datamodel[0]["symbol"]
      my_distribution=datamodel[0]["distribution"]
      my_area=datamodel[0]["area"]
      my_publication_date= datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
      my_release_date= datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
      my_sessions=datamodel[0]["sessions"]
      my_title=datamodel[0]["title"]
      my_agendas=datamodel[0]["agendas"]
      my_subjects=datamodel[0]["subjects"]
      my_tcodes=[]
      my_tcodes.append(datamodel[0]["tcodes"])
      
      # get the token
      my_token=get_token()

      # definition of the header
      headers = {
              "authorization":  "Access {}".format(my_token),
              }
          
      # build the url
      url = config("base_url") + "api/loading/symbol"

      # retrieving the data and assignment
      symbols=  [f"{my_symbol}","",""]   
      sessions= [f"{my_sessions}","",""]
      agendas=  [f"{my_agendas}","",""]   
      
      
      # retrieving jobnumber for the ones existing and if not exist the system will create it
      jobnumbers=check_if_docsymbol_exists(my_symbol)[1]
      
      # generate values for jobnumbers missing if it's the case
      my_final_job_numbers=["xxx","xxx","xxx","xxx","xxx","xxx","xxx"]
     
      # copy the jobnumbers list in my_final_job_numbers
      for i in range(len(jobnumbers)):
        my_final_job_numbers[i]=jobnumbers[i]
     
      # check missing values and add missing values generating job numbers
      my_language=0
      
      for i in range(len(my_final_job_numbers)):
        if my_final_job_numbers[i]=="":

          if i==0:
            recup=get_job_number(my_symbol,"AR")
            my_final_job_numbers[i]=recup["jobnumber_value"]
          if i==1:
            recup=get_job_number(my_symbol,"ZH")
            my_final_job_numbers[i]=recup["jobnumber_value"]
          if i==2:
            recup=get_job_number(my_symbol,"EN")
            my_final_job_numbers[i]=recup["jobnumber_value"]
          if i==3:
            recup=get_job_number(my_symbol,"FR")
            my_final_job_numbers[i]=recup["jobnumber_value"]
          if i==4:
            recup=get_job_number(my_symbol,"RU")
            my_final_job_numbers[i]=recup["jobnumber_value"]
          if i==5:
            recup=get_job_number(my_symbol,"ES")
            my_final_job_numbers[i]=recup["jobnumber_value"]                     
          if i==6:
            recup=get_job_number(my_symbol,"DE")
            my_final_job_numbers[i]=recup["jobnumber_value"]  
        my_language+=1
        
      # define payload
      payload ={
                "symbols":symbols,
                "sessions":sessions,
                "agendas": agendas,
                "area": my_area, 
                "distribution":my_distribution, 
                "tcodes": my_tcodes,
                "publicationDate": my_publication_date,
                "perLanguage": {
                  LANGUAGES[0]: { 
                          "jobNumber": my_final_job_numbers[0],
                          "releaseDate": my_release_date, 
                          "title": my_title,
                          "fullText":""
                          },
                  LANGUAGES[1]: { 
                          "jobNumber": my_final_job_numbers[1],
                          "releaseDate": my_release_date, 
                          "title": "" ,
                          "fullText":""
                          },  
                  LANGUAGES[2]: { 
                          "jobNumber": my_final_job_numbers[2],
                          "releaseDate":my_release_date, 
                          "title":""  ,
                          "fullText":""
                          },  
                  LANGUAGES[3]: { 
                          "jobNumber": my_final_job_numbers[3],
                          "releaseDate":my_release_date, 
                          "title": "" ,
                          "fullText":""
                          },  
                  LANGUAGES[4]: { 
                          "jobNumber": my_final_job_numbers[4],
                          "releaseDate":my_release_date, 
                          "title": "" ,
                          "fullText":""
                          },  
                  LANGUAGES[5]: { 
                          "jobNumber": my_final_job_numbers[5],
                          "releaseDate":my_release_date, 
                          "title": "" ,
                          "fullText":""
                          },
                  LANGUAGES[6]: { 
                          "jobNumber": my_final_job_numbers[6],
                          "releaseDate":my_release_date,
                          "title": "" ,
                          "fullText":""
                          }    
                    }
                }
        
      # define file
      files = {
        'data': (None,json.dumps(payload),'application/json'),
      }

      res = requests.post(url, headers=headers,files=files,verify=False)
      data=res.json()
      data["status"]=2 #update
      data["update"]=True #update
      return data
        
    else :
      result={}
      result["status"]=0
      result["update"]=False
      return result


########################################################################
# Send file to ODS
########################################################################

def ods_file_upload_simple_file(my_symbol,my_distribution,my_jobnumber,my_language,my_path):
  
  # get the token
  my_token=get_token()


  # definition of the header
  headers = {
          "authorization":  "Access {}".format(my_token),
          }

  # creation the data
  payload = {
        "symbol":my_symbol,
        "area": "UNDOC", 
        "distribution": my_distribution, 
        "perLanguage": {f"{my_language}": { "jobNumber": f"{my_jobnumber}"} }
      }
  # creation of the file dict
  files={
    'data': (None, json.dumps(payload), 'application/json'),
    f'{my_jobnumber}.pdf':(f'{my_jobnumber}.pdf',open(my_path,'rb'),'application/octet-stream') 
  }

  # build the url
  url=config("base_url") + "api/loading/file"

  # building the request

  response = requests.post(url,headers=headers,files=files,verify=False)
 
  return response.json()


def get_data_from_undl(docsymbol):
  
  DB.connect(Config.connect_string, database="undlFiles")
  docsymbol_formatted=docsymbol.replace("/","\/")
  query = Query.from_string(f"191__a:/^"+ docsymbol_formatted +"$/") 
  lst=[]
  document_symbol=""
  distribution=""
  area="UNDOC"
  publication_date=""
  release_date=datetime.now().strftime('%d/%m/%y')
  sessions=""
  title_en=""
  agendas=""
  subjects=""

  for bib in BibSet.from_query(query):
    if docsymbol==bib.get_value('191', 'a'):
      document_symbol=bib.get_value('191', 'a')
      distribution=bib.get_value('091', 'a')
      publication_date=bib.get_value('269','a')
      sessions=' '.join(bib.get_values('191','c'))
      title_en=bib.get_value('245', 'a')+" "+bib.get_value('245', 'b')
      agendas=' '.join(bib.get_values('991','b'))
      subjects=','.join(bib.get_values('650','a'))
      datamodel=(document_symbol, distribution, area, publication_date, release_date, sessions, title_en, agendas, subjects)
      lst.append(datamodel)

  return lst

########################################################################
####### Function to download file ######################################
########################################################################

def download_file_and_send_to_ods(docsymbol):
    
  # define the report list
  report=[]
    
  # call the api to know if this symbol exists already (1 if the symbol exists 0 otherwise)
  my_matche=ods_get_loading_symbol(docsymbol)["body"]["meta"]["matches"]
  
  if my_matche!=0: # the symbol is new we can create 
    
    # connect to the database
    DB.connect(Config.connect_string, database="undlFiles")

    # query the database according to the document symbol
    query = Query.from_string(f"191__a:/^{docsymbol}$/")
    
    # store  not used jobnumbers
    used_jobnumbers=[]
    
    # download the files in all languages
    for bib in BibSet.from_query(query):
      my_jobnumber=""
      document_symbol=bib.get_value('191', 'a')
      
      # fixing some issues with the regex returning values 
      if len(document_symbol)==len(docsymbol):
        distribution=bib.get_value('091', 'a')
        for language in LANGUAGES : 
          
          filename = document_symbol.replace("/", "_") + f"-{language}.pdf"  
          
          # setting a default for *nix systems should be safer than testing explicitly
          # for the platform name
          path="./ods/tmp"
          
          if platform.os.name in ['windows','nt'] :
            path='ods\\temp'
        
          #if platform.os.name == 'linux':
          #  path='ods/temp'
            
          
          filepath = Path(os.path.join(path, filename))
          filepath.parent.mkdir(parents=True, exist_ok=True)
          
          # getting the file
          f = File.latest_by_identifier_language(Identifier('symbol', document_symbol), f'{language}')

          if f is not None:
            uri = f.uri
            response = requests.get("https://"+uri, stream=True)

            # download the file on the temp folder
            with open(filepath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)

          # write the report and send the file to ODS
          recup1=""

          if f is not None:
            result=ods_get_loading_symbol(docsymbol)
            recup_job_numbers=result["body"]["data"][0]["job_numbers"]
                    
            if language=="AR":
              my_jobnumber=recup_job_numbers[0]
              recup1=ods_file_upload_simple_file(docsymbol,distribution,recup_job_numbers[0],language,filepath)
              
            if language=="ZH":
              my_jobnumber=recup_job_numbers[1]
              recup1=ods_file_upload_simple_file(docsymbol,distribution,recup_job_numbers[1],language,filepath)
              
            if language=="EN":
              my_jobnumber=recup_job_numbers[2]
              recup1=ods_file_upload_simple_file(docsymbol,distribution,recup_job_numbers[2],language,filepath)
              
            if language=="FR":
              my_jobnumber=recup_job_numbers[3]
              recup1=ods_file_upload_simple_file(docsymbol,distribution,recup_job_numbers[3],language,filepath)
              
            if language=="RU":
              my_jobnumber=recup_job_numbers[4]
              recup1=ods_file_upload_simple_file(docsymbol,distribution,recup_job_numbers[4],language,filepath)
              
            if language=="ES":
              my_jobnumber=recup_job_numbers[5]
              recup1=ods_file_upload_simple_file(docsymbol,distribution,recup_job_numbers[5],language,filepath)    
              
            if language=="DE":
              my_jobnumber=recup_job_numbers[6]
              recup1=ods_file_upload_simple_file(docsymbol,distribution,recup_job_numbers[6],language,filepath)    

            if recup1["status"]==1:
              used_jobnumbers.append(my_jobnumber)    
              report.append({
                              "filename":filename,
                              "docsymbol":docsymbol,
                              "language":language,
                              "jobnumber":my_jobnumber,
                              "result":"downloaded and sent successfully!!!"
                              })
            else:
              report.append({
                            "filename":filename,
                            "docsymbol":docsymbol,
                            "language":language,
                            "jobnumber":"",
                            "result":"not sent to ODS!!!"
                          })
          
          else :
              report.append({
                          "filename":filename,
                          "docsymbol":docsymbol,
                          "language":language,
                          "jobnumber":"",
                          "result":"file not downloaded!!!"
                          })
          time.sleep(2)

    # release not used jobnumbers
    not_used_jobnumbers=list(set(recup_job_numbers) - set(used_jobnumbers))
    for jb in not_used_jobnumbers:
      release_job_number(jb)

    # clean temp folder
    files = os.listdir(path)
    
    # Iterate over each file and delete it
    for file in files:
        file_path = os.path.join(path, file)
        os.remove(file_path)
        
  else :

    report.append({
                "filename":"",
                "docsymbol":docsymbol,
                "language":"",
                "jobnumber":"",
                "result":"docsymbol does not exist!!!"
                })

  # return the report
  return report

# print(check_if_docsymbol_exists("A/RES/70/11"))
# ods_create_update_metadata("A/CONF.94/9")
# get_data_from_cb("A/CONF.94/9")
# get_job_number("A/CONF.94/9")