// Modern Notification System
class NotificationManager {
    constructor() {
        this.container = null;
        this.notifications = [];
        this.init();
    }

    init() {
        // Create notification container if it doesn't exist
        if (!document.querySelector('.notification-container')) {
            this.container = document.createElement('div');
            this.container.className = 'notification-container';
            document.body.appendChild(this.container);
        } else {
            this.container = document.querySelector('.notification-container');
        }
    }

    show(message, type = 'info', title = '', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        const iconMap = {
            success: 'fas fa-check',
            error: 'fas fa-times',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };

        const titleMap = {
            success: 'Success',
            error: 'Error',
            warning: 'Warning',
            info: 'Information'
        };

        const finalTitle = title || titleMap[type] || 'Notification';
        const icon = iconMap[type] || iconMap.info;

        notification.innerHTML = `
            <div class="notification-icon">
                <i class="${icon}"></i>
            </div>
            <div class="notification-content">
                <div class="notification-title">${finalTitle}</div>
                <div class="notification-message">${message}</div>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;

        this.container.appendChild(notification);
        this.notifications.push(notification);

        // Trigger animation
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);

        // Auto remove after duration
        if (duration > 0) {
            setTimeout(() => {
                this.remove(notification);
            }, duration);
        }

        return notification;
    }

    remove(notification) {
        if (notification && notification.parentNode) {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
                const index = this.notifications.indexOf(notification);
                if (index > -1) {
                    this.notifications.splice(index, 1);
                }
            }, 300);
        }
    }

    success(message, title = 'Success', duration = 5000) {
        return this.show(message, 'success', title, duration);
    }

    error(message, title = 'Error', duration = 7000) {
        return this.show(message, 'error', title, duration);
    }

    warning(message, title = 'Warning', duration = 6000) {
        return this.show(message, 'warning', title, duration);
    }

    info(message, title = 'Information', duration = 5000) {
        return this.show(message, 'info', title, duration);
    }

    clear() {
        this.notifications.forEach(notification => {
            this.remove(notification);
        });
    }
}

// Global notification instance
const notifications = new NotificationManager();

// Replace alert function globally
window.alert = function(message) {
    notifications.info(message, 'Alert');
};

Vue.component('ods', {
    template: `
                <div class="container-fluid">
                    <div class="modern-card">
                        <div class="card-header description-section">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <h1 class="card-title">
                                        <i class="fas fa-database me-3"></i>
                                        ODS Actions
                                    </h1>
                                   
                                </div>
                                <div class="d-flex align-items-center gap-3">
                                    <div class="user-info-header">
                                        <i class="fas fa-user me-2"></i>
                                        <span class="user-name-header">{{session_username}}</span>
                                    </div>
                                    <button class="btn-modern btn-secondary-modern" @click="toggleTheme" title="Toggle Dark/Light Mode">
                                        <i :class="themeIcon"></i>
                                    </button>
                                    <a href="./logout" class="btn-modern btn-danger-modern">
                                        <i class="fas fa-sign-out-alt me-2"></i>
                                        Sign Out
                                    </a>
                        </div>
                        </div>
                        </div>
                        
                        <div class="card-body">
                            <ul class="nav nav-tabs modern-nav-tabs" id="mainTabs" role="tablist">
                                <li v-if="session_show_display=='true'" class="nav-item" role="presentation">
                                    <button class="nav-link active" id="display-tab" data-bs-toggle="tab" data-bs-target="#display" type="button" role="tab" aria-controls="display" aria-selected="true">
                                        <i class="fas fa-eye me-2"></i>
                                        Display Metadata
                                    </button>
                                </li>
                                <li v-if="session_show_create_update=='true'" class="nav-item" role="presentation">
                                    <button class="nav-link" id="create-update-tab" data-bs-toggle="tab" data-bs-target="#create-update" type="button" role="tab" aria-controls="create-update" aria-selected="false">
                                        <i class="fas fa-edit me-2"></i>
                                        Send Metadata
                                    </button>
                                </li>
                                <li v-if="session_show_send_file=='true'" class="nav-item" role="presentation">
                                    <button class="nav-link" id="send-files-tab" data-bs-toggle="tab" data-bs-target="#send-files" type="button" role="tab" aria-controls="send-files" aria-selected="false">
                                        <i class="fas fa-upload me-2"></i>
                                        Send Files
                                    </button>
                                </li>
                                <li v-if="session_show_parameters=='true'" class="nav-item" role="presentation">
                                    <button class="nav-link" id="parameters-tab" data-bs-toggle="tab" data-bs-target="#parameters" type="button" role="tab" aria-controls="parameters" aria-selected="false">
                                        <i class="fas fa-cog me-2"></i>
                                        Parameters
                                    </button>
                                </li>
                            </ul>
                        
                        <!-- <div class="card-body " style="margin-top: 1px;margin-left:10px;"> -->
                        
                            <div class="tab-content mt-4">
                                <!-- Display Tab -->	
                                <div v-if="session_show_display=='true'" class="tab-pane show active" id="display" role="tabpanel" aria-labelledby="display-tab">
                                    <div class="modern-controls-section">
                                        <div class="row">
                                            <div class="col-12">
                                                <label for="docsymbols" class="form-label-modern">Document Symbols</label>
                                                <textarea id="docsymbols" class="form-control-modern" rows="4" placeholder="Paste the list of symbols here (new line separated). The Apply button will be enabled when you enter content." name="docsymbols" v-model="docsymbols"></textarea>
                                            </div>
                                            </div>
                                        <div class="modern-button-group mt-3">
                                            <button class="btn-modern btn-primary-modern" type="button" id="toggleButton" @click="displayMetaData(docsymbols);" :disabled="isDisplayButtonDisabled">
                                                <i class="fas fa-search me-2"></i>
                                                Apply
                                            </button>
                                            <button v-if="displayResult" class="btn-modern btn-secondary-modern" type="button" @click="refreshDisplayResults()">
                                                <i class="fas fa-trash me-2"></i>
                                                Clear
                                            </button>
                                            </div>
                                            </div>
                                    
                                    <div id="displayProgress1" class="text-center mt-4" v-if="displayProgress1">
                                        <div class="loading-spinner">
                                            <div class="spinner"></div>
                                            <p>Loading metadata...</p>
                                        </div>
                                    </div>
                                    
                                    <div class="modern-table-container" v-if="displayResult">
                                        <table id="MyTable" class="modern-responsive-table">
                                            <thead>
                                                <tr>
                                                    <th>Document Symbol</th>
                                                    <th>Agenda</th>
                                                    <th>Session</th>
                                                    <th>Distribution</th>
                                                    <th>Area</th>
                                                    <th>Subjects</th>
                                                    <th>Job Number</th>
                                                    <th>Title</th>
                                                    <th>Publication Date</th>
                                                    <th>Release Date</th>
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
                                    </div>
                                
                                    <div class="modern-action-buttons" v-if="displayResult==true">
                                        <button class="btn-modern btn-secondary-modern" type="button" @click="docsymbols='';displayResult=false;listOfRecordsDiplayMetaData=[];">
                                            <i class="fas fa-trash me-2"></i>
                                            Clear List
                                        </button>
                                        <button class="btn-modern btn-info-modern" type="button" @click="exportTableToCSV('MyTable')">
                                            <i class="fas fa-download me-2"></i>
                                            Export to CSV
                                        </button>
                                    </div>
                                </div>
                                <!-- End Display Tab -->
                                    
                        
                                <!-- Create/Update Tab -->	
                                <div v-if="session_show_create_update=='true'" class="tab-pane fade" id="create-update" role="tabpanel" aria-labelledby="create-update-tab">
                                    <div class="modern-controls-section">
                                        <div class="row">
                                            <div class="col-12">
                                                <label for="docsymbols1" class="form-label-modern">Document Symbols</label>
                                                <textarea id="docsymbols1" class="form-control-modern" rows="4" placeholder="Paste the list of symbols here (new line separated). The Send button will be enabled when you enter content." name="docsymbols1" v-model="docsymbols1"></textarea>
                                            </div>
                                            </div>
                                        <div class="modern-button-group mt-3">
                                            <button class="btn-modern btn-success-modern" type="button" @click="displayResultCreateUpdate(docsymbols1);" :disabled="isSendButtonDisabled">
                                                <i class="fas fa-paper-plane me-2"></i>
                                                Send
                                            </button>
                                            <button v-if="displayResult1" class="btn-modern btn-secondary-modern" type="button" @click="refreshSendResults()">
                                                <i class="fas fa-trash me-2"></i>
                                                Clear
                                            </button>
                                            </div>
                                            </div>
                                    
                                    <div id="displayProgress2" class="text-center mt-4" v-if="displayProgress2">
                                        <div class="loading-spinner">
                                            <div class="spinner"></div>
                                            <p>Processing metadata...</p>
                                        </div>
                                    </div>
                                       
                                    <div class="modern-table-container" v-if="displayResult1">
                                        <table id="MyTable1" class="modern-responsive-table">
                                            <thead>
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
                                    
                                    <div class="modern-action-buttons" v-if="displayResult1==true">
                                        <button class="btn-modern btn-secondary-modern" type="button" @click="docsymbols1='';displayResult1=false;listOfResult1=[];">
                                            <i class="fas fa-trash me-2"></i>
                                            Clear List
                                        </button>
                                        <button class="btn-modern btn-info-modern" type="button" @click="exportTableToCSV('MyTable1')">
                                            <i class="fas fa-download me-2"></i>
                                            Export to CSV
                                        </button>
                                    </div>
                                </div>
                                <!-- End Create/Update Tab -->	
                                
                            
                                <!-- Send Files Tab -->	
                                <div v-if="session_show_send_file=='true'" class="tab-pane fade" id="send-files" role="tabpanel" aria-labelledby="send-files-tab">
                                    <div class="modern-controls-section">
                                        <div class="row">
                                            <div class="col-12">
                                                <label for="docsymbols2" class="form-label-modern">Document Symbols</label>
                                                <textarea id="docsymbols2" class="form-control-modern" rows="4" placeholder="Paste the list of symbols here (new line separated). The Send Files button will be enabled when you enter content." name="docsymbols2" v-model="docsymbols2"></textarea>
                                            </div>
                                            </div>
                                        <div class="modern-button-group mt-3">
                                            <button class="btn-modern btn-success-modern" type="button" v-if="displayResult2==false" @click="displayResultSendFile(docsymbols2)" :disabled="isSendFilesButtonDisabled">
                                                <i class="fas fa-upload me-2"></i>
                                                Send Files
                                            </button>
                                            <button v-if="displayResult2" class="btn-modern btn-secondary-modern" type="button" @click="refreshSendFilesResults()">
                                                <i class="fas fa-trash me-2"></i>
                                                Clear
                                            </button>
                                            </div>
                                            </div>
                                    
                                    <div id="displayProgress3" class="text-center mt-4" v-if="displayProgress3">
                                        <div class="loading-spinner">
                                            <div class="spinner"></div>
                                            <p>Uploading files...</p>
                                        </div>
                                    </div>
                                
                                    <div class="modern-table-container" v-if="displayResult2">
                                        <table id="MyTable2" class="modern-responsive-table">
                                            <thead>
                                                <tr>
                                                    <th>Filename</th>
                                                    <th>Document Symbol</th>
                                                    <th>Language</th>
                                                    <th>Job Number</th>
                                                    <th>Result</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                    <tr v-for="record in listOfResult2">
                                                    <td>{{record["filename"]}}</td>
                                                    <td>{{record["docsymbol"]}}</td>
                                                    <td>{{record["language"]}}</td>
                                                    <td>{{record["jobnumber"]}}</td>
                                                    <td>{{record["result"]}}</td>
                                                    </tr> 
                                            </tbody>
                                        </table>
                                    </div>
                                    
                                    <div class="modern-action-buttons" v-if="displayResult2==true">
                                        <button class="btn-modern btn-secondary-modern" type="button" @click="docsymbols2='';displayResult2=false;listOfResult2=[];">
                                            <i class="fas fa-trash me-2"></i>
                                            Clear List
                                        </button>
                                        <button class="btn-modern btn-info-modern" type="button" @click="exportTableToCSV('MyTable2')">
                                            <i class="fas fa-download me-2"></i>
                                            Export to CSV
                                        </button>
                                    </div>
                                </div>
                                <!-- End Send Files Tab -->	

                                  
                                <!-- Parameters Tab -->	
                                <div v-if="session_show_parameters=='true'" class="tab-pane fade" id="parameters" role="tabpanel">
                                    <div class="modern-controls-section">
                                        <h4 class="mb-4">
                                            <i class="fas fa-cog me-2"></i>
                                            System Parameters
                                        </h4>

                                    <div class="accordion" id="accordionExample">
                                        <div class="accordion-item" id="sites">
                                                <h2 class="accordion-header" id="headingOne0">
                                                    <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne0" aria-expanded="true" aria-controls="collapseOne0">
                                                        <i class="fas fa-building me-2"></i>
                                                        <strong>Sites Management</strong>
                                                    </button>
                                                </h2>
                                                <div id="collapseOne0" class="accordion-collapse collapse" aria-labelledby="headingOne0" data-bs-parent="#accordionExample">
                                                <div class="accordion-body">
                                                        <div class="description-section mb-4">
                                                            <h5>Add New Site</h5>
                                                            <p>Please fill the fields below to create a new site.</p>
                                                        </div>
                                                        
                                                        <form class="form-modern">
                                                            <div class="row">
                                                                <div class="col-md-4">
                                                                    <label for="code_site" class="form-label-modern">Code Site</label>
                                                                    <input type="text" class="form-control-modern" id="code_site" v-model="code_site" placeholder="Enter 3-letter site code">
                                                                </div>
                                                                <div class="col-md-4">
                                                                    <label for="label_site" class="form-label-modern">Label Site</label>
                                                                    <input type="text" class="form-control-modern" id="label_site" v-model="label_site" placeholder="Enter site label">
                                                                </div>
                                                                <div class="col-md-4">
                                                                    <label for="prefix_site" class="form-label-modern">Prefix Site</label>
                                                                    <input type="text" class="form-control-modern" id="prefix_site" v-model="prefix_site" placeholder="Enter 2-letter prefix">
                                                                </div>
                                                        </div>
                                                            
                                                            <div class="modern-button-group mt-4">
                                                                <button type="button" class="btn-modern btn-primary-modern" @click="addSite()">
                                                                    <i class="fas fa-plus me-2"></i>
                                                                    Create Site
                                                                </button>
                                                        </div>                                                                                                                
                                                    </form>
                                                </div>
                                                </div>
                                            </div>
                                            <div class="accordion-item" id="users">
                                                <h2 class="accordion-header" id="headingOne">
                                                    <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne" aria-expanded="false" aria-controls="collapseOne">
                                                        <i class="fas fa-users me-2"></i>
                                                    <strong>Users Management</strong>
                                                </button>
                                                </h2>
                                                <div id="collapseOne" class="accordion-collapse collapse" aria-labelledby="headingOne" data-bs-parent="#accordionExample">
                                                <div class="accordion-body">
                                                        <div class="description-section mb-4">
                                                            <h5>Add New User</h5>
                                                            <p>Please fill the fields below to create a new user account.</p>
                                                        </div>
                                                        
                                                        <form class="form-modern">
                                                            <div class="row">
                                                                <div class="col-md-6">
                                                                    <label for="site" class="form-label-modern">Site</label>
                                                                    <select id="site" class="form-select-modern" v-model="code_site">
                                                                        <option value="">Select a site</option>
                                                                        <option v-for="my_site in site" :value="my_site">{{my_site}}</option>
                                                                    </select>
                                                        </div>
                                                                <div class="col-md-6">
                                                                    <label for="email" class="form-label-modern">Email</label>
                                                                    <input type="email" class="form-control-modern" id="email" v-model="email" placeholder="Enter user email">
                                                        </div>
                                                            </div>
                                                            
                                                            <div class="row mt-3">
                                                                <div class="col-md-6">
                                                                    <label for="password" class="form-label-modern">Password</label>
                                                                    <input type="password" class="form-control-modern" id="password" v-model="password" placeholder="Enter user password">
                                                                </div>
                                                            </div>
                                                            
                                                            <div class="mt-4">
                                                                <label class="form-label-modern">Select the tab(s) to display</label>
                                                                <div class="row">
                                                                    <div class="col-md-6">
                                                                        <div class="form-check">
                                                                            <input class="form-check-input" type="checkbox" id="show_display" v-model="show_display">
                                                                            <label class="form-check-label" for="show_display">Show Display metadata</label>
                                                                        </div>
                                                                        <div class="form-check">
                                                                            <input class="form-check-input" type="checkbox" id="show_create_update" v-model="show_create_update">
                                                                            <label class="form-check-label" for="show_create_update">Show Create/Update metadata</label>
                                                                        </div>
                                                                        <div class="form-check">
                                                                            <input class="form-check-input" type="checkbox" id="show_send_file" v-model="show_send_file">
                                                                            <label class="form-check-label" for="show_send_file">Show Send files to ODS</label>
                                                                        </div>
                                                                    </div>
                                                                    <div class="col-md-6">
                                                                        <div class="form-check">
                                                                            <input class="form-check-input" type="checkbox" id="show_jobnumbers_management" v-model="show_jobnumbers_management">
                                                                            <label class="form-check-label" for="show_jobnumbers_management">Show Job numbers management</label>
                                                                        </div>
                                                                        <div class="form-check">
                                                                            <input class="form-check-input" type="checkbox" id="show_parameters" v-model="show_parameters">
                                                                            <label class="form-check-label" for="show_parameters">Show Parameters</label>
                                                                        </div>
                                                                    </div>
                                                            </div>
                                                            </div>
                                                            
                                                            <div class="modern-button-group mt-4">
                                                                <button type="button" class="btn-modern btn-primary-modern" @click="addUser()">
                                                                    <i class="fas fa-user-plus me-2"></i>
                                                                    Create User
                                                                </button>
                                                            </div>
                                                    </form>
                                                </div>
                                                </div>
                                            </div>
                                            <div class="accordion-item">
                                                <h2 class="accordion-header" id="headingThree">
                                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseThree" aria-expanded="false" aria-controls="collapseThree">
                                                        <i class="fas fa-list-alt me-2"></i>
                                                        <strong>System Logs</strong>
                                                </button>
                                                </h2>
                                                <div id="collapseThree" class="accordion-collapse collapse" aria-labelledby="headingThree" data-bs-parent="#accordionExample">
                                                <div class="accordion-body">
                                                        <div class="description-section mb-4">
                                                            <h5>Activity Logs</h5>
                                                            <p>View and export system activity logs.</p>
                                                        </div>
                                                        
                                                        <!-- Filter Controls -->
                                                        <div class="modern-controls-section mb-4">
                                                            <div class="row">
                                                                <div class="col-md-4">
                                                                    <label for="logUserFilter" class="form-label-modern">Filter by User</label>
                                                                    <input type="text" id="logUserFilter" class="form-control-modern" v-model="logUserFilter" placeholder="Enter username...">
                                                                </div>
                                                                <div class="col-md-4">
                                                                    <label for="logActionFilter" class="form-label-modern">Filter by Action</label>
                                                                    <input type="text" id="logActionFilter" class="form-control-modern" v-model="logActionFilter" placeholder="Enter action...">
                                                                </div>
                                                                <div class="col-md-4">
                                                                    <label for="logDateFilter" class="form-label-modern">Filter by Date</label>
                                                                    <input type="date" id="logDateFilter" class="form-control-modern" v-model="logDateFilter">
                                                                </div>
                                                            </div>
                                                            <div class="modern-button-group mt-3">
                                                                <button type="button" class="btn-modern btn-secondary-modern" @click="clearLogFilters">
                                                                    <i class="fas fa-times me-2"></i>
                                                                    Clear Filters
                                                                </button>
                                                            </div>
                                                        </div>
                                                        
                                                        <div class="modern-button-group mb-4">
                                                            <button type="button" class="btn-modern btn-info-modern" @click="exportTableToCSV('listlogs')">
                                                                <i class="fas fa-download me-2"></i>
                                                                Export All Logs to CSV
                                                            </button>
                                                        </div>
                                                        
                                                        <div class="modern-table-container">
                                                            <table class="modern-responsive-table" id="listlogs">
                                                        <thead>
                                                            <tr>
                                                                        <th>User</th>
                                                                        <th>Action</th>
                                                                        <th>Date</th>
                                                            </tr>
                                                        </thead>
                                                        <tbody>
                                                                    <tr v-for="field in filteredLogs">
                                                                        <td>{{field.user}}</td>
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
                                </div>
                                <!-- End Parameters Tab -->	
                            </div>
                        </div>
                    </div>
                </div>
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
        logUserFilter:"",
        logActionFilter:"",
        logDateFilter:"",
        isDarkMode: true,
        code_site:"",
        label_site:"",
        prefix_site:"",
    }
    },
    
    computed: {
        filteredLogs() {
            return this.listOfLogs.filter(log => {
                const userMatch = !this.logUserFilter || log.user.toLowerCase().includes(this.logUserFilter.toLowerCase());
                const actionMatch = !this.logActionFilter || log.action.toLowerCase().includes(this.logActionFilter.toLowerCase());
                const dateMatch = !this.logDateFilter || this.formatDateForFilter(log.date.$date) === this.logDateFilter;
                
                return userMatch && actionMatch && dateMatch;
            });
        },
        
        themeIcon() {
            return this.isDarkMode ? 'fas fa-sun' : 'fas fa-moon';
        },
        
        // Button state computed properties
        isDisplayButtonDisabled() {
            return !this.docsymbols || this.docsymbols.trim() === '';
        },
        
        isSendButtonDisabled() {
            return !this.docsymbols1 || this.docsymbols1.trim() === '';
        },
        
        isSendFilesButtonDisabled() {
            return !this.docsymbols2 || this.docsymbols2.trim() === '';
        }
    },
    
    mounted() {
        // Initialize theme from localStorage or default to dark
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            this.isDarkMode = savedTheme === 'dark';
            document.documentElement.setAttribute('data-bs-theme', savedTheme);
        } else {
            // Default to dark mode
            this.isDarkMode = true;
            document.documentElement.setAttribute('data-bs-theme', 'dark');
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
        
        formatDateForFilter(dateString) {
            // Convert the date string to YYYY-MM-DD format for comparison
            const date = new Date(dateString);
            return date.toISOString().split('T')[0];
        },
        
        clearLogFilters() {
            this.logUserFilter = "";
            this.logActionFilter = "";
            this.logDateFilter = "";
        },
        
        toggleTheme() {
            this.isDarkMode = !this.isDarkMode;
            const htmlElement = document.documentElement;
            htmlElement.setAttribute('data-bs-theme', this.isDarkMode ? 'dark' : 'light');
            
            // Save preference to localStorage
            localStorage.setItem('theme', this.isDarkMode ? 'dark' : 'light');
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
        try {
            const my_response = await fetch("./loading_symbol",{
                "method":"POST",
                "body":dataset
                });
                
            const my_data = await my_response.json()

            // loading data
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

        } catch (error) {
            // remove Progress bar
            this.displayProgress1=false
            notifications.error(error.message || error, 'Search Error');
        }
        finally{
            // remove Progress bar
            this.displayProgress1=false
        }

        // display Results
        if (this.listOfRecordsDiplayMetaData.length>=1) {
            this.displayResult=true;
            // Show success notification
            notifications.success(`Found ${this.listOfRecordsDiplayMetaData.length} metadata records`, 'Search Complete');
        } else {
            notifications.info('No metadata records found for the provided symbols', 'Search Complete');
        }

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
            try {
                const my_response = await fetch("./create_metadata_ods",{
                    "method":"POST",
                    "body":dataset
                    });
                
                const my_data = await my_response.json();

                my_data.forEach(elements => {
                    //console.log(typeof(elements))
                    this.listOfResult1=this.listOfResult1.concat(elements)
                })
                
            } catch (error) {
                // Stop spinner on error
                this.displayProgress2=false
                notifications.error(error.message || error, 'Send Error');
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
            
            // Show success notification
            notifications.success(`Processed ${this.listOfResult1.length} metadata records`, 'Send Complete');
            
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
                try {
                    const my_response = await fetch("./exporttoodswithfile",{
                        "method":"POST",
                        "body":dataset
                        });
                                       
                    const my_data = await my_response.json()
                    // console.log(my_data)
                    // loading data
                    my_data.forEach(elements => {
                        //console.log(typeof(elements))
                        this.listOfResult2=this.listOfResult2.concat(elements)
                    })
                    
                } catch (error) {
                    // Stop spinner on error
                    this.displayProgress3=false
                    notifications.error(error.message || error, 'Upload Error');
                }
                finally{
                    // display Progress bar
                    this.displayProgress3=false
                }

                if (this.listOfResult2.length!=0){
                    this.displayResult2=true;
                    // Show success notification
                    notifications.success(`Uploaded ${this.listOfResult2.length} files successfully`, 'Upload Complete');
                } else {
                    notifications.warning('No files were uploaded', 'Upload Complete');
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
                        notifications.success(my_data.message, 'User Created');
                        }
                        
                    catch (error) {
                        notifications.error(error.message || error, 'User Creation Error');
                    }
                }
            else{
                notifications.warning("Please check the inputs!", 'Validation Error') 
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
                        notifications.success(my_data.message, 'Site Created');
                        }
                        
                    catch (error) {
                        notifications.error(error.message || error, 'Site Creation Error');
                    }
                }
            else{
                notifications.warning("Please check the inputs!", 'Validation Error') 
            }
            window.location.reload();      
        },
        
        // Notification helper methods
        showSuccess(message, title = 'Success') {
            notifications.success(message, title);
        },
        
        showError(message, title = 'Error') {
            notifications.error(message, title);
        },
        
        showWarning(message, title = 'Warning') {
            notifications.warning(message, title);
        },
        
        showInfo(message, title = 'Information') {
            notifications.info(message, title);
        },
        
        // Refresh methods for each tab - only clear data and hide results
        refreshDisplayResults() {
            this.listOfRecordsDiplayMetaData = [];
            this.displayResult = false;
            this.docsymbols = ''; // Clear the textarea
            notifications.success('Display results and input cleared', 'Clear Complete');
        },
        
        refreshSendResults() {
            this.listOfResult1 = [];
            this.displayResult1 = false;
            this.docsymbols1 = ''; // Clear the textarea
            notifications.success('Send results and input cleared', 'Clear Complete');
        },
        
        refreshSendFilesResults() {
            this.listOfResult2 = [];
            this.displayResult2 = false;
            this.docsymbols2 = ''; // Clear the textarea
            notifications.success('Send files results and input cleared', 'Clear Complete');
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
                    
                    // Show success notification
                    notifications.success('CSV file downloaded successfully!', 'Export Complete');
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