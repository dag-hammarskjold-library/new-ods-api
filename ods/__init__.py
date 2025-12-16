##############################################################################################
##########  IMPORTS
##############################################################################################

from werkzeug.security import check_password_hash, generate_password_hash
import json
import datetime
import os
import requests
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
                    session["show_jobnumbers_management"]=True
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
                        session["show_display"]=result["show_display"]
                        session["show_create_update"]=result["show_create_update"]
                        session["show_send_file"]=result["show_send_file"]
                        session["show_jobnumbers_management"]=result["show_jobnumbers_management"]
                        session["show_parameters"]=result["show_parameters"]
                        
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
                session_show_display=session["show_display"]
                session_show_create_update=session["show_create_update"]
                session_show_send_file=session["show_send_file"]
                session_show_jobnumbers_management=session["show_jobnumbers_management"]
                session_show_parameters=session["show_parameters"]

                return render_template('index_vue.html',
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
    

    #this is a temp route to diplay documents in a language using a symbol main8
    @app.route("/<lang>/<path:symbol>")
    def show_document1(symbol, lang=None):
        client = MongoClient(database_conn)
        my_database = client["undlFiles"] 
        filesColl=my_database.files
        lang=lang.upper()
        LANGUAGES = {
            'ar': 'العربية',
            'zh': '中文',
            'en': 'English',
            'fr': 'Français',
            'ru': 'Русский',
            'es': 'Español'
        }
        LANGUAGESList =['DE', 'AR', 'FR', 'ES', 'RU', 'ZH', 'EN']
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
            return render_template("language_selection.html", symbol=symbol, languages=languages, LANGUAGES=LANGUAGES)

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
            mongo_query["languages"] = lang
        
        # Calculate skip
        skip = (page - 1) * limit
        
        # Find documents with sorting, skipping, and limiting
        docs = filesColl.find(mongo_query, collation=cln).sort([("identifiers.value", 1)]).skip(skip).limit(limit)
        
        results = []
        for doc in docs:
            uri = doc.get("uri", "")
            uri="https://ods-actions.sjtwsr1nwt8y4.us-east-1.cs.amazonlightsail.com/"+lang+"/"+quote(doc["identifiers"][0]["value"], safe='/')
            for ident in doc.get("identifiers", []):
                if ident["value"].startswith(query):
                    results.append({"identifier": ident["value"], "url": uri})
                    break  # Assuming one matching identifier per document
        return jsonify(results)








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
        Download the chatbot user manual as markdown file
        """
        try:
            from pathlib import Path
            from flask import send_file, Response
            
            # Get the manual markdown file
            ai_path = Path(__file__).parent.parent / "ai"
            manual_path = ai_path / "CHATBOT_USER_MANUAL.md"
            
            if not manual_path.exists():
                error_msg = f'User manual not found at: {manual_path}'
                app.logger.error(error_msg)
                return Response(
                    error_msg,
                    status=404,
                    mimetype='text/plain'
                )
            
            # Return markdown file
            return send_file(
                str(manual_path),
                mimetype='text/markdown',
                as_attachment=True,
                download_name='ODS_Actions_Chatbot_User_Manual.md'
            )
            
        except Exception as e:
            error_msg = f'Error downloading manual: {str(e)}'
            app.logger.error(f"Error downloading manual: {str(e)}", exc_info=True)
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