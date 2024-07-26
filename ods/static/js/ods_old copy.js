Vue.component('ods', {
    template: `
            <div>
                <div class="h-100 d-flex align-items-center justify-content-center mt-3">
                    <h1> ODS ACTIONS </h1>
                    <hr>
                </div>
                <div class="wrapper">
                    <div class="tabs">
                            <div class="tab">
                                <input type="radio" name="css-tabs" id="tab-1" checked class="tab-switch">
                                <label for="tab-1" class="tab-label"><strong>Display metadata from ODS  ....</strong></label>
                                <div class="tab-content">
                                    <h5>
                                       <strong>This feature provides some Metadata for a specific Document Symbol. The user has to copy and paste the document symbol (or a list of document symbols) and click on the display result(s) button.</strong>
                                    </h5>
                                    <!-- Form managing the display -->
                                    <form class="form-inline" @submit.prevent>
                                        <div class="form-group mb-2">
                                            <label for="inputDocSymbol1" class="sr-only">Docsymbol</label>
                                            <textarea type="text" class="form-control"  placeholder=" Insert / Paste docsymbol(s)" id="docsymbols" name="docsymbols" v-model="docsymbols"></textarea>
                                        </div>
                                        
                                        <button class="btn btn-warning mb-2 ml-2" v-if="displayResult1==true" type="button" @click="docsymbols='';displayResult1=false;listOfRecordsDiplayMetaData=[];">Clear List</button>
                                        <button class="btn btn-success mb-2 ml-2" v-if="displayResult1==true" type="button" @click="exportExcel('displayResult1')">Export to csv</button>
                                    </form>
                                    <div v-if="displayResult1">
                                        <table id="displayResult1" class="table table-bordered table-responsive ">
                                            <thead>
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

                                            <tr v-for="record in listOfRecordsDiplayMetaData">
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
                                    </div>
                                </div>

                            </div>
                            <div class="tab">
                                <input type="radio" name="css-tabs" id="tab-2" class="tab-switch">
                                <label for="tab-2" class="tab-label"><strong>Create metadata in ODS .... </strong></label>
                                <div class="tab-content">
                                    <h5> <strong>
                                    The create metadata will create some metadata in ODS for a specific Document Symbol. Some parameters are needed for this process        
                                    </strong></h5>
                                    <form @submit.prevent>
                                         <div class="row">
                                            <!-- Field -->

                                            <div class="col">
                                                <input type="text" class="form-control" placeholder="Document symbol" name="my_symbol" id="my_symbol" v-model="my_symbol">
                                            </div>
                                            
                                            <div class="col">
                                                <input type="text" class="form-control" placeholder="Area" name="my_area" id="my_area" v-model="my_area">
                                            </div>

                                            <div class="col">
                                                <input type="text" class="form-control" placeholder="Distribution" name="my_distribution" id="my_distribution" v-model="my_distribution">
                                            </div>     
                                            
                                            <div class="col">
                                                <input type="text" class="form-control" placeholder="Title" name="my_title" id="my_title" v-model="my_title">
                                            </div>  

                                            <div class="col">
                                                <input type="text" class="form-control" placeholder="Language" name="my_language" id="my_language" v-model="my_language">
                                            </div>  

                                            <!-- Button -->
                                            <div class="col">
                                                <button class="btn btn-primary  btn-success" type="button"  id="createMetadata" @click="createMetadata()">Create Metadata</button>
                                            </div>

                                         </div>
     
                                     </form>

                                </div>
                            </div>
                            <div class="tab">
                                <input type="radio" name="css-tabs" id="tab-3" class="tab-switch">
                                <label for="tab-3" class="tab-label"><strong>Update metadata in ODS .... </strong></label>
                                <div class="tab-content">
                                   <h5> <strong>
                                   This feature update one record (using the docsymbol) with a specific value for the field targeted. Some parameters are needed for this process.
                                   </strong></h5>
                                   <div class="accordion" id="accordionExample">
                                   <div class="accordion-item">
                                   <h2 class="accordion-header" id="headingOne">
                                     <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
                                     <strong> Update One File </strong>
                                     </button>
                                   </h2>
                                   <div id="collapseOne" class="accordion-collapse collapse" aria-labelledby="headingOne" data-bs-parent="#accordionExample">
                                     <div class="accordion-body">
                                       
                                     <form @submit.prevent>
                                         <div class="row">
                                         <div class="col">
                                             <input type="text" class="form-control" placeholder="Document symbol" name="docsymbol2" id="docsymbol2" v-model="docsymbol2">
                                         </div>
                                         <div class="col">
                                             <select name="field2" id="field2" class="form-select" v-model="field2" placeholder="Select field to update">
                                                 <optgroup label="Select the Field to update">
                                                     <option value="symbols" selected="selected">Symbols</option>
                                                     <option value="publicationDate">Publication Date</option>
                                                     <option value="releaseDate">Release Date</option>
                                                     <option value="title">Title</option>
                                                     <option value="tcodes">Tcodes</option>
                                                     <option value="area">Area</option>
                                                     <option value="distribution">Distribution</option>
                                                     <option value="agendas">Agendas</option>
                                                     <option value="sessions">Sessions</option>
                                                     <option value="fullText">Full Text</option>
                                                 </optgroup>
                                             </select>
                                         </div>
                                         <div class="col">
                                             <input type="text" class="form-control" placeholder="Field value" id="fieldvalue2" name="fieldvalue2" v-model="fieldvalue2">
                                         </div>
                                         <div class="col">
                                             <select name="language2" id="language2" class="form-select" v-model="language2">
                                                 <optgroup label="Select the language">
                                                     <option value="en" selected="selected">English</option>
                                                     <option value="fr">French</option>
                                                     <option value="es">Spanish</option>
                                                     <option value="ru">Russian</option>
                                                     <option value="ar">Arabic</option>
                                                     <option value="zh">Chinese</option>
                                                 </optgroup>
                                             </select>
                                         </div>
                                         <!-- Second option -->
                                         

                                         
                                         <div class="col">
                                             <button class="btn btn-primary  btn-success" type="button"  id="toggleButton4" @click="update_one_file_to_ods()">Update Metadata</button>
                                         </div>
                                         </div>
     
                                     </form>

                                     </div>
                                   </div>
                                 </div>
                                    <div class="accordion-item">
                                      <h2 class="accordion-header" id="headingOne1">
                                        <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne1" aria-expanded="true" aria-controls="collapseOne1">
                                        <strong> Update Multiple Files </strong>
                                        </button>
                                      </h2>
                                      <div id="collapseOne1" class="accordion-collapse collapse" aria-labelledby="headingOne" data-bs-parent="#accordionExample1">
                                        <div class="accordion-body">
                                          
                                            <form @submit.prevent>
                                                    <h5> For this feature, you need to prepare a csv file with <strong> 4 columns (without headers) </strong>:  
                                                        <ul>
                                                            <strong>
                                                                <li> First column : Document symbol </li>
                                                                <li> Second column : Field to update </li>
                                                                <li> Third column :  Value of the field </li>
                                                                <li> Fourth column : Language </li>
                                                            </strong>
                                                        </ul>
                                                        Copy / Paste the content of your file in the text area (below) then hit "Update Metadata" button
                                                    </h5>

                                                <div class="form-group mb-2">
                                                    <label for="inputDocSymbol0" class="sr-only">Docsymbol / Field to update / Value to update / Language </label>
                                                    <textarea type="text" class="form-control"  placeholder=" Docsymbol / Job number / Language / Path " id="data_send_multiple5" name="data_send_multiple5" v-model="data_send_multiple5"></textarea>
                                                </div>
                    
                                                <div class="col">
                                                    <button class="btn btn-primary  btn-success" type="button"  id="toggleButton5" @click="update_multiple_files_to_ods()">Update Metadata</button>
                                                </div>
        
                                            </form>

                                        </div>
                                      </div>
                                    </div>




                                  </div>
                                </div>
                            </div>
                            <div class="tab">
                                <input type="radio" name="css-tabs" id="tab-4" class="tab-switch">
                                <label for="tab-4" class="tab-label"><strong>Send files to ODS ..... </strong></label>
                                <div class="tab-content">
                                    <h5><strong>This feature send one file (for the one file feature) or multiple files (for the multiple files feature).
                                    Some parameters are needed for this process. </strong></h5>
                                    <div class="accordion" id="accordionExample">
                                    <div class="accordion-item">
                                      <h2 class="accordion-header" id="headingOne">
                                        <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
                                        <strong> Send One File </strong>
                                        </button>
                                      </h2>
                                      <div id="collapseOne" class="accordion-collapse collapse" aria-labelledby="headingOne" data-bs-parent="#accordionExample">
                                        <div class="accordion-body">
                                          
                                        <form @submit.prevent>
                                            <div class="row">
                                            <div class="col">
                                                <input type="text" class="form-control" placeholder="Document symbol" name="docsymbol4" id="docsymbol4" v-model="docsymbol4">
                                            </div>
                                            <div class="col">
                                                <input type="text" class="form-control" placeholder="Job number" name="jobnumber4" id="jobnumber4" v-model="jobnumber4">
                                            </div>
                                            <div class="col">
                                                <select name="language4" id="language4" class="form-select" v-model="language4">
                                                    <option value="en" selected="selected">English</option>
                                                    <option value="fr">French</option>
                                                    <option value="es">Spanish</option>
                                                    <option value="ru">Russian</option>
                                                    <option value="ar">Arabic</option>
                                                    <option value="zh">Chinese</option>
                                                </select>
                                            </div>
                                            <div class="col">
                                                <input type="text" class="form-control" placeholder="Path" id="path4" name="path4" v-model="path4">
                                            </div>
                                            
                                            <div class="col">
                                                <button class="btn btn-primary  btn-success" type="button"  id="toggleButton4" @click="send_one_file_to_ods()">Send your file</button>
                                            </div>
                                            </div>
        
                                        </form>

                                        </div>
                                      </div>
                                    </div>
                                    <div class="accordion-item">
                                      <h2 class="accordion-header" id="headingTwo">
                                        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseTwo" aria-expanded="false" aria-controls="collapseTwo">
                                          <strong> Send Multiple Files </strong>
                                        </button>
                                      </h2>
                                      <div id="collapseTwo" class="accordion-collapse collapse" aria-labelledby="headingTwo" data-bs-parent="#accordionExample">
                                        <div class="accordion-body">
                                          <h5> For this feature, you need to prepare a csv file with <strong> 4 columns (without headers) </strong>:  
                                                <ul>
                                                    <strong>
                                                        <li> First column : Document symbol </li>
                                                        <li> Second column : Job number </li>
                                                        <li> Third column : Language </li>
                                                        <li> Fourth column : Path </li>
                                                    </strong>
                                                </ul>
                                                Copy / Paste the content of your file in the text area (below) then hit "Send Files" button
                                          </h5>
                                          <!-- Form managing the multiple send -->
                                          <form class="form-inline" @submit.prevent>
                                              <div class="form-group mb-2">
                                                  <label for="inputDocSymbol1" class="sr-only">Docsymbol / Job number / language / path </label>
                                                  <textarea type="text" class="form-control"  placeholder=" Docsymbol / Job number / language / path " id="data_send_multiple4" name="data_send_multiple4" v-model="data_send_multiple4"></textarea>
                                              </div>
                                              <button type="button" class="btn btn-primary mb-2" @click="send_multiple_files_to_ods();">Send Files</button>
                                          </form>
                                        </div>
                                      </div>
                                    </div>
                                  </div>


                                </div>



                                
                                
                            </div>
                    </div>                   
                </div>  
            </div>
                 `,
created: async function(){
    },

data: function () {
    return {
        // Management of the display of the # divs
        showDisplayTab:false,
        showCreateTab:false,
        showUpdateTab:false,
        showSendFileTab:false,
        displayResult1:false,
        docsymbols:"",
        docsymbol2:"",
        fieldvalue2:"",
        field2:"",
        language2:"",
        listOfRecordsDiplayMetaData:[],
        docsymbol4:"",
        jobnumber4:"",
        language4:"",
        path4:"",
        data_send_multiple4:[],
        data_send_multiple5:[],
        my_symbol:"",
        my_area:"",
        my_distribution:"",
        my_title:"",
        my_language:""
    }
    },
        
    methods:{

        async displayMetaData(){

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
        
        my_data.forEach(element => {
            // We save the data
            console.log(element["body"]["data"])
            this.listOfRecordsDiplayMetaData.push(element["body"]["data"])
            })

            this.displayResult1=true;
        
        },
        
        // function creating metadata in ODS
        async createMetadata(){
            let dataset = new FormData()
            dataset.append('docsymbol',this.my_symbol)
            dataset.append('area',this.my_area)
            dataset.append('distribution',this.my_distribution)
            dataset.append('title',this.my_title)
            dataset.append('language',this.my_language)

            // loading all the data
            const my_response = await fetch("/create_metadata_ods",{
                "method":"POST",
                "body":dataset
                });
            
            const data = await my_response.json()

            alert(data)
        },

        // function sending file in ODS
        async send_one_file_to_ods(){
        
            let dataset = new FormData()
            dataset.append('docsymbol',this.docsymbol4)
            dataset.append('jobnumber',this.jobnumber4)
            dataset.append('language',this.language4)
            dataset.append('path',this.path4)
        
            // loading all the data
            const my_response = await fetch("/send_one_file_ods",{
                "method":"POST",
                "body":dataset
                });
            
            const data = await my_response.json()

            alert(data)
            
            },
        async update_one_file_to_ods(){
        
                let dataset = new FormData()
                dataset.append('docsymbol',this.docsymbol2)
                dataset.append('field',this.field2)
                dataset.append('fieldvalue',this.fieldvalue2)
                dataset.append('language',this.language2)
            
                // loading all the data
                const my_response = await fetch("/update_one_file_ods",{
                    "method":"PATCH",
                    "body":dataset
                    });
                
                const data = await my_response.json()
    
                alert(data)
                
                },

        async update_multiple_files_to_ods(){

            let dataset = new FormData()
            dataset.append('data_send_multiple5',this.data_send_multiple5)

            // loading all the data
            const my_response = await fetch("/update_multiple_file_ods",{
                "method":"PATCH",
                "body":dataset
                });
            
            const data = await my_response.json()

            alert(data)
            
            },

        async send_multiple_files_to_ods(){
    
            let dataset = new FormData()
            dataset.append('data_send_multiple4',this.data_send_multiple4)

            // loading all the data
            const my_response = await fetch("/send_multiple_file_ods",{
                "method":"POST",
                "body":dataset
                });
            
            const data = await my_response.json()

            alert(data)
            
            },

        async createRecord(){
            let dataset = new FormData()
            dataset.append('_id',this.my_id)
            dataset.append('record',this.record)
            dataset.append('name',this.name)
            dataset.append('topic',this.topic)
            dataset.append('vote',this.vote)
            dataset.append('date',this.date)
            dataset.append('security_council_document',this.security_council_document)
            dataset.append('refresh',this.refresh)
            dataset.append('listing_id',this.listing_id)
            dataset.append('languageSelected',this.languageSelected)
            const my_response = await fetch("/create_sc_listing",{
            "method":"POST",
            "body":dataset
            });
            const my_data = await my_response.json();
            console.log(my_data)
            this.displayRecordFromQuery=true
            alert("Record created!!!")
            location.reload()
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