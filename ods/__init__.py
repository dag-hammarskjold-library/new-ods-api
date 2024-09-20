##############################################################################################
##########  IMPORTS
##############################################################################################

from werkzeug.security import check_password_hash, generate_password_hash
import json
import datetime
import os
import ods.ods_rutines
from flask import Flask,render_template,request,redirect,session
from decouple import config
from pymongo import MongoClient

return_data=""

########################################################################
# definition of the credentials of the ODS API
########################################################################

base_url = config("base_url")
username = config("username")
password = config("password")
client_id = config("client_id")
client_secret = config("client_secret")


##############################################################################################
##########  APP INIZIALISATION
##############################################################################################

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev'
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
    # MAIN ROUTE
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
            if request.form.get("email")==config("default_username"):

                if request.form.get("password")==config("default_password"):
                    
                    # special user
                    ods.ods_rutines.add_log(datetime.datetime.now(tz=datetime.timezone.utc),config("default_username"),"Connected to the system!!!")
                    
                    # add the username to the session
                    session['username'] = config("default_username")
                    
                    #return render_template('index.html',user_connected=config("DEFAULT_USER_NAME"))
                    return redirect('index')

            
            # check if the user exists in the database with the good password
            client = MongoClient(config("CONN"))
            my_database = client["undlFiles"] 
            my_collection = my_database["ods_action_users_collection"]


            user = {
                "email": request.form.get("email"),
            }

            results= list(my_collection.find(user))
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
                        
                        # add the username to the session
                        session['username'] = result["name"]
                        
                        find_record=True

                        if session['username']!="":
                            return redirect('index')
                        else:
                            return redirect("login.html")
                        
                if find_record==False:
                    
                    # user not found
                    error="User not found in the database!!!"
                    return render_template("login.html",error=error)

    ############################################################################
    # MAIN ROUTE
    ############################################################################
    
    @app.route('/index')
    def index_vue():
        return render_template('index_vue.html')


    ############################################################################
    # DISPLAY METADATA FROM ODS
    ############################################################################

    @app.route('/loading_symbol',methods=['POST'])
    def loading_symbol():
        docsymbols = request.form["docsymbols"].split("\r\n")
        print(docsymbols)
        data= [ ods.ods_rutines.ods_get_loading_symbol(docsymbol)  for docsymbol in docsymbols ]   
        return data
        
    ############################################################################
    # CREATE / UPDATE METADATA
    ############################################################################
    
    @app.route('/create_metadata_ods',methods=['POST'])
    def ods_create_update_metadata():

        docsymbols = request.form["docsymbols1"].replace("\r","").split("\n")
        data=[]
        
        for docsymbol in docsymbols:
            result=ods.ods_rutines.ods_create_update_metadata(docsymbol)
            text="-1 this is default value"
            if (result["status"]== 0 and result["update"]==False):
                text="Metadata not created Something happened!!!"
            if (result["status"]== 1 and result["update"]==False) :
                text="Metadata created!!!"
            if (result["status"]== 2 and result["update"]==True) :
                text="Metadata updated!!!"                
            summary={
                "docsymbol":docsymbol,
                "text":text
                }
            data.append(summary)
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
        
        return json.dumps(result)
        
    return app

app = create_app()