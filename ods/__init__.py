##############################################################################################
##########  IMPORTS
##############################################################################################

from werkzeug.security import check_password_hash, generate_password_hash
import json
import datetime
import os
import platform
import requests
import copy
import traceback
import ods.ods_rutines
from flask import Flask, jsonify,render_template,request,redirect,session, url_for, send_file
from io import BytesIO
from urllib.parse import quote, unquote
from pymongo.collation import Collation
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
    
    # Serve static files from public folder
    @app.route('/public/<path:filename>')
    def public_files(filename):
        import os
        from flask import send_from_directory
        public_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'public')
        return send_from_directory(public_dir, filename)

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
                    session["show_download_files"]=True
                    session["show_parameters"]=True
                    

                    return jsonify({
                        "success": True,
                        "message": "Login successful",
                        "redirect": url_for("index_vue")
                    })

            
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
                return jsonify({
                    "success": False,
                    "error": "Please check your credentials",
                    "error_type": "invalid_credentials"
                })
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
                        # Use the SAME conversion logic as list_users route for consistency
                        def to_string_value(val):
                            if val is None:
                                return "false"
                            if isinstance(val, bool):
                                return "true" if val else "false"
                            if isinstance(val, str):
                                normalized = val.strip().lower()
                                return "true" if normalized == "true" else "false"
                            return "false"
                        
                        # Convert to strings first (same as list_users), then to boolean for session
                        show_display_str = to_string_value(result.get("show_display", "false"))
                        show_create_update_str = to_string_value(result.get("show_create_update", "false"))
                        show_send_file_str = to_string_value(result.get("show_send_file", "false"))
                        show_download_files_str = to_string_value(result.get("show_download_files", "false"))
                        show_parameters_str = to_string_value(result.get("show_parameters", "false"))
                        
                        # Convert strings to boolean for session storage
                        session["show_display"] = show_display_str == "true"
                        session["show_create_update"] = show_create_update_str == "true"
                        session["show_send_file"] = show_send_file_str == "true"
                        session["show_download_files"] = show_download_files_str == "true"
                        session["show_parameters"] = show_parameters_str == "true"
                        
                        find_record=True
                        print(f'session after login {session}')
                        print(f"username is {session['username']}")
                        if session['username']!="":
                            return jsonify({
                                "success": True,
                                "message": "Login successful",
                                "redirect": url_for("index_vue")
                            })
                        else:
                            return jsonify({
                                "success": False,
                                "error": "Session error",
                                "error_type": "session_error"
                            })
                        
                if find_record==False:
                    
                    # incorrect password
                    return jsonify({
                        "success": False,
                        "error": "Please check your credentials",
                        "error_type": "invalid_credentials"
                    })

    ############################################################################
    # MAIN ROUTE
    ############################################################################
    
    @app.route('/index')
    def index_vue():
        if session:
            if session['username']!="":

                session_username=session['username']
                # Convert boolean values to lowercase strings for Vue component
                # Vue component checks for 'true' string, not boolean True
                def to_string(val):
                    if isinstance(val, bool):
                        return "true" if val else "false"
                    if isinstance(val, str):
                        return val.lower().strip()
                    return "false"
                
                session_show_display=to_string(session.get("show_display", False))
                session_show_create_update=to_string(session.get("show_create_update", False))
                session_show_send_file=to_string(session.get("show_send_file", False))
                session_show_download_files=to_string(session.get("show_download_files", False))
                session_show_parameters=to_string(session.get("show_parameters", False))

                return render_template('index_vue.html',
                                       session_username=session_username,
                                       session_show_display=session_show_display,
                                       session_show_create_update=session_show_create_update,
                                       session_show_send_file=session_show_send_file,
                                       session_show_download_files=session_show_download_files,
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

            # Helper function to convert to string "true" or "false"
            def get_string_value(key):
                value = request.form.get(key)
                # If value is None or empty string, return "false"
                if value is None or value == '':
                    return "false"
                # If it's already a string, normalize it
                if isinstance(value, str):
                    normalized = value.lower().strip()
                    return "true" if normalized == 'true' else "false"
                # If it's a boolean, convert to string
                if isinstance(value, bool):
                    return "true" if value else "false"
                # For any other type, convert to string
                return "true" if bool(value) else "false"

            # Ensure show_download_files is always set (default to "false" if not provided)
            show_download_files_value = request.form.get("show_download_files")
            if show_download_files_value is None:
                show_download_files = "false"
            else:
                show_download_files = get_string_value("show_download_files")
            
            user = {
                "site":request.form.get("site"),
                "email": request.form.get("email"),
                "password": pwd,
                "show_display": get_string_value("show_display"),
                "show_create_update": get_string_value("show_create_update"),
                "show_send_file": get_string_value("show_send_file"),
                "show_download_files": show_download_files,
                "show_parameters": get_string_value("show_parameters"),
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
    # LIST USERS ROUTE
    ############################################################################
    
    @app.route("/list_users", methods=['GET'])
    def list_users():
        try:
            client = MongoClient(database_conn)
            my_database = client["odsActions"] 
            my_collection = my_database["ods_actions_users_collection"]
            
            # Get all users (excluding passwords), sorted by email
            my_users = my_collection.find({}, {"password": 0}, sort=[("email", 1)])
            
            # Convert to list and format dates, ensuring no duplicates by email
            users_list = []
            seen_emails = set()
            for user in my_users:
                # Helper function to convert MongoDB value to string "true"/"false"
                def to_string_value(val):
                    if val is None:
                        return "false"
                    if isinstance(val, bool):
                        return "true" if val else "false"
                    if isinstance(val, str):
                        normalized = val.strip().lower()
                        return "true" if normalized == "true" else "false"
                    return "false"
                
                # Convert MongoDB document to dict, preserving all fields
                user_dict = json.loads(json_util.dumps(user))
                
                # Get email from user_dict
                email = user_dict.get("email", "")
                # Only add if we haven't seen this email before
                if email and email not in seen_emails:
                    seen_emails.add(email)
                    
                    # Convert all permission fields to strings "true"/"false" using ORIGINAL MongoDB values
                    # This ensures we use the actual database values, not defaults
                    user_dict["show_display"] = to_string_value(user.get("show_display", "false"))
                    user_dict["show_create_update"] = to_string_value(user.get("show_create_update", "false"))
                    user_dict["show_send_file"] = to_string_value(user.get("show_send_file", "false"))
                    user_dict["show_download_files"] = to_string_value(user.get("show_download_files", "false"))
                    user_dict["show_parameters"] = to_string_value(user.get("show_parameters", "false"))
                    
                    # Debug: log values for eric.attere@un.org
                    if email == "eric.attere@un.org":
                        print(f"\n{'='*60}")
                        print(f"=== DEBUG: Processing user {email} ===")
                        print(f"{'='*60}")
                        print(f"MongoDB document keys: {list(user.keys())}")
                        print(f"\nMongoDB RAW values (before any conversion):")
                        print(f"  show_display: {repr(user.get('show_display'))} (type: {type(user.get('show_display')).__name__}, in dict: {'show_display' in user})")
                        print(f"  show_create_update: {repr(user.get('show_create_update'))} (type: {type(user.get('show_create_update')).__name__}, in dict: {'show_create_update' in user})")
                        print(f"  show_send_file: {repr(user.get('show_send_file'))} (type: {type(user.get('show_send_file')).__name__}, in dict: {'show_send_file' in user})")
                        print(f"  show_download_files: {repr(user.get('show_download_files'))} (type: {type(user.get('show_download_files')).__name__}, in dict: {'show_download_files' in user})")
                        print(f"  show_parameters: {repr(user.get('show_parameters'))} (type: {type(user.get('show_parameters')).__name__}, in dict: {'show_parameters' in user})")
                        print(f"\nAfter to_string_value conversion:")
                        print(f"  show_display: {user_dict.get('show_display')} (type: {type(user_dict.get('show_display')).__name__})")
                        print(f"  show_create_update: {user_dict.get('show_create_update')} (type: {type(user_dict.get('show_create_update')).__name__})")
                        print(f"  show_send_file: {user_dict.get('show_send_file')} (type: {type(user_dict.get('show_send_file')).__name__})")
                        print(f"  show_download_files: {user_dict.get('show_download_files')} (type: {type(user_dict.get('show_download_files')).__name__})")
                        print(f"  show_parameters: {user_dict.get('show_parameters')} (type: {type(user_dict.get('show_parameters')).__name__})")
                        print(f"{'='*60}\n")
                    
                    users_list.append(user_dict)
            
            return jsonify(users_list)
            
        except Exception as e:
            return jsonify({
                "error": f"Error fetching users: {str(e)}"
            }), 500

    ############################################################################
    # UPDATE USER ROUTE
    ############################################################################
    
    @app.route("/update_user", methods=['POST'])
    def update_user():
        try:
            client = MongoClient(database_conn)
            my_database = client["odsActions"] 
            my_collection = my_database["ods_actions_users_collection"]
            
            user_email = request.form.get("email", "").strip()
            if not user_email:
                return jsonify({
                    "status": "NOK",
                    "message": "Email is required"
                }), 400
            
            # Build update document
            # Store values as strings "true" or "false" (not booleans)
            def get_string_value(key):
                value = request.form.get(key)
                # If value is None or empty string, return "false"
                if value is None or value == '':
                    return "false"
                # If it's already a string, normalize it
                if isinstance(value, str):
                    normalized = value.lower().strip()
                    return "true" if normalized == 'true' else "false"
                # If it's a boolean, convert to string
                if isinstance(value, bool):
                    return "true" if value else "false"
                # For any other type, convert to string
                return "true" if bool(value) else "false"
            
            # Ensure show_download_files is always set (default to "false" if not provided)
            show_download_files_value = request.form.get("show_download_files")
            if show_download_files_value is None:
                show_download_files = "false"
            else:
                show_download_files = get_string_value("show_download_files")
            
            update_data = {
                "site": request.form.get("site"),
                "show_display": get_string_value("show_display"),
                "show_create_update": get_string_value("show_create_update"),
                "show_send_file": get_string_value("show_send_file"),
                "show_download_files": show_download_files,
                "show_parameters": get_string_value("show_parameters")
            }
            
            # Only update password if provided
            new_password = request.form.get("password", "").strip()
            if new_password:
                update_data["password"] = generate_password_hash(new_password)
            
            # Update user
            result = my_collection.update_one(
                {"email": user_email},
                {"$set": update_data}
            )
            
            if result.modified_count > 0 or result.matched_count > 0:
                # Create log
                ods.ods_rutines.add_log(
                    datetime.datetime.now(tz=datetime.timezone.utc),
                    session.get('username', 'unknown_user'),
                    f"User {user_email} updated in the system!!!"
                )
                
                return jsonify({
                    "status": "OK",
                    "message": "User updated successfully!!!"
                })
            else:
                return jsonify({
                    "status": "NOK",
                    "message": "User not found or no changes made"
                }), 404
            
        except Exception as e:
            return jsonify({
                "status": "NOK",
                "message": f"Error updating user: {str(e)}"
            }), 500

    ############################################################################
    # DELETE USER ROUTE
    ############################################################################
    
    @app.route("/delete_user", methods=['POST'])
    def delete_user():
        try:
            client = MongoClient(database_conn)
            my_database = client["odsActions"] 
            my_collection = my_database["ods_actions_users_collection"]
            
            user_email = request.form.get("email", "").strip()
            if not user_email:
                return jsonify({
                    "status": "NOK",
                    "message": "Email is required"
                }), 400
            
            # Prevent deleting the default user
            if user_email == config("DEFAULT_USERNAME"):
                return jsonify({
                    "status": "NOK",
                    "message": "Cannot delete the default user"
                }), 403
            
            # Prevent users from deleting themselves
            if user_email == session.get('username', ''):
                return jsonify({
                    "status": "NOK",
                    "message": "You cannot delete your own account"
                }), 403
            
            # Delete user
            result = my_collection.delete_one({"email": user_email})
            
            if result.deleted_count > 0:
                # Create log
                ods.ods_rutines.add_log(
                    datetime.datetime.now(tz=datetime.timezone.utc),
                    session.get('username', 'unknown_user'),
                    f"User {user_email} deleted from the system!!!"
                )
                
                return jsonify({
                    "status": "OK",
                    "message": "User deleted successfully!!!"
                })
            else:
                return jsonify({
                    "status": "NOK",
                    "message": "User not found"
                }), 404
            
        except Exception as e:
            return jsonify({
                "status": "NOK",
                "message": f"Error deleting user: {str(e)}"
            }), 500

    ############################################################################
    # DISPLAY METADATA FROM ODS
    ############################################################################

    @app.route('/loading_symbol',methods=['POST'])
    def loading_symbol():
        docsymbols = request.form["docsymbols"].split("\r\n")
        final=[]
        
        for docsymbol in docsymbols:
            result=ods.ods_rutines.ods_get_loading_symbol(docsymbol)
            try:
                tcodes=result["body"]["data"][0]["tcodes"]
                #print(tcodes)
                subjects=[ods.ods_rutines.get_subject(tcode) for tcode in tcodes]
                result["body"]["data"][0]["subjects"]=subjects
            except:
                pass
            
            # Get title and other metadata from CDB
            try:
                cdb_data = ods.ods_rutines.get_data_from_cb(docsymbol)
                if cdb_data and len(cdb_data) > 0:
                    cdb_record = cdb_data[0]
                    # Add title from CDB to the result
                    result["body"]["data"][0]["title"] = cdb_record.get("title", "Not found")
                    # Also add other CDB fields if they're missing
                    if "agendas" not in result["body"]["data"][0] or not result["body"]["data"][0]["agendas"]:
                        result["body"]["data"][0]["agendas"] = cdb_record.get("agendas", "Not found")
                    if "sessions" not in result["body"]["data"][0] or not result["body"]["data"][0]["sessions"]:
                        result["body"]["data"][0]["sessions"] = cdb_record.get("sessions", "Not found")
                    if "subjects" not in result["body"]["data"][0] or not result["body"]["data"][0]["subjects"]:
                        result["body"]["data"][0]["subjects"] = cdb_record.get("subjects", "Not found")
            except:
                # If CDB data is not available, set title to "Not found"
                result["body"]["data"][0]["title"] = "Not found"
            
            result["docsymbol"]=docsymbol
            final.append(result)
        
        # create log
        username = session.get('username', 'unknown_user')
        ods.ods_rutines.add_log(datetime.datetime.now(tz=datetime.timezone.utc),username,"ODS loading symbol endpoint called from the system!!!")
        
        # create analytics
        ods.ods_rutines.add_analytics(datetime.datetime.now(tz=datetime.timezone.utc),username,"loading_symbol_endpoint",final)
        
        return final
        
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
    
    @app.route('/exporttoodswithfile',methods=['POST'])
    def exporttoodswithfile():
        data_send_multiple= request.form["docsymbols2"].replace("\r","").split("\n")
        result=[]
        for record in data_send_multiple:
            result.append(ods.ods_rutines.download_file_and_send_to_ods(record))  
        # create log
        username = session.get('username', 'unknown_user')
        ods.ods_rutines.add_log(datetime.datetime.now(tz=datetime.timezone.utc), username, "ODS send file to ods endpoint called from the system!!!")     
        
        # create analytics
        ods.ods_rutines.add_analytics(datetime.datetime.now(tz=datetime.timezone.utc), username, "send_file_endpoint", result)
        
        return jsonify(result)
    
    ############################################################################
    # DOWNLOAD FILE FROM ODS
    ############################################################################
    
    @app.route('/download_file_from_ods', methods=['POST'])
    def download_file_from_ods_route():
        """
        Download PDF files from ODS for a document symbol and multiple languages.
        Expects JSON with "docsymbol": "symbol", "languages": ["lang1", "lang2", ...]
        """
        print(f"DEBUG: download_file_from_ods endpoint called")
        try:
            # Expect JSON with docsymbol and languages array
            data = request.get_json()
            docsymbol = data.get('docsymbol', '').strip()
            languages = data.get('languages', [])
            
            if not docsymbol:
                return jsonify({
                    "status": 0,
                    "error": "docsymbol is required"
                }), 400
            
            if not languages or not isinstance(languages, list):
                return jsonify({
                    "status": 0,
                    "error": "languages array is required"
                }), 400
            
            results = []
            username = session.get('username', 'unknown_user')
            print(f"DEBUG: Username from session: {username}")
            
            for language in languages:
                language = language.strip()
                if not language:
                    continue
                
                # Call the download function
                result = ods.ods_rutines.download_file_from_ods(docsymbol, language)
                result['docsymbol'] = docsymbol
                result['language'] = language
                
                # Create log for each download
                log_message = f"Download file from ODS: {docsymbol} [{language}]"
                if result.get("status") == 1:
                    log_message += f" - Success: {result.get('filename', '')}"
                else:
                    log_message += f" - Failed: {result.get('message', '')}"
                
                ods.ods_rutines.add_log(
                    datetime.datetime.now(tz=datetime.timezone.utc),
                    username,
                    log_message
                )
                
                results.append(result)
            
            # Create analytics for this docsymbol - data is the results array for all languages
            analytics_data = results
            print(f"DEBUG: Results data: {analytics_data}")
            print(f"DEBUG: Calling add_analytics with action: download_file_from_ods_endpoint, data length: {len(analytics_data) if analytics_data else 'None'}")
            if not analytics_data:
                print(f"ERROR: analytics_data is empty!")
            else:
                try:
                    ods.ods_rutines.add_analytics(
                        datetime.datetime.now(tz=datetime.timezone.utc),
                        username,
                        "download_file_from_ods_endpoint",
                        analytics_data
                    )
                    print(f"DEBUG: add_analytics call completed successfully")
                except Exception as e:
                    print(f"ERROR: add_analytics failed: {e}")
                    print(f"ERROR: Traceback: {traceback.format_exc()}")
            print(f"DEBUG: add_analytics call completed")
            
            return jsonify(results)
            
        except Exception as e:
            # Log error
            username = session.get('username', 'unknown_user')
            ods.ods_rutines.add_log(
                datetime.datetime.now(tz=datetime.timezone.utc),
                username,
                f"Error downloading file from ODS: {str(e)}"
            )
            
            return jsonify({
                "status": 0,
                "error": f"Error downloading file: {str(e)}"
            }), 500
    
    ############################################################################
    # BATCH DOWNLOAD FILES FROM ODS
    ############################################################################
    
    @app.route('/batch_download_files_from_ods', methods=['POST'])
    def batch_download_files_from_ods_route():
        """
        Download multiple PDF files from ODS for multiple document symbols and multiple languages.
        Accepts POST requests with docsymbols (array) and languages array.
        Supports backward compatibility with single docsymbol.
        """
        try:
            # Get parameters from request
            if request.is_json:
                # Check for new format: array of symbols
                docsymbols = request.json.get('docsymbols', [])
                # Backward compatibility: single docsymbol
                if not docsymbols:
                    single_symbol = request.json.get('docsymbol', '').strip()
                    if single_symbol:
                        docsymbols = [single_symbol]
                
                languages = request.json.get('languages', [])
            else:
                # Form data - check for multiple symbols
                docsymbols_str = request.form.get('docsymbols', '')
                single_symbol = request.form.get('docsymbol', '').strip()
                
                if docsymbols_str:
                    # Parse comma/newline separated symbols
                    docsymbols = [s.strip() for s in docsymbols_str.replace('\n', ',').split(',') if s.strip()]
                elif single_symbol:
                    docsymbols = [single_symbol]
                else:
                    docsymbols = []
                
                # Languages can come as comma-separated string or array
                languages_str = request.form.get('languages', '')
                if languages_str:
                    languages = [lang.strip() for lang in languages_str.split(',') if lang.strip()]
                else:
                    languages = []
            
            # Validate required parameters
            username = session.get('username', 'unknown_user')
            
            if not docsymbols or len(docsymbols) == 0:
                error_result = {
                    "status": 0,
                    "error": "At least one document symbol is required"
                }
                # Create analytics for validation error
                ods.ods_rutines.add_analytics(
                    datetime.datetime.now(tz=datetime.timezone.utc),
                    username,
                    "batch_download_files_from_ods_endpoint",
                    [error_result]
                )
                return jsonify(error_result), 400
            
            if not languages or len(languages) == 0:
                error_result = {
                    "status": 0,
                    "error": "At least one language must be selected"
                }
                # Create analytics for validation error
                ods.ods_rutines.add_analytics(
                    datetime.datetime.now(tz=datetime.timezone.utc),
                    username,
                    "batch_download_files_from_ods_endpoint",
                    [error_result]
                )
                return jsonify(error_result), 400
            
            # Download files for each symbol and each language
            results = []
            for docsymbol in docsymbols:
                for language in languages:
                    result = ods.ods_rutines.download_file_from_ods(docsymbol, language)
                    # Add docsymbol to result for tracking
                    result['docsymbol'] = docsymbol
                    results.append(result)
            
            # Create log
            successful = sum(1 for r in results if r.get("status") == 1)
            total_files = len(docsymbols) * len(languages)
            log_message = f"Batch download from ODS: {len(docsymbols)} symbol(s), {successful}/{total_files} files downloaded successfully"
            
            ods.ods_rutines.add_log(
                datetime.datetime.now(tz=datetime.timezone.utc),
                username,
                log_message
            )
            
            # Create analytics - exactly like send_file_endpoint
            ods.ods_rutines.add_analytics(
                datetime.datetime.now(tz=datetime.timezone.utc),
                username,
                "batch_download_files_from_ods_endpoint",
                results
            )
            
            return jsonify({
                "status": 1,
                "docsymbols": docsymbols,
                "total_symbols": len(docsymbols),
                "total": total_files,
                "successful": successful,
                "results": results
            })
            
        except Exception as e:
            # Log error
            username = session.get('username', 'unknown_user')
            error_message = f"Error batch downloading files from ODS: {str(e)}"
            
            ods.ods_rutines.add_log(
                datetime.datetime.now(tz=datetime.timezone.utc),
                username,
                error_message
            )
            
            # Create analytics for error
            error_result = {
                "status": 0,
                "error": f"Error batch downloading files: {str(e)}"
            }
            ods.ods_rutines.add_analytics(
                datetime.datetime.now(tz=datetime.timezone.utc),
                username,
                "batch_download_files_from_ods_endpoint",
                [error_result]
            )
            
            return jsonify(error_result), 500
    
    ############################################################################
    # SERVE DOWNLOADED FILE CONTENT
    ############################################################################
    
    @app.route('/download_file_content', methods=['GET'])
    def download_file_content_route():
        """
        Serve a downloaded file from the temp directory for browser download.
        """
        try:
            filepath = request.args.get('filepath', '')
            if not filepath:
                return jsonify({"error": "filepath parameter is required"}), 400
            
            # Security: ensure file is in temp_01 directory (used for download from ODS)
            if platform.system() in ['Windows', 'nt']:
                temp_dir = os.path.abspath('ods\\temp_01')
            else:
                temp_dir = os.path.abspath('./ods/tmp_01')
            
            filepath_abs = os.path.abspath(filepath)
            temp_dir_abs = os.path.abspath(temp_dir)
            
            # Verify file is within temp directory
            if not filepath_abs.startswith(temp_dir_abs):
                return jsonify({"error": "Invalid file path"}), 403
            
            if not os.path.exists(filepath_abs):
                return jsonify({"error": "File not found"}), 404
            
            return send_file(
                filepath_abs,
                as_attachment=True,
                download_name=os.path.basename(filepath_abs)
            )
            
        except Exception as e:
            return jsonify({
                "error": f"Error serving file: {str(e)}"
            }), 500
    
    ############################################################################
    # CLEANUP TEMP DOWNLOAD FOLDER
    ############################################################################
    
    @app.route('/cleanup_download_temp', methods=['POST'])
    def cleanup_download_temp_route():
        """
        Clean up the tmp_01 folder after downloads are complete.
        Removes all files from the temporary download directory.
        """
        try:
            # Determine temp directory path based on platform
            if platform.system() in ['Windows', 'nt']:
                temp_dir = os.path.abspath('ods\\temp_01')
            else:
                temp_dir = os.path.abspath('./ods/tmp_01')
            
            # Check if directory exists
            if not os.path.exists(temp_dir):
                return jsonify({
                    "status": 1,
                    "message": "Temp directory does not exist, nothing to clean"
                })
            
            # Remove all files in the directory
            files_removed = 0
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        files_removed += 1
                except Exception as e:
                    # Log error but continue cleaning other files
                    print(f"Error removing file {file_path}: {str(e)}")
            
            # Log cleanup action
            username = session.get('username', 'unknown_user')
            ods.ods_rutines.add_log(
                datetime.datetime.now(tz=datetime.timezone.utc),
                username,
                f"Cleaned up download temp folder: {files_removed} file(s) removed"
            )
            
            return jsonify({
                "status": 1,
                "message": f"Successfully cleaned {files_removed} file(s) from temp directory",
                "files_removed": files_removed
            })
            
        except Exception as e:
            return jsonify({
                "status": 0,
                "error": f"Error cleaning temp directory: {str(e)}"
            }), 500
    
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
        session.pop('show_download_files', None)
        session.pop('show_parameters', None)
        session.pop('prefix_site',None)
        

        print(f'logout from {session}')
        #session.clear()
        #print(session)
        return redirect(url_for("login"))
    

    #this is a temp route to diplay documents in a language using a symbol main8
    @app.route("/<lang>/<path:symbol>")
    def show_document1(symbol, lang=None):
        client = MongoClient(database_conn)
        my_database = client["undlFiles"] 
        filesColl=my_database.files
        lang=lang.upper()
        LANGUAGES = {
        #    'ar': 'العربية',
        #    'zh': '中文',
            'en': 'English',
        #    'fr': 'Français',
        #    'ru': 'Русский',
        #   'es': 'Español'
        }
        #LANGUAGESList =['DE', 'AR', 'FR', 'ES', 'RU', 'ZH', 'EN']
        LANGUAGESList =['EN']
        print(symbol)
        #symbol=unquote(symbol)
        print(f"after unquote the symbol is {symbol}")
        cln = Collation(locale='en', strength=2)
        docs = filesColl.find({"identifiers.value": symbol}, collation=cln)
        languages = [''.join(doc.get("languages")) for doc in docs]
        print(languages)
        if lang is None:
            # Find all documents matching the symbol
            docs = filesColl.find({"identifiers.value": symbol})
            languages = [''.join(doc.get("languages")) for doc in docs]
            
            if not languages:
                return "No available languages for this document.", 404
            return render_template("language_selection.html", symbol=symbol, languages='en', LANGUAGES=LANGUAGES)

        # Look up the specific document for  the given language
        doc = filesColl.find_one({"identifiers.value": symbol, "languages": lang}, collation=cln)
        if not doc or not doc.get("uri"):
            return "Document not found for this language.", 404

        # Fetch and serve the PDF
        symbol=quote(symbol, safe='/')
        print(symbol)
        uri = "https://"+doc["uri"]
        response = requests.get(uri)
        if response.status_code == 200:
            return send_file(BytesIO(response.content), download_name=f"{symbol}_{lang}.pdf", mimetype='application/pdf')
        else:
            return "Unable to fetch PDF", 502

    

    @app.route('/browse_docs', methods=['GET'])
    def search_identifiers():
        import re
        query = request.args.get('q', '')
        lang = request.args.get('lang', 'en').upper()
        lang='en'
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        if not query:
            return jsonify([])
        
        client = MongoClient(database_conn)
        my_database = client["undlFiles"] 
        filesColl = my_database.files
        cln = Collation(locale='en', strength=2, numericOrdering=True)
        
        # Build the query
        mongo_query = {"identifiers.value": {"$regex": "^" + re.escape(query)}}
        if lang:
            #mongo_query["languages"] = lang
            mongo_query["languages"] = 'en'
        
        # Calculate skip
        skip = (page - 1) * limit
        
        # Find documents with sorting, skipping, and limiting
        docs = filesColl.find(mongo_query, collation=cln).sort([("identifiers.value", 1)]).skip(skip).limit(limit)
        
        results = {}
        for doc in docs:
            uri = doc.get("uri", "")
            uri="https://ods-actions.sjtwsr1nwt8y4.us-east-1.cs.amazonlightsail.com/"+lang+"/"+quote(doc["identifiers"][0]["value"], safe='/')
            for ident in doc.get("identifiers", []):
                if ident["value"].startswith(query):
                    results[ident["value"]] = {"identifier": ident["value"], "url": uri}
                    break  # Assuming one matching identifier per document
        return jsonify(list(results.values()))








    @app.route("/display_logs",methods=['GET'])
    def display_logs():

        client = MongoClient(database_conn)
        my_database = client["odsActions"] 
        my_collection = my_database["ods_actions_logs_collection"]
        
        # get all the logs
        my_logs=my_collection.find(sort=[( "date", -1 )])
            
        # just render the logs
        return json.loads(json_util.dumps(my_logs))    
    
    '''
    Display the IP address a remote resource sees in its logs. Necessary for firewall updates.
    '''
    @app.route("/ip")
    def get_ip():
        data = requests.get("https://api.ipify.org?format=json")
        return data.json()
    
    ############################################################################
    # CHATBOT ENDPOINT
    ############################################################################
    
    @app.route("/chatbot", methods=['POST'])
    def chatbot():
        """
        Chatbot endpoint using Gemini API with PDF documentation context
        """
        try:
            import sys
            from pathlib import Path
            
            # Add ai folder to path
            ai_path = Path(__file__).parent.parent / "ai"
            if str(ai_path) not in sys.path:
                sys.path.insert(0, str(ai_path))
            
            from ai.chatbot import simple_chat
            
            # Get user message from request
            user_message = request.form.get('message') or request.json.get('message', '')
            
            if not user_message:
                return jsonify({
                    'success': False,
                    'error': 'No message provided'
                }), 400
            
            # Get conversation history if provided
            conversation_history = request.json.get('history', []) if request.is_json else []
            
            # Use simple_chat for stateless interactions
            # For conversation history, you can use chat_with_gemini instead
            result = simple_chat(user_message)
            
            # Log the interaction
            username = session.get('username', 'unknown_user')
            ods.ods_rutines.add_log(
                datetime.datetime.now(tz=datetime.timezone.utc),
                username,
                f"Chatbot query: {user_message[:100]}"
            )
            
            return jsonify(result)
            
        except ImportError as e:
            return jsonify({
                'success': False,
                'error': f'Chatbot module not available: {str(e)}'
            }), 500
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Error processing chat request: {str(e)}'
            }), 500
    
    @app.route("/download_chatbot_manual", methods=['GET'])
    def download_chatbot_manual():
        """
        Download the chatbot user manual as PDF file
        """
        try:
            from pathlib import Path
            from flask import send_file, Response
            
            # Get the manual PDF file
            ai_path = Path(__file__).parent.parent / "ai"
            pdf_path = ai_path / "CHATBOT_USER_MANUAL.pdf"
            
            if not pdf_path.exists():
                error_msg = f'Chatbot user manual PDF not found at: {pdf_path}'
                app.logger.error(error_msg)
                return Response(
                    error_msg,
                    status=404,
                    mimetype='text/plain'
                )
            
            # Return PDF file
            return send_file(
                str(pdf_path),
                mimetype='application/pdf',
                as_attachment=True,
                download_name='ODS_Actions_Chatbot_User_Manual.pdf'
            )
            
        except Exception as e:
            error_msg = f'Error downloading manual: {str(e)}'
            app.logger.error(f"Error downloading manual: {str(e)}", exc_info=True)
            return Response(
                error_msg,
                status=500,
                mimetype='text/plain'
            )
    
    @app.route("/download_ods_documentation", methods=['GET'])
    def download_ods_documentation():
        """
        Download the ODS Actions Documentation as PDF file
        """
        try:
            from pathlib import Path
            from flask import send_file, Response
            
            # Get the documentation PDF file
            ai_path = Path(__file__).parent.parent / "ai"
            pdf_path = ai_path / "ODS_Actions_Documentation.pdf"
            
            if not pdf_path.exists():
                error_msg = f'ODS Actions Documentation not found at: {pdf_path}'
                app.logger.error(error_msg)
                return Response(
                    error_msg,
                    status=404,
                    mimetype='text/plain'
                )
            
            return send_file(
                str(pdf_path),
                mimetype='application/pdf',
                as_attachment=True,
                download_name='ODS_Actions_Documentation.pdf'
            )
            
        except Exception as e:
            error_msg = f'Error downloading ODS documentation: {str(e)}'
            app.logger.error(f"Error downloading ODS documentation: {str(e)}", exc_info=True)
            return Response(
                error_msg,
                status=500,
                mimetype='text/plain'
            )
    
    '''
    Change user password
    '''
    @app.route("/change_password", methods=['POST'])
    def change_password():
        try:
            email = request.form.get('email')
            new_password = request.form.get('new_password')
            
            if not email or not new_password:
                return jsonify({"success": False, "message": "Email and new password are required"})
            
            if len(new_password) < 6:
                return jsonify({"success": False, "message": "Password must be at least 6 characters long"})
            
            # Connect to MongoDB
            client = MongoClient(database_conn)
            my_database = client["odsActions"]
            my_collection = my_database["ods_actions_users_collection"]
            
            # Find user by email first
            user = my_collection.find_one({"email": email})
            
            if not user:
                # Try to find user by username
                user = my_collection.find_one({"username": email})
                
                if not user:
                    # Try case-insensitive search
                    user = my_collection.find_one({"email": {"$regex": f"^{email}$", "$options": "i"}})
                    
                    if not user:
                        # Try partial match
                        user = my_collection.find_one({"email": {"$regex": email, "$options": "i"}})
                        
                        if not user:
                            return jsonify({"success": False, "message": "User not found"})
            
            # Hash the new password
            hashed_password = generate_password_hash(new_password)
            
            # Update the user's password - use the same field we found the user with
            if user.get("email"):
                update_query = {"email": user["email"]}
            else:
                update_query = {"username": user["username"]}
                
            result = my_collection.update_one(
                update_query,
                {"$set": {"password": hashed_password}}
            )
            
            if result.modified_count > 0:
                # Log the password change
                username = session.get('username', email)
                ods.ods_rutines.add_log(
                    datetime.datetime.now(tz=datetime.timezone.utc),
                    username,
                    "Password changed successfully"
                )
                
                return jsonify({"success": True, "message": "Password changed successfully"})
            else:
                return jsonify({"success": False, "message": "Failed to update password"})
                
        except Exception as e:
            return jsonify({"success": False, "message": f"Error: {str(e)}"})
        
    return app
app = create_app()