import json
import os
import ods.ods_rutines
from flask import Flask,render_template,request


return_data=""

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
    
    @app.route('/')
    def index_vue():
        return render_template('index_vue.html')


    ############################################################################
    # DISPLAY METADATA FROM ODS
    ############################################################################

    @app.route('/loading_symbol',methods=['POST'])
    def loading_symbol():
        docsymbols = request.form["docsymbols"].split("\n")
        data= [ ods.ods_rutines.ods_get_loading_symbol(docsymbol)  for docsymbol in docsymbols ]   
        print(data)
        return data
        
    ############################################################################
    # CREATE / UPDATE METADATA
    ############################################################################
    
    @app.route('/create_metadata_ods',methods=['POST'])
    def ods_create_update_metadata():

        docsymbol= request.form["docsymbols1"]
        result=ods.ods_rutines.ods_create_update_metadata(docsymbol)
        print(result["status"])

        if (result["status"]!= 1) :
            text="Metadata not created Something happened!!!"
        else:
            text="Metadata created!!!"
            
        data=(docsymbol,text)
        print(json.dumps(data))
        return json.dumps(data)
    
    
    # @app.route('/send_one_file_ods',methods=['POST'])
    # def send_one_file_ods():

    #     docsymbol= request.form["docsymbol"]
    #     jobnumber= request.form["jobnumber"]
    #     language= request.form["language"]        
    #     path= request.form["path"]
    #     result=ods.ods_rutines.ods_file_upload_simple_file(docsymbol,jobnumber,language,path)
    #     result=result["status"]
    #     if (result!= 1) :
    #         text="File not uploaded Something happened!!!"
    #     else:
    #         text="File uploaded!!!"
            
    #     data=(docsymbol,jobnumber,text)
        
    #     return json.dumps(data)

    
    # @app.route('/update_one_file_ods',methods=['PATCH'])
    # def update_one_file_ods():

    #     docsymbol= request.form["docsymbol"]
    #     language= request.form["language"]       
    #     field= request.form["field"]   
    #     fieldvalue= request.form["fieldvalue"] 
    #     result=ods.ods_rutines.ods_update_metada(docsymbol,field,fieldvalue,language)
    #     result=result["status"]
    #     if (result!= 1) :
    #         text="Metadata not updated!!!"
    #     else:
    #         text="Metadata updated!!!"
            
    #     data=(docsymbol,field,fieldvalue,language,text)
        
    #     return json.dumps(data)       
    
    # @app.route('/update_multiple_file_ods',methods=['PATCH'])
    # def update_multiple_file_ods():  
        
    #     data_update_multiple= request.form["data_send_multiple5"].replace("\r","").split("\n")
    #     data=[]
    #     for my_data in data_update_multiple:
    #         my_data=my_data.replace("\"","")
    #         my_data0=my_data.split(",")
    #         result=ods.ods_rutines.ods_update_metada(my_data0[0],my_data0[1],my_data0[2],my_data0[3])    
    #         result=result["status"]
    #         if (result!= 1) :
    #              text="File not updated Something happened!!!"
    #         else:
    #              text="File updated!!!"
    #         data.append(
    #             (my_data0[0],my_data0[1],my_data0[2],my_data0[3],text)
    #             )
        
    #     return json.dumps(data)  
                
    
    # @app.route('/send_multiple_file_ods',methods=['POST'])
    # def send_multiple_file_ods():

    #     data_send_multiple= request.form["data_send_multiple4"].replace("\r","").split("\n")
    #     data=[]
    #     for record in data_send_multiple:
    #         record=record.replace("\"","")
    #         my_data=record.split(",")
    #         result=ods.ods_rutines.ods_file_upload_simple_file(my_data[0],my_data[1],my_data[2],my_data[3])    
    #         result=result["status"]
    #         if (result!= 1) :
    #              text="File not uploaded Something happened!!!"
    #         else:
    #              text="File uploaded!!!"
    #         data.append(
    #             (my_data[0],my_data[1],my_data[2],my_data[3],text)
    #             )
        
    #     return json.dumps(data)

    # @app.route('/exporttoods',methods=['GET','POST'])
    # def exporttoods():
    #     data=[]
    #     symbols=request.form.get("docsymbols1")
    #     message=ods.ods_rutines.export_to_ods(symbols)
    #     data.append(
    #         (symbols,message)
    #     )
        
    #     return json.dumps(data)
    
    ############################################################################
    # SEND FILE TO ODS
    ############################################################################
    
    @app.route('/exporttoodswithfile',methods=['POST'])
    def exporttoodswithfile():
        data_send_multiple= request.form["docsymbols2"].replace("\r","").split("\n")
        result=[]
        for record in data_send_multiple:
            result.append(ods.ods_rutines.download_file_and_send_to_ods(record))  
        
        print(json.dumps(result))
        return json.dumps(result)
        
    return app