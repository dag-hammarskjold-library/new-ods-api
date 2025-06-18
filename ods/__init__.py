##############################################################################################
##########  IMPORTS
##############################################################################################

from werkzeug.security import check_password_hash, generate_password_hash
import json
import datetime
import os
import requests
import ods.ods_rutines
from flask import Flask, jsonify,render_template,request,redirect,session, url_for
from decouple import config
from pymongo import MongoClient
from bson import json_util

return_data=""

########################################################################
# definition of the credentials of the ODS API
########################################################################

base_url = config("BASE_URL")
username = config("USERNAME")
password = config("PASSWORD")
client_id = config("CLIENT_ID")
client_secret = config("CLIENT_SECRET")
database_conn=config("CONN")


##############################################################################################
##########  APP INIZIALISATION
##############################################################################################

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='h@454325hdhdbhdb'
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    ############################################################################
    # LOGIN
    ############################################################################
    
    @app.route('/',methods=["GET","POST"])
    def login():
        
        error=None
        
        # check the method called
        if request.method=="GET":

            # just render the login
            return render_template("login.html")
        
        if request.method=="POST":
            
            # check if it's the special user
            if request.form.get("email")==config("DEFAULT_USERNAME"):

                if request.form.get("password")==config("DEFAULT_PASSWORD"):
                    
                    # special user
                    ods.ods_rutines.add_log(datetime.datetime.now(tz=datetime.timezone.utc),config("DEFAULT_USERNAME"),"Connected to the system!!!")
                    
                    # add the username to the session
                    
                    session['username'] = config("DEFAULT_USERNAME")
                    
                    # add the prefix to the session
                    session["prefix_site"]="NX"
                    
                    # management of the access to the tabs
                    session["show_display"]=True
                    session["show_create_update"]=True
                    session["show_send_file"]=True
                    session["show_jobnumbers_management"]=True
                    session["show_parameters"]=True
                    

                    return redirect(url_for("index_vue"))

            
            # check if the user exists in the database with the good password
            client = MongoClient(database_conn)
            my_database = client["odsActions"] 
            my_collection = my_database["ods_actions_users_collection"]


            user = {
                "email": request.form.get("email"),
            }

            results= list(my_collection.find(user))
            #print(results)
           
            find_record=False

            if (len(results)==0):
                # user not found
                error="User not found in the database!!!"
                return render_template("login.html",error=error)
            else :
                        
                for result in results:
                    if check_password_hash(result["password"],request.form.get("password")):
                
                        # user found
                        ods.ods_rutines.add_log(datetime.datetime.now(tz=datetime.timezone.utc),request.form.get("email"),"Connected to the system!!!")
                        #session.clear()
                        print(f'session b4 login {session}')
                        # add the username to the session
                        session['username'] = result["email"]
                        
                        # add the prefix to the session
                        session["prefix_site"]=get_prefix_from_site(result["site"])
                        
                         # management of the access to the tabs
                        session["show_display"]=result["show_display"]
                        session["show_create_update"]=result["show_create_update"]
                        session["show_send_file"]=result["show_send_file"]
                        session["show_jobnumbers_management"]=result["show_jobnumbers_management"]
                        session["show_parameters"]=result["show_parameters"]
                        
                        find_record=True
                        print(f'session after login {session}')
                        print(f"username is {session['username']}")
                        if session['username']!="":
                            return redirect(url_for("index_vue"))
                        else:
                            return redirect(url_for("login"))
                        
                if find_record==False:
                    
                    # user not found
                    error="User not found in the database!!!"
                    return render_template("login.html",error=error)

    ############################################################################
    # MAIN ROUTE
    ############################################################################
    
    @app.route('/index')
    def index_vue():
        if session:
            if session['username']!="":

                session_username=session['username']
                session_show_display=session["show_display"]
                session_show_create_update=session["show_create_update"]
                session_show_send_file=session["show_send_file"]
                session_show_jobnumbers_management=session["show_jobnumbers_management"]
                session_show_parameters=session["show_parameters"]

                return render_template('index_simple.html',
                                       user=session_username,
                                       session_username=session_username,
                                       session_show_display=session_show_display,
                                       session_show_create_update=session_show_create_update,
                                       session_show_send_file=session_show_send_file,
                                       session_show_jobnumbers_management=session_show_jobnumbers_management,
                                       session_show_parameters=session_show_parameters
                                       )
        else:
            return  redirect(url_for("login"))
    
    ############################################################################
    # LIST SITE ROUTE
    ############################################################################
    
    @app.route("/list_sites",methods=['GET'])
    def list_sites():

        client = MongoClient(database_conn)
        my_database = client["odsActions"] 
        my_collection = my_database["ods_actions_sites_collection"]
        
        # get all the logs
        my_sites=my_collection.find(sort=[( "creation_date", -1 )])
            
        # just render the logs
        return json.loads(json_util.dumps(my_sites))    
        
    ############################################################################
    # CREATE SITE ROUTE
    ############################################################################
    
    @app.route("/add_site", methods=["POST"])
    def add_site():
    
        try :    
            client = MongoClient(database_conn)
            my_database = client["odsActions"] 
            my_collection = my_database["ods_actions_sites_collection"]

            site = {
                "code_site":request.form.get("code_site"),
                "Label_site":request.form.get("label_site"),
                "prefix_site":request.form.get("prefix_site"),
                "creation_date": datetime.datetime.now(tz=datetime.timezone.utc)
            }
            
            # save the site in the database
            my_site=my_collection.insert_one(site)
            
            # create log
            ods.ods_rutines.add_log(datetime.datetime.now(tz=datetime.timezone.utc),session['username'],"Site " + str(my_site.inserted_id) + "  added to the system!!!")
            
            if (my_site.inserted_id):
                result={
                    "status" : "OK",
                    "message" : "Site created!!!"
                }
                return jsonify(result)

            else :
                result={
                    "status" : "NOK",
                    "message" : "Site not created!!!"
                }
                return jsonify(result)
            
        except:
            result={
                "status" : "NOK",
                "message" : "Site not created!!!"
            }
            return jsonify(result)
            
    ############################################################################
    # CREATE USER ROUTE
    ############################################################################
    
    @app.route("/add_user", methods=["POST"])
    def add_user():
    
        try :    
            client = MongoClient(database_conn)
            my_database = client["odsActions"] 
            my_collection = my_database["ods_actions_users_collection"]

            # converting password to array of bytes 
            pwd = generate_password_hash(request.form.get("password"))

            user = {
                "site":request.form.get("site"),
                "email": request.form.get("email"),
                "password": pwd,
                "show_display": request.form.get("show_display"),
                "show_create_update": request.form.get("show_create_update"),
                "show_send_file": request.form.get("show_send_file"),
                "show_jobnumbers_management": request.form.get("show_jobnumbers_management"),
                "show_parameters": request.form.get("show_parameters"),
                "creation_date": datetime.datetime.now(tz=datetime.timezone.utc)
            }
            
            # save the user in the database
            my_user=my_collection.insert_one(user)
            
            # create log
            ods.ods_rutines.add_log(datetime.datetime.now(tz=datetime.timezone.utc),session['username'],"User " + str(my_user.inserted_id) + "  added to the system!!!")
            
            if (my_user.inserted_id):
                result={
                    "status" : "OK",
                    "message" : "User created!!!"
                }
                return jsonify(result)

            else :
                result={
                    "status" : "NOK",
                    "message" : "User not created!!!"
                }
                return jsonify(result)
            
        except:
            result={
                "status" : "NOK",
                "message" : "User not created!!!"
            }
            return jsonify(result)


    ############################################################################
    # DISPLAY METADATA FROM ODS
    ############################################################################

    @app.route('/loading_symbol',methods=['POST'])
    def loading_symbol():
        try:
            # Check if user is authenticated
            if 'username' not in session:
                print("User not authenticated in loading_symbol")
                return jsonify({"error": "User not authenticated"}), 401
            
            print(f"Loading symbol for user: {session['username']}")
            
            if 'docsymbols' not in request.form:
                print("No docsymbols in request form")
                return jsonify({"error": "No docsymbols provided"}), 400
            
            docsymbols = request.form["docsymbols"].split("\r\n")
            print(f"Processing docsymbols: {docsymbols}")
            
            final=[]
            
            for docsymbol in docsymbols:
                try:
                    print(f"Processing docsymbol: {docsymbol}")
                    result=ods.ods_rutines.ods_get_loading_symbol(docsymbol)
                    try:
                        tcodes=result["body"]["data"][0]["tcodes"]
                        #print(tcodes)
                        subjects=[ods.ods_rutines.get_subject(tcode) for tcode in tcodes]
                        result["body"]["data"][0]["subjects"]=subjects
                    except Exception as e:
                        print(f"Error processing tcodes for {docsymbol}: {e}")
                        pass
                    result["docsymbol"]=docsymbol
                    final.append(result)
                except Exception as e:
                    print(f"Error processing docsymbol {docsymbol}: {e}")
                    # Add error result for this docsymbol
                    final.append({
                        "docsymbol": docsymbol,
                        "body": {
                            "data": [{
                                "symbol": docsymbol,
                                "agendas": "Error processing",
                                "sessions": "Error processing",
                                "distribution": "Error processing",
                                "area": "Error processing",
                                "subjects": "Error processing",
                                "job_numbers": "Error processing",
                                "title_en": "Error processing",
                                "publication_date": "Error processing",
                                "agenpublication_datedas": "Error processing",
                                "release_dates": "Error processing"
                            }]
                        }
                    })
            
            print(f"Final result count: {len(final)}")
            
            # create log
            try:
                ods.ods_rutines.add_log(datetime.datetime.now(tz=datetime.timezone.utc),session['username'],"ODS loading symbol endpoint called from the system!!!")
            except Exception as e:
                print(f"Error adding log: {e}")
            
            # create analytics
            try:
                ods.ods_rutines.add_analytics(datetime.datetime.now(tz=datetime.timezone.utc),session['username'],"loading_symbol_endpoint",final)
            except Exception as e:
                print(f"Error adding analytics: {e}")
            
            return jsonify(final)
        except Exception as e:
            print(f"Error in loading_symbol: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": "Internal server error", "details": str(e)}), 500
        
    @app.route("/get_sites",methods=['GET'])
    def get_sites():

        client = MongoClient(database_conn)
        my_database = client["odsActions"] 
        my_collection = my_database["ods_actions_sites_collection"]
        
        # get all the logs
        my_sites=my_collection.find(sort=[( "creation_date", -1 )])
           
        # just render the logs
        return json.loads(json_util.dumps(my_sites))        
        
    ####################################################################################################################################        
    # return prefix from the database
    ####################################################################################################################################        
    def get_prefix_from_site(my_site:str)->str:

        try:
            client = MongoClient(database_conn)
            my_database = client["odsActions"] 
            my_collection = my_database["ods_actions_sites_collection"]
            site = {
                "code_site": my_site,
            }

            results= list(my_collection.find(site))

            return results[0]["prefix_site"]
        
        except:

            return ""    
    ############################################################################
    # CREATE / UPDATE METADATA
    ############################################################################
    
    @app.route('/create_metadata_ods',methods=['POST'])
    def ods_create_update_metadata():

        docsymbols = request.form["docsymbols1"].replace("\r","").split("\n")
        data=[]
        prefix=session["prefix_site"]
        
        for docsymbol in docsymbols:
            result=ods.ods_rutines.ods_create_update_metadata(docsymbol,prefix)
            #print(result)
            text="-1 this is default value"
            if (result["status"]== 0 and result["update"]==False):
                text="Metadata not found in the Central DB/ME"
            if (result["status"]== -1 and result["update"]==False):
                text=result["message"]
            if (result["status"]== 1 and result["update"]==False) :
                text="Metadata created!!!"
            if (result["status"]== 2 and result["update"]==True) :
                text="Metadata updated!!!"
            if (result["status"]==3) :
                text="There is a duplicate symbol in ODS!!!"                
            summary={
                "docsymbol":docsymbol,
                "text":text
                }
            data.append(summary)
        # create log
        ods.ods_rutines.add_log(datetime.datetime.now(tz=datetime.timezone.utc),session['username'],"ODS creating/updating endpoint called from the system!!!")
        
        # create analytics
        ods.ods_rutines.add_analytics(datetime.datetime.now(tz=datetime.timezone.utc),session['username'],"creating_updating_endpoint",data)
        
        return data
    
    ############################################################################
    # SEND FILE TO ODS
    ############################################################################

    @app.route('/exporttoodswithfilebylanguages',methods=['POST'])
    def exporttoodswithfilebylanguages():
        # get the docsymbols
        data_send_multiple= request.form["docsymbols2"].replace("\r","").split("\n")
        # get the languages
        ar=request.form.get("ar")
        zh=request.form.get("zh")
        en=request.form.get("en")
        fr=request.form.get("fr")
        ru=request.form.get("ru")
        es=request.form.get("es")
        de=request.form.get("de")
        
        result=[]
        # loop on the docsymbols
        for record in data_send_multiple:
            result.append(ods.ods_rutines.download_file_and_send_to_ods_by_languages(record,ar,zh,en,fr,ru,es,de))  
        print("inside exporttoodswithfilebylanguages")
        print(result)       
        # create log
        ods.ods_rutines.add_log(datetime.datetime.now(tz=datetime.timezone.utc),session['username'],"ODS send file to ods endpoint called from the system!!!")     
        
        # create analytics
        ods.ods_rutines.add_analytics(datetime.datetime.now(tz=datetime.timezone.utc),session['username'],"send_file_endpoint",result)
        
        return json.dumps(result)
    
    @app.route('/exporttoodswithfile',methods=['POST'])
    def exporttoodswithfile():
        data_send_multiple= request.form["docsymbols2"].replace("\r","").split("\n")
        result=[]
        for record in data_send_multiple:
            result.append(ods.ods_rutines.download_file_and_send_to_ods(record))  
        # create log
        ods.ods_rutines.add_log(datetime.datetime.now(tz=datetime.timezone.utc),session['username'],"ODS send file to ods endpoint called from the system!!!")     
        
        # create analytics
        ods.ods_rutines.add_analytics(datetime.datetime.now(tz=datetime.timezone.utc),session['username'],"send_file_endpoint",result)
        
        return json.dumps(result)
    
    ############################################################################
    # LOGOUT
    ############################################################################
    @app.route('/logout')
    def logout():
        # create log
        ods.ods_rutines.add_log(datetime.datetime.now(tz=datetime.timezone.utc),session['username'],"Disconnected from the system!!!")
        print(f'session b4 logout {session}')
        # remove the username from the session if it is there
        session.pop('username', None)
        session.pop('show_display', None)
        session.pop('show_create_update',None)
        session.pop('show_send_file', None)
        session.pop('show_jobnumbers_management', None)
        session.pop('show_parameters', None)
        session.pop('prefix_site',None)
        

        print(f'logout from {session}')
        #session.clear()
        #print(session)
        return redirect(url_for("login"))
    
    
    @app.route("/display_logs",methods=['GET'])
    def display_logs():
        try:
            # Check if user is authenticated
            if 'username' not in session:
                return jsonify({"error": "User not authenticated"}), 401
            
            client = MongoClient(database_conn)
            my_database = client["odsActions"] 
            my_collection = my_database["ods_actions_logs_collection"]
            
            # get all the logs
            my_logs=my_collection.find(sort=[( "date", -1 )])
                
            # just render the logs
            return json.loads(json_util.dumps(my_logs))
        except Exception as e:
            print(f"Error in display_logs: {e}")
            return jsonify({"error": "Internal server error"}), 500
    
    '''
    Display the IP address a remote resource sees in its logs. Necessary for firewall updates.
    '''
    @app.route("/ip")
    def get_ip():
        data = requests.get("https://api.ipify.org?format=json")
        return data.json()
        
    return app
app = create_app()