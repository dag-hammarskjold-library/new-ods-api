Vue.component('ods', {
    template: `
                <div class="card mt-5 ml-5" style="margin:auto;height:1000px;width:1150px;">
                        <div class="mt-3 d-flex justify-content-center">
                            <a href="./logout" class="link-dark rounded"><i class="fas fa-sign-out-alt"> Sign out  </i></a>
                        </div>
                        <div class="mt-3 d-flex justify-content-center sofadi-one-regular">
                            <h1> <span class="sofadi-one-regular"> ODS ACTIONS </span></h1>
                        </div>
                        <div class="mt-3 d-flex justify-content-center sofadi-one-regular">
                            <h5> <span> <i class="fas fa-user"></i> connected : {{session_username}} </span></h5>
                        </div>
                        <div class="card-header mt-5 mb-1 bg-white"> 
                            <ul class="nav nav-tabs card-header-tabs bg-white">
                                <li v-if="session_show_display=='true'" class="nav-item"><button class="nav-link active" id="display-tab" data-bs-toggle="tab" data-bs-target="#display" type="button" role="tab" aria-controls="display" aria-selected="true"><strong>Display metadata from ODS</strong></button></li>
                                <li v-if="session_show_create_update=='true'"  class="nav-item"><button class="nav-link" id="create-update-tab" data-bs-toggle="tab" data-bs-target="#create-update" type="button" role="tab" aria-controls="create-update" aria-selected="false"><strong>Send metadata to ODS</strong></button></li>
                                <li v-if="session_show_send_file=='true'" class="nav-item"> <button class="nav-link" id="send-files-tab" data-bs-toggle="tab" data-bs-target="#send-files" type="button" role="tab" aria-controls="send-files" aria-selected="false"><strong>Send files to ODS</strong></button></li>
                                <!--v-if="session_show_jobnumbers_management=='true'"  <li class="nav-item"> <button class="nav-link" id="jobmanagement" data-bs-toggle="tab" data-bs-target="#jobmanagement" type="button" role="tab" aria-controls="send-files" aria-selected="false"><strong>Job Numbers Management</strong></button></li>-->
                                <li v-if="session_show_parameters=='true'"  class="nav-item"> <button class="nav-link" id="parameters-tab" data-bs-toggle="tab" data-bs-target="#parameters" type="button" role="tab" aria-controls="parameters" aria-selected="false"><strong>Parameters</strong></button></li>
                            </ul>
                        </div>
                        
                        <!-- <div class="card-body " style="margin-top: 1px;margin-left:10px;"> -->
                        
                            <div class="tab-content">
                            
                                <!-- First Tab -->	
                                
                                <div v-if="session_show_display=='true'" class="tab-pane show active " style="margin: 10px auto;text-align: center;" id="display" role="tabpanel" aria-labelledby="display-tab" >
                                    <form class="form-inline" @submit.prevent>
                                        <textarea id="docsymbols" class="col-11" rows="7" style=""  placeholder="Paste the list of symbols here (new line separated)" name="docsymbols" v-model="docsymbols"></textarea>
                                        <button class="btn btn-primary col-2 btn btn-success" type="button"  id="toggleButton" style="margin: 10px auto;padding: 10px;" @click="displayMetaData(docsymbols);">Apply</button>
                                    </form>    
                                        <div id="displayProgress1" class="mt-3" v-if="displayProgress1">
                                            <div class="spinner-grow text-primary" role="status">
                                                <span class="visually-hidden">Loading...</span>
                                            </div>
                                            <div class="spinner-grow text-secondary" role="status">
                                                <span class="visually-hidden">Loading...</span>
                                            </div>
                                            <div class="spinner-grow text-success" role="status">
                                                <span class="visually-hidden">Loading...</span>
                                            </div>
                                            <div class="spinner-grow text-danger" role="status">
                                                <span class="visually-hidden">Loading...</span>
                                            </div>
                                            <div class="spinner-grow text-warning" role="status">
                                                <span class="visually-hidden">Loading...</span>
                                            </div>
                                            <div class="spinner-grow text-info" role="status">
                                                <span class="visually-hidden">Loading...</span>
                                            </div>
                                                <div class="spinner-grow text-light" role="status">
                                            <span class="visually-hidden">Loading...</span>
                                                </div>
                                            <div class="spinner-grow text-dark" role="status">
                                                <span class="visually-hidden">Loading...</span>
                                            </div>
                                        </div>
                                    <div class="col-11" style="height:400px;overflow:auto;margin: 20px auto;" v-if="displayResult">
                                       
                                        <table id="MyTable" class="table table-bordered table-responsive table-striped ">
                                            <thead class="table-light">
                                            <tr>
                                                <th scope="col">Document Symbol</th>
                                                <th scope="col">Agenda</th>
                                                <th scope="col">Session</th>
                                                <th scope="col">Distribution</th>
                                                <th scope="col">Area</th>
                                                <th scope="col">Subjects</th>
                                                <th scope="col">Job Number</th>
                                                <th scope="col">Title</th>
                                                <th scope="col">Publication Date</th>
                                                <th scope="col">Release Date</th>
                                            </tr>
                                            </thead>
                                            <tbody>

                                            <tr v-for="record in listOfRecordsDiplayMetaData" v-if="listOfRecordsDiplayMetaData.length>=1">
                                                <td>{{record[0]['symbol']}}</td>
                                                <td>{{record[0]['agendas']}}</td>
                                                <td>{{record[0]['sessions']}}</td>
                                                <td>{{record[0]['distribution']}}</td>
                                                <td>{{record[0]['area']}}</td>
                                                <td>{{record[0]['subjects']}}</td>
                                                <td>{{record[0]["job_numbers"]}}</td>
                                                <td>{{record[0]["title_en"]}}</td>
                                                <td>{{record[0]["publication_date"]}}</td>
                                                <td>{{record[0]["release_dates"]}}</td>
                                            </tr>


                                            </tbody>
                                        </table>
                                        <button class="btn btn-primary mb-2 mr-2 align-items-center" v-if="displayResult==true" type="button" @click="docsymbols='';displayResult=false;listOfRecordsDiplayMetaData=[];">Clear List</button>
                                        <button class="btn btn-success mb-2  ml-1 align-items-center" v-if="displayResult==true" type="button" @click="exportTableToCSV('MyTable')">Export to csv</button>
                                    </div>
                                
                                </div>
                                <!-- End first Tab -->	
                                    
                        
                                <!-- Second Tab -->	
                                <div v-if="session_show_create_update=='true'" class="tab-pane fade" style="margin: 10px auto;text-align: center;" id="create-update" role="tabpanel" aria-labelledby="create-update-tab" >
                                    <form class="form-inline" @submit.prevent>
                                        <textarea id="docsymbols1" rows="7" class="col-11" placeholder="Paste the list of symbols here (new line separated)" style="" name="docsymbols1" v-model="docsymbols1"></textarea>
                                        <button class="btn btn-primary col-2 btn btn-success" type="button"  style="margin: 10px auto;padding: 10px;" @click="displayResultCreateUpdate(docsymbols1);">Send</button>
                                    </form>
                                   <div id="displayProgress2" class="mt-3" v-if="displayProgress2">
                                            <div class="spinner-grow text-primary" role="status">
                                                <span class="visually-hidden">Loading...</span>
                                            </div>
                                            <div class="spinner-grow text-secondary" role="status">
                                                <span class="visually-hidden">Loading...</span>
                                            </div>
                                            <div class="spinner-grow text-success" role="status">
                                                <span class="visually-hidden">Loading...</span>
                                            </div>
                                            <div class="spinner-grow text-danger" role="status">
                                                <span class="visually-hidden">Loading...</span>
                                            </div>
                                            <div class="spinner-grow text-warning" role="status">
                                                <span class="visually-hidden">Loading...</span>
                                            </div>
                                            <div class="spinner-grow text-info" role="status">
                                                <span class="visually-hidden">Loading...</span>
                                            </div>
                                                <div class="spinner-grow text-light" role="status">
                                            <span class="visually-hidden">Loading...</span>
                                                </div>
                                            <div class="spinner-grow text-dark" role="status">
                                                <span class="visually-hidden">Loading...</span>
                                            </div>
                                        </div>
                                    <div class="table-responsive col-11" style="height:400px;overflow:auto;margin: 20px auto;" v-if="displayResult1">
                                       
                                        <table id="MyTable1" class="table table-striped">
                                            <thead class="table-light">
                                                <tr>
                                                    <th>Document Symbol</th>
                                                    <th>Result</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                
                                                <tr v-for="record in listOfResult1">
                                                    <td>{{record["docsymbol"]}}</td>
                                                    <td>{{record["text"]}}</td>
                                                </tr>
                                            </tbody>
                                        </table>
                                        
                                    </div>
                                    
                                    <button type="submit" class="btn btn-primary mr-2 align-items-center" v-if="displayResult1==true" @click="docsymbols1='';displayResult1=false;listOfResult1=[];">Clear List</button>
                                    <button type="submit" class="btn btn-success ml-1 align-items-center" v-if="displayResult1==true" type="button" @click="exportTableToCSV('MyTable1')">Export to csv</button>
                                    
                                
                                </div>
                                <!-- End Second Tab -->	
                                
                            
                                <!-- Third Tab -->	
                                <div v-if="session_show_send_file=='true'" class="tab-pane fade" style="margin: 10px auto;text-align: center;" id="send-files" role="tabpanel" aria-labelledby="create-update-tab" >
                                    <form class="form-inline" @submit.prevent>
                                        <textarea class="col-11" rows="7" placeholder="Paste the list of symbols here (new line separated)" style="" name="docsymbols2" v-model="docsymbols2"></textarea>
                                        <button class="btn btn-primary col-2 btn btn-success" type="button"  style="margin: 10px auto;padding: 10px;" v-if="displayResult2==false"  @click="displayResultSendFile(docsymbols2)">Send</button> 
                                    </form>
                                    <div id="displayProgress3" class="mt-3" v-if="displayProgress3">
                                            <div class="spinner-grow text-primary" role="status">
                                                <span class="visually-hidden">Loading...</span>
                                            </div>
                                            <div class="spinner-grow text-secondary" role="status">
                                                <span class="visually-hidden">Loading...</span>
                                            </div>
                                            <div class="spinner-grow text-success" role="status">
                                                <span class="visually-hidden">Loading...</span>
                                            </div>
                                            <div class="spinner-grow text-danger" role="status">
                                                <span class="visually-hidden">Loading...</span>
                                            </div>
                                            <div class="spinner-grow text-warning" role="status">
                                                <span class="visually-hidden">Loading...</span>
                                            </div>
                                            <div class="spinner-grow text-info" role="status">
                                                <span class="visually-hidden">Loading...</span>
                                            </div>
                                                <div class="spinner-grow text-light" role="status">
                                            <span class="visually-hidden">Loading...</span>
                                                </div>
                                            <div class="spinner-grow text-dark" role="status">
                                                <span class="visually-hidden">Loading...</span>
                                            </div>
                                        </div>
                                    <div class="table-responsive col-11 shadow" style="height:400px;overflow:auto;margin: 20px auto;" v-if="displayResult2">
                                
                                        <table style="height:400px;overflow:auto;margin: 20px auto;" id="MyTable2" class="table">
                                            <thead class="table-light table-striped">
                                                <tr>
                                                    <th>Filename </th>
                                                    <th>Document symbol</th>
                                                    <th>Language</th>
                                                    <th>Jobnumber</th>
                                                    <th>Result</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                               
                                                    <tr v-for="record in listOfResult2">
                                                        <td>
                                                            {{record["filename"]}}
                                                        </td> 
                                                        <td>
                                                            {{record["docsymbol"]}}
                                                        </td>
                                                        <td>
                                                         {{record["language"]}}
                                                        </td>
                                                        <td>
                                                         {{record["jobnumber"]}}
                                                        </td>
                                                        <td>
                                                            {{record["result"]}}
                                                        </td>
                                                    </tr> 
                                             
                                            </tbody>
                                        </table>
                                    </div>

                                        <button type="submit" class="btn btn-primary mr-2 align-items-center" v-if="displayResult2==true" @click="docsymbols2='';displayResult2=false;listOfResult2=[];">Clear List</button>
                                        <button type="submit" class="btn btn-success ml-1 align-items-center" v-if="displayResult2==true" type="button" @click="exportTableToCSV('MyTable2')">Export to csv</button>
                                    
                                
                                </div>
                                <!-- End Third Tab -->	

                                  
                                <!-- Parameters Tab -->	
                                    <div v-if="session_show_parameters=='true'" class="tab-pane fade show" id="parameters" role="tabpanel">

                                    <div class="accordion" id="accordionExample">
                                        <div class="accordion-item" id="sites">
                                                <h2 class="accordion-header" id="headingOne0">
                                                    <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne0" aria-expanded="true" aria-controls="collapseOne0">
                                                        <strong>Sites Management</strong>
                                                    </button>
                                                </h2>
                                                <div id="collapseOne0" class="accordion-collapse collapse " aria-labelledby="headingOne0" data-bs-parent="#accordionExample">
                                                <div class="accordion-body">
                                                    <strong>Please fill the fields below.</strong>
                                                    <hr>
                                                    <form>
                            
                                                        <div class="mb-3">
                                                            <label for="" class="form-label"><strong>Code Site</strong></label>
                                                            <input type="text" class="form-control" id="code_site" value="code_site" aria-describedby="code_site_help" v-model="code_site">
                                                        </div>
                                                        <div class="mb-3">
                                                            <label for="" class="form-label"><strong>Label Site</strong></label>
                                                            <input type="text" class="form-control" id="label_site" value="label_site" aria-describedby="label_site" v-model="label_site">
                                                        </div>
                                                        <div class="mb-3">
                                                            <label for="" class="form-label"><strong>Prefix Site</strong></label>
                                                            <input type="text" class="form-control" id="prefix_site" value="prefix_site" aria-describedby="prefix_site" v-model="prefix_site">
                                                        </div>                                                                                                                
                                                        <hr>
                                                        <div class="mt-2">
                                                            <button type="button" class="btn btn-primary" @click="addSite()">Create</button>
                                                            <!-- <button type="button" class="btn btn-secondary" @click="">Edit</button> -->
                                                        <div>
                                                    </form>
        
                                                </div>
                                                </div>
                                            </div>
                                            <div class="accordion-item" id="users">
                                                <h2 class="accordion-header" id="headingOne">
                                                <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
                                                    <strong>Users Management</strong>
                                                </button>
                                                </h2>
                                                <div id="collapseOne" class="accordion-collapse collapse" aria-labelledby="headingOne" data-bs-parent="#accordionExample">
                                                <div class="accordion-body">
                                                    <strong>Please fill the fields below.</strong>
                                                    <hr>
                                                    <form>
                                                        <div class="mb-3">
                                                            <label for="" class="form-label"><strong>Site</strong></label>
                                                            <select id="site" class="form-select" v-model="code_site">
                                                                <option v-for="my_site in site">{{my_site}}</option>
                                                            </select>
                                                        </div>
                                                        <div class="mb-3">
                                                            <label for="" class="form-label"><strong>Email</strong></label>
                                                            <input type="email" class="form-control" id="email" value="email" aria-describedby="emailHelp" v-model="email">
                                                        </div>
                                                        <div class="mb-3">
                                                            <label for="" class="form-label"><strong>Password</strong></label>
                                                            <input type="password" class="form-control" id="password" value="password" v-model="password">
                                                        </div>
                                                        <div class="mb-3">
                                                            <label for="" class="form-label"><strong>Select the tab(s) to display</strong></label>
                                                            <div class="form-check form-check">
                                                                <input class="form-check-input" type="checkbox" id="show_display" value="show_display" v-model="show_display">
                                                                <label class="form-check-label" for="inlineCheckbox1">Show Display metadata</label>
                                                            </div>
                                                            <div class="form-check form-check">
                                                                <input class="form-check-input" type="checkbox" id="show_create_update" value="show_create_update" v-model="show_create_update">
                                                                <label class="form-check-label" for="inlineCheckbox2"> Show Create/ Update metadata</label>
                                                            </div>
                                                            <div class="form-check form-check">
                                                                <input class="form-check-input" type="checkbox" id="show_send_file" value="show_send_file" v-model="show_send_file">
                                                                <label class="form-check-label" for="inlineCheckbox2">Show Send files to ODS </label>
                                                            </div>
                                                            <div class="form-check form-check">
                                                                <input class="form-check-input" type="checkbox" id="show_jobnumbers_management" value="show_jobnumbers_management" v-model="show_jobnumbers_management">
                                                                <label class="form-check-label" for="inlineCheckbox2">Show Job numbers management</label>
                                                            </div>
                                                            <div class="form-check form-check">
                                                                <input class="form-check-input" type="checkbox" id="show_parameters" value="show_parameters" v-model="show_parameters">
                                                                <label class="form-check-label" for="inlineCheckbox2">Show Parameters</label>
                                                            </div>
                                                        </div>
                                                        <hr>
                                                        <div class="mt-2">
                                                            <button type="button" class="btn btn-primary" @click="addUser()">Create</button>
                                                            <!-- <button type="button" class="btn btn-secondary" @click="alert('edit')">Edit</button> -->
                                                        <div>
                                                    </form>
        
                                                </div>
                                                </div>
                                            </div>
                                            <div class="accordion-item">
                                                <h2 class="accordion-header" id="headingThree">
                                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseThree" aria-expanded="false" aria-controls="collapseThree">
                                                    <strong>Logs</strong>
                                                </button>
                                                </h2>
                                                <div id="collapseThree" class="accordion-collapse collapse" aria-labelledby="headingThree" data-bs-parent="#accordionExample">
                                                <div class="accordion-body">
                                                    <button type="submit" class="btn btn-success ml-1 align-items-center" type="button" @click="exportTableToCSV('listlogs')">Export all the logs in csv</button>
                                                    <div class="shadow" style="height:400px;overflow:auto;margin: 20px auto;">
                                                        <table class="table table-striped tableau" id="listlogs">
                                                        <thead>
                                                            <tr>
                                                            <th scope="col">User</th>
                                                            <th scope="col">Action</th>
                                                            <th scope="col">Date</th>
                                                            </tr>
                                                        </thead>
                                                        <tbody>
                                                            <tr v-for="field in listOfLogs">
                                                                <th scope="row"> {{field.user}} </th>
                                                                <td>{{field.action}}</td>
                                                                <td>{{field.date.$date}}</td>
                                                            </tr>
                                                        </tbody>
                                                        </table>       
                                                    </div>

                                                </div>
                                                </div>
                                            </div>
                                        </div>

                                        
                                    </div>
                                <!-- End parameters Tab -->	
                            
                            </div>
                        
                        
                        
                        
                        <!-- </div> -->
                        
                    </div>
                <!-- <script src="assets/bootstrap/js/bootstrap.min.js"></script>-->
                    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-C6RzsynM9kWDrMNeT87bh95OGNyZPhcTNXj1NW7RuBCsyN/o0jlpcV8Qyq46cDfL" crossorigin="anonymous"></script>
                    <script>
                    document.getElementById('toggleButton').addEventListener('click', function() {
                    // Toggle the 'hidden' class on the table
                    var table = document.getElementById('myTable');
                    if (table.classList.contains('hidden')) {
                        table.classList.remove('hidden');
                    } else {
                        table.classList.add('hidden');
                    }
                    });
                    </script>
             `,
created:async function(){
    this.loadLogs()
    this.loadSites()
    },
props: ['session_username','session_show_display','session_show_create_update','session_show_send_file','session_show_jobnumbers_management','session_show_parameters'],
data: function () {
    return {
        // Management of the display of the # divs
        displayResult:false,
        displayResult1:false,
        displayResult2:false,
        listOfRecordsDiplayMetaData:[],
        listOfResult1:[],
        listOfResult2:[],
        docsymbols:"",
        docsymbols1:"",
        docsymbols2:"",
        displayProgress1:false,
        displayProgress2:false,
        displayProgress3:false,
        displayErrorTab1:[],
        site:[],
        email:"",
        password:"",
        show_display:false,
        show_create_update:false,
        show_send_file:false,
        show_jobnumbers_management:false,
        show_parameters:false,
        creation_date:"",
        listOfLogs:[],
        code_site:"",
        label_site:"",
        prefix_site:"",
    }
    },
        
    methods:{

        async loadLogs(){
        // loading the logs
        const my_response = await fetch("./display_logs",{
            "method":"GET",
            });
        const my_data = await my_response.json();
        my_data.forEach(element => {
            this.listOfLogs.push(element)
        });
        },
        async loadSites(){

        // loading the sites
        const my_response1 = await fetch("./get_sites",{
            "method":"GET",
            });
        const my_data1 = await my_response1.json();
        my_data1.forEach(element => {
            this.site.push(element["code_site"])
        });
        },
        async displayMetaData(){

        // just in case
        this.displayResult=false;

        // display Progress bar
        this.displayProgress1=true

        // Just to refresh the UI
        this.listOfRecordsDiplayMetaData=[]
        
        let dataset = new FormData()
        let cleanedDocSymbols = this.docsymbols.toUpperCase(); 
        dataset.append('docsymbols',cleanedDocSymbols)
    
        // loading all the data
        const my_response = await fetch("./loading_symbol",{
            "method":"POST",
            "body":dataset
            });
            
        const my_data = await my_response.json()

        // loading data
        try {     
            my_data.forEach(element => {

                // check the length of the data array to see if we found the information
                
                // use case 1 : we found the data
                if (element["body"]["data"].length!==0) 
                    this.listOfRecordsDiplayMetaData.push(element["body"]["data"])

                // use case 2 : we did not find the data
                if (element["body"]["data"].length===0) {
                    // creation of the object
                    this.listOfRecordsDiplayMetaData.push(
                        [{
                            symbol:element["docsymbol"],
                            agendas:"Not found",
                            sessions:"Not found",
                            distribution:"Not found",
                            area:"Not found",
                            subjects:"Not found",
                            job_numbers:"Not found",
                            title_en:"Not found",
                            publication_date:"Not found",
                            agenpublication_datedas:"Not found",
                            release_dates:"Not found"
                        }])
                }

            })

            //     let docsymbol=element[1]
            //     // console.log(element[0])


            //         if (data[0]["body"]["data"][0].length!==0)  
            //             {  
            //             this.listOfRecordsDiplayMetaData.push(data[0]["body"]["data"][0])
            //             }

            //         //implement case where nothing is returned , docsymbol does not exits
                    // if (element["body"]["data"].length==0)  
                    // })
                } 
        catch (error) {
            // remove Progress bar
            this.displayProgress1=false
        }
        finally{
            // remove Progress bar
            this.displayProgress1=false
        }

        // display Results
        if (this.listOfRecordsDiplayMetaData.length>=1)
            this.displayResult=true;

        },
              
        async displayResultCreateUpdate(){

            // just in case
            this.displayResult1=false;

            // display Progress bar
            this.displayProgress2=true

            // Just to refresh the UI
            this.listOfResult1=[]
            


            this.docsymbols1 = this.docsymbols1
                .split('\n')
                .filter(line => line.trim() !== '')
                .join('\n');

            let dataset = new FormData()
            dataset.append('docsymbols1',this.docsymbols1)

        
            // loading all the data
            const my_response = await fetch("./create_metadata_ods",{
                "method":"POST",
                "body":dataset
                });
            
        
           
            const my_data = await my_response.json();

            try {        
                my_data.forEach(elements => {
                    //console.log(typeof(elements))
                    this.listOfResult1=this.listOfResult1.concat(elements)
                })
                
            } catch (error) {
                //alert(error)
            }
            finally{
                // display Progress bar
                this.displayProgress2=false
            }

            //this.listOfResult1.push(my_data)

    
            // hide Progress bar
            //this.displayProgress2=false

            // display the results of the query
            this.displayResult1=true;
            
            },

            async displayResultSendFile(){

                // just in case
                this.displayResult2=false;

                // display Progress bar
                this.displayProgress3=true
                
                this.docsymbols2 = this.docsymbols2
                    .split('\n')
                    .filter(line => line.trim() !== '')
                    .join('\n');


                let dataset = new FormData()
                dataset.append('docsymbols2',this.docsymbols2)
            
                // loading all the data
                const my_response = await fetch("./exporttoodswithfile",{
                    "method":"POST",
                    "body":dataset
                    });
                                   
                const my_data = await my_response.json()
                // console.log(my_data)
                // loading data
                try {        
                    my_data.forEach(elements => {
                        //console.log(typeof(elements))
                        this.listOfResult2=this.listOfResult2.concat(elements)
                    })
                    
                } catch (error) {
                    alert(error)
                }
                finally{
                    // display Progress bar
                    this.displayProgress3=false
                }

                if (this.listOfResult2.length!=0){
                    this.displayResult2=true;
                    }
            },
        checkInput(){
            // init the variable
            let result=true;

            // check the checkboxes
            if (this.show_display == false && this.show_create_update == false && this.show_send_file == false && this.show_jobnumbers_management == false && this.show_parameters == false)
                result=false

            // check the inputs
            if (this.site =="") result=false
            if (this.email =="") result=false
            if (this.password =="") result=false

            // check valid email
            const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (regex.test(this.email)==false) result=false

            // send the result of the validation
            return result
        },
        checkInput1(){
            // init the variable
            let result=true;

            // check the inputs
            if (this.code_sitesite =="" || this.code_site.length!==3) result=false
            if (this.label_site =="") result=false
            if (this.prefix_site =="" || this.prefix_site.length!==2) result=false

            // send the result of the validation
            return result
        },
        async addUser(){

            let my_site= document.getElementById("site")
            let my_value=my_site.value
            
            let result=this.checkInput()

            if (result==true)
                {
                    // define the dataset
                    let dataset = new FormData()

                    // add the fields to the dataset
                    dataset.append('site',my_value)
                    dataset.append('email',this.email)
                    dataset.append('password',this.password)
                    dataset.append('show_display',this.show_display)
                    dataset.append('show_create_update',this.show_create_update)
                    dataset.append('show_send_file',this.show_send_file)
                    dataset.append('show_jobnumbers_management',this.show_jobnumbers_management)
                    dataset.append('show_parameters',this.show_parameters)

                    // loading all the data
                    const my_response = await fetch("./add_user",{
                        "method":"POST",
                        "body":dataset
                        });
                                    
                    const my_data = await my_response.json()
                    try 
                        {        
                        alert(my_data.message)
                        }
                        
                    catch (error) {
                        alert(error)
                    }
                }
            else{
                alert("please check the inputs!!!!") 
            }        
        },
        async addSite(){
            
            let result=this.checkInput1()

            if (result==true)
                {
                    // define the dataset
                    let dataset = new FormData()

                    // add the fields to the dataset
                    dataset.append('code_site',this.code_site.toUpperCase())
                    dataset.append('label_site',this.label_site)
                    dataset.append('prefix_site',this.prefix_site.toUpperCase())

                    // loading all the data
                    const my_response = await fetch("./add_site",{
                        "method":"POST",
                        "body":dataset
                        });
                                    
                    const my_data = await my_response.json()
                    try 
                        {        
                        alert(my_data.message)
                        }
                        
                    catch (error) {
                        alert(error)
                    }
                }
            else{
                alert("please check the inputs!!!!") 
            }
            window.location.reload();      
        },
        downloadCSV(csv) {
                    let csvFile;
                    let downloadLink;
                
                    // CSV file
                    csvFile = new Blob([csv], {type: "text/csv"});
                
                    // Download link
                    downloadLink = document.createElement("a");
                
                    // File name
                    downloadLink.download = "export.csv";
                
                    // Create a link to the file
                    downloadLink.href = window.URL.createObjectURL(csvFile);
                
                    // Hide the link
                    downloadLink.style.display = "none";
                
                    // Add the link to the DOM
                    document.body.appendChild(downloadLink);
                
                    // Click the link
                    downloadLink.click();
        },
        exportTableToCSV(tableName) {
            let csv = [];
            let rows = document.getElementById(tableName).rows;
        
            for (let i = 0; i < rows.length; i++) {
                let row = [], cols = rows[i].querySelectorAll("td, th");
        
                for (let j = 0; j < cols.length; j++) 
                    row.push(cols[j].innerText);
        
                csv.push(row.join(","));
            }
            // Download CSV file
            this.downloadCSV(csv.join("\n"));
        },
        exportExcel(tableName) {
            const uri = 'data:application/vnd.ms-excel;base64,',
            template = '<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40"><head><!--[if gte mso 9]><xml><x:ExcelWorkbook><x:ExcelWorksheets><x:ExcelWorksheet><x:Name>{worksheet}</x:Name><x:WorksheetOptions><x:DisplayGridlines/></x:WorksheetOptions></x:ExcelWorksheet></x:ExcelWorksheets></x:ExcelWorkbook></xml><![endif]--></head><body><table>{table}</table></body></html>',
            base64 = function(s) {
            return window.btoa(unescape(encodeURIComponent(s)))
            },
            format = function(s, c) {
            return s.replace(/{(\w+)}/g, function(m, p) {
            return c[p];
            })
            }
            var toExcel = document.getElementById(tableName).innerHTML;
            var ctx = {
            worksheet: name || '',
            table: toExcel
            };
            var link = document.createElement("a");
            link.download = "export.xls";
            link.href = uri + base64(format(template, ctx))
            link.click();
        },
    },
})
  
let app_ods = new Vue({
  el: '#ods_component'
})