Vue.component('ods', {
    template: `
                <div class="card mt-5 ml-5" style="margin:auto;height:700px;width:1150px;">
                        <div class="mt-3 d-flex justify-content-center">
                            <h1> ODS ACTIONS </h1> 
                        </div>
                        <div class="card-header mt-5 mb-1 bg-white">
                            <ul class="nav nav-tabs card-header-tabs bg-white">
                                <li class="nav-item"><button class="nav-link active" id="display-tab" data-bs-toggle="tab" data-bs-target="#display" type="button" role="tab" aria-controls="display" aria-selected="true"><strong>Display metadata from ODS</strong></button></li>
                                <li class="nav-item"><button class="nav-link" id="create-update-tab" data-bs-toggle="tab" data-bs-target="#create-update" type="button" role="tab" aria-controls="create-update" aria-selected="false"><strong>Create/Update existing metadata to ODS</strong></button></li>
                                <li class="nav-item"> <button class="nav-link" id="send-files-tab" data-bs-toggle="tab" data-bs-target="#send-files" type="button" role="tab" aria-controls="send-files" aria-selected="false"><strong>Send files to ODS</strong></button></li>
                                <li class="nav-item"> <button class="nav-link" id="jobmanagement" data-bs-toggle="tab" data-bs-target="#jobmanagement" type="button" role="tab" aria-controls="send-files" aria-selected="false"><strong>Job Numbers Management</strong></button></li>
                                <li class="nav-item"> <button class="nav-link" id="parameters-tab" data-bs-toggle="tab" data-bs-target="#parameters" type="button" role="tab" aria-controls="parameters" aria-selected="false"><strong>Parameters</strong></button></li>
                            </ul>
                        </div>
                        
                        <!-- <div class="card-body " style="margin-top: 1px;margin-left:10px;"> -->
                        
                            <div class="tab-content">
                            
                                <!-- First Tab -->	
                                <div class="tab-pane show active " style="margin: 10px auto;text-align: center;" id="display" role="tabpanel" aria-labelledby="display-tab" >
                                    <form class="form-inline" @submit.prevent>
                                        <textarea id="docsymbols" class="col-11" style="margin:20px auto;border-radius:10px;color:#c8c7c7; border-color: #A8A8A8;border-style:1 rem solid;border-width: 2px;"  placeholder="Paste the list of symbols here (space separated)" name="docsymbols" v-model="docsymbols"></textarea>
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
                                    <div class="table-responsive col-11" style="margin: 20px auto;" v-if="displayResult">
                                       
                                        <table id="MyTable" class="table table-bordered table-responsive ">
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
                                        <button class="btn btn-success mb-2  ml-1 align-items-center" v-if="displayResult==true" type="button" @click="exportExcel('MyTable')">Export to csv</button>
                                    </div>
                                
                                </div>
                                <!-- End first Tab -->	
                                    
                        
                                <!-- Second Tab -->	
                                <div class="tab-pane fade" style="margin: 10px auto;text-align: center;" id="create-update" role="tabpanel" aria-labelledby="create-update-tab" >
                                    <form class="form-inline" @submit.prevent>
                                        <textarea id="docsymbols1" class="col-11" placeholder="Paste the list of symbols here (space separated)" style="margin:20px auto;border-radius:10px;color:#c8c7c7; border-color: #A8A8A8;border-style:1 rem solid;border-width: 2px;" name="docsymbols1" v-model="docsymbols1"></textarea>
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
                                    <div class="table-responsive col-11" style="margin: 20px auto;" v-if="displayResult1">
                                       
                                        <table id="MyTable1" class="table">
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
                                    <button type="submit" class="btn btn-success ml-1 align-items-center" v-if="displayResult1==true" type="button" @click="exportExcel('MyTable1')">Export to csv</button>
                                    
                                
                                </div>
                                <!-- End Second Tab -->	
                                
                            
                                <!-- Third Tab -->	
                                <div class="tab-pane fade" style="margin: 10px auto;text-align: center;" id="send-files" role="tabpanel" aria-labelledby="create-update-tab" >
                                    <form class="form-inline" @submit.prevent>
                                        <textarea class="col-11" placeholder="Paste the list of symbols here (space separated)" style="margin:20px auto;border-radius:10px;color:#c8c7c7; border-color: #A8A8A8;border-style:1 rem solid;border-width: 2px;" name="docsymbols2" v-model="docsymbols2"></textarea>
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
                                    <div class="table-responsive col-11 shadow" style="margin: 20px auto;" v-if="displayResult2">
                                
                                        <table id="MyTable2" class="table">
                                            <thead class="table-light">
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
                                        <button type="submit" class="btn btn-success ml-1 align-items-center" v-if="displayResult2==true" type="button" @click="exportExcel('MyTable2')">Export to csv</button>
                                    
                                
                                </div>
                                <!-- End Third Tab -->	
                                <!-- Parameters Tab -->	
                                    <div class="tab-pane fade show" id="parameters" role="tabpanel">

                                        <div class="accordion" id="accordionExample">
                                            <div class="accordion-item" id="users">
                                                <h2 class="accordion-header" id="headingOne">
                                                <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
                                                    <strong>Users Management</strong>
                                                </button>
                                                </h2>
                                                <div id="collapseOne" class="accordion-collapse collapse show" aria-labelledby="headingOne" data-bs-parent="#accordionExample">
                                                <div class="accordion-body">
                                                    <strong>Please fill the fields below.</strong>
                                                    <hr>
                                                    <form>
                                                        <select class="form-select" aria-label="Default select example">
                                                            <option selected>Please select the site</option>
                                                            <option value="1">NYC</option>
                                                            <option value="2">GEN</option>
                                                        </select>
                                                        <div class="mb-3">
                                                            <label for="exampleInputEmail1" class="form-label">Email address</label>
                                                            <input type="email" class="form-control" id="exampleInputEmail1" aria-describedby="emailHelp">
                                                            <div id="emailHelp" class="form-text">We'll never share your email with anyone else.</div>
                                                        </div>
                                                        <div class="mb-3">
                                                            <label for="exampleInputPassword1" class="form-label">Password</label>
                                                            <input type="password" class="form-control" id="exampleInputPassword1">
                                                        </div>
                                                        <div class="form-check form-check-inline">
                                                            <input class="form-check-input" type="checkbox" id="inlineCheckbox1" value="option1">
                                                            <label class="form-check-label" for="inlineCheckbox1">Display metadata access</label>
                                                        </div>
                                                        <div class="form-check form-check-inline">
                                                            <input class="form-check-input" type="checkbox" id="inlineCheckbox2" value="option2">
                                                            <label class="form-check-label" for="inlineCheckbox2">Create/ Update metadata access</label>
                                                        </div>
                                                        <div class="form-check form-check-inline">
                                                            <input class="form-check-input" type="checkbox" id="inlineCheckbox2" value="option2">
                                                            <label class="form-check-label" for="inlineCheckbox2">Send files to ODS access</label>
                                                        </div>
                                                        <div class="form-check form-check-inline">
                                                            <input class="form-check-input" type="checkbox" id="inlineCheckbox2" value="option2">
                                                            <label class="form-check-label" for="inlineCheckbox2">Job numbers management access</label>
                                                        </div>
                                                        <div class="form-check form-check-inline">
                                                            <input class="form-check-input" type="checkbox" id="inlineCheckbox2" value="option2">
                                                            <label class="form-check-label" for="inlineCheckbox2">Parameters</label>
                                                        </div>
                                                        <div class="mt-2">
                                                            <button type="submit" class="btn btn-primary">Create the user</button>
                                                        <div>
                                                    </form>
        
                                                </div>
                                                </div>
                                            </div>
                                            <div class="accordion-item">
                                                <h2 class="accordion-header" id="headingTwo">
                                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseTwo" aria-expanded="false" aria-controls="collapseTwo">
                                                   <strong>Job numbers Management </strong>
                                                </button>
                                                </h2>
                                                <div id="collapseTwo" class="accordion-collapse collapse" aria-labelledby="headingTwo" data-bs-parent="#accordionExample">
                                                <div class="accordion-body">
                                                    <strong>This is the second item's accordion body.</strong> It is hidden by default, until the collapse plugin adds the appropriate classes that we use to style each element. These classes control the overall appearance, as well as the showing and hiding via CSS transitions. You can modify any of this with custom CSS or overriding our default variables. It's also worth noting that just about any HTML can go within the <code>.accordion-body</code>, though the transition does limit overflow.
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
                                                    <strong>This is the third item's accordion body.</strong> It is hidden by default, until the collapse plugin adds the appropriate classes that we use to style each element. These classes control the overall appearance, as well as the showing and hiding via CSS transitions. You can modify any of this with custom CSS or overriding our default variables. It's also worth noting that just about any HTML can go within the <code>.accordion-body</code>, though the transition does limit overflow.
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
created: async function(){
    },

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
    }
    },
        
    methods:{

        async displayMetaData(){

        // just in case
        this.displayResult=false;

        // display Progress bar
        this.displayProgress1=true

        // Just to refresh the UI
        this.listOfRecordsDiplayMetaData=[]
        
        let dataset = new FormData()
        dataset.append('docsymbols',this.docsymbols)
    
        // loading all the data
        const my_response = await fetch("/loading_symbol",{
            "method":"POST",
            "body":dataset
            });
            
        const my_data = await my_response.json();
        
        // loading data
        try {        
            my_data.forEach(element => {
            if (element["body"]["data"].length!==0)    
                this.listOfRecordsDiplayMetaData.push(element["body"]["data"])
            else {
                alert("No data found for this docsymbol, maybe it is not created!!!!")
            }
            })
            
        } catch (error) {
            console.log(error)
        }
        finally{
            // display Progress bar
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
            
            let dataset = new FormData()
            dataset.append('docsymbols1',this.docsymbols1)

        
            // loading all the data
            const my_response = await fetch("/create_metadata_ods",{
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
                alert(error)
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
                
                let dataset = new FormData()
                dataset.append('docsymbols2',this.docsymbols2)
            
                // loading all the data
                const my_response = await fetch("exporttoodswithfile",{
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