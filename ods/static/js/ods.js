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
                                        ODS Actions
                                    </h1>
                                   
                                </div>
                                <div class="d-flex align-items-end gap-3">
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
                                <li class="nav-item" role="presentation">
                                    <button class="nav-link" id="change-password-tab" data-bs-toggle="tab" data-bs-target="#change-password" type="button" role="tab" aria-controls="change-password" aria-selected="false">
                                        <i class="fas fa-key me-2"></i>
                                        Change Password
                                    </button>
                                </li>
                                <li v-if="session_show_parameters=='true'" class="nav-item" role="presentation">
                                    <button class="nav-link" id="parameters-tab" data-bs-toggle="tab" data-bs-target="#parameters" type="button" role="tab" aria-controls="parameters" aria-selected="false">
                                        <i class="fas fa-cog me-2"></i>
                                        Parameters
                                    </button>
                                </li>
                                <li class="nav-item" role="presentation">
                                    <button class="nav-link" id="help-tab" data-bs-toggle="tab" data-bs-target="#help" type="button" role="tab" aria-controls="help" aria-selected="false">
                                        <i class="fas fa-question-circle me-2"></i>
                                        Help
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
                                                <textarea id="docsymbols" class="form-control-modern" rows="10" placeholder="Paste the list of symbols here (new line separated). The Apply button will be enabled when you enter content." name="docsymbols" v-model="docsymbols"></textarea>
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
                                    
                                    <div class="modern-table-container" v-if="displayResult" style="overflow-y: auto !important; max-height: 500px !important;">
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
                                                <td v-html="formatField(record[0]['symbol'])"></td>
                                                <td v-html="formatField(record[0]['agendas'])"></td>
                                                <td v-html="formatField(record[0]['sessions'])"></td>
                                                <td v-html="formatField(record[0]['distribution'])"></td>
                                                <td v-html="formatField(record[0]['area'])"></td>
                                                <td v-html="formatField(record[0]['subjects'])"></td>
                                                <td v-html="formatJobNumbersWithFlags(record[0]['job_numbers'])"></td>
                                                <td v-html="formatField(record[0]['title'])"></td>
                                                <td v-html="formatField(record[0]['publication_date'], true)"></td>
                                                <td v-html="formatField(record[0]['release_dates'], true)"></td>
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
                                                <textarea id="docsymbols1" class="form-control-modern" rows="10" placeholder="Paste the list of symbols here (new line separated). The Send button will be enabled when you enter content." name="docsymbols1" v-model="docsymbols1"></textarea>
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
                                       
                                    <div class="modern-table-container" v-if="displayResult1" style="overflow-y: auto !important; max-height: 500px !important;">
                                        <table id="MyTable1" class="modern-responsive-table">
                                            <thead>
                                                <tr>
                                                    <th>Document Symbol</th>
                                                    <th>Result</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <tr v-for="record in listOfResult1">
                                                    <td v-html="formatField(record['docsymbol'])"></td>
                                                    <td v-html="formatField(record['text'])"></td>
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
                                                <textarea id="docsymbols2" class="form-control-modern" rows="10" placeholder="Paste the list of symbols here (new line separated). The Send Files button will be enabled when you enter content." name="docsymbols2" v-model="docsymbols2"></textarea>
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
                                
                                    <div class="modern-table-container" v-if="displayResult2" style="overflow-y: auto !important; max-height: 500px !important;">
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
                                                    <td v-html="formatField(record['filename'])"></td>
                                                    <td v-html="formatField(record['docsymbol'])"></td>
                                                    <td v-html="formatField(record['language'])"></td>
                                                    <td v-html="formatField(record['jobnumber'])"></td>
                                                    <td v-html="formatField(record['result'])"></td>
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
                                
                                <!-- Change Password Tab -->	
                                <div class="tab-pane fade" id="change-password" role="tabpanel" aria-labelledby="change-password-tab">
                                    <div class="modern-controls-section">
                                        <h4 class="mb-4">
                                            <i class="fas fa-key me-2"></i>
                                            Change Password
                                        </h4>
                                        
                                        <div class="row">
                                            <div class="col-md-8 col-lg-6">
                                                <div class="modern-card">
                                                    <div class="card-body">
                                                        <form @submit.prevent="changePasswordFromTab">
                                                            <div class="mb-3">
                                                                <label for="currentEmail" class="form-label-modern">Email Address</label>
                                                                <input type="email" class="form-control-modern" id="currentEmail" v-model="userEmail" readonly>
                                                            </div>
                                                            
                                                            <div class="mb-3">
                                                                <label for="newPasswordTab" class="form-label-modern">New Password</label>
                                                                <input type="password" class="form-control-modern" id="newPasswordTab" v-model="newPassword" placeholder="Enter new password" required>
                                                            </div>
                                                            
                                                            <div class="mb-4">
                                                                <label for="confirmPasswordTab" class="form-label-modern">Confirm New Password</label>
                                                                <input type="password" class="form-control-modern" id="confirmPasswordTab" v-model="confirmPassword" placeholder="Confirm new password" required>
                                                            </div>
                                                            
                                                            <div class="d-flex gap-2">
                                                                <button type="submit" class="btn-modern btn-primary-modern" :disabled="!newPassword || !confirmPassword">
                                                                    <i class="fas fa-check me-2"></i>
                                                                    Change Password
                                                                </button>
                                                                <button type="button" class="btn-modern btn-secondary-modern" @click="clearPasswordFields">
                                                                    <i class="fas fa-times me-2"></i>
                                                                    Clear
                                                                </button>
                                                            </div>
                                                        </form>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <!-- End Change Password Tab -->	
                                
                                <!-- Help Tab -->	
                                <div class="tab-pane fade" id="help" role="tabpanel" aria-labelledby="help-tab">
                                    <div class="modern-controls-section">
                                        <div class="d-flex justify-content-between align-items-center mb-4">
                                            <div>
                                                <h4 class="mb-2">
                                                    <i class="fas fa-question-circle me-2"></i>
                                                    ODS Actions Help Assistant
                                                </h4>
                                                <p class="mb-0">Ask me anything about the ODS Actions application. I can help you understand features, workflows, and how to use the system effectively.</p>
                                            </div>
                                            <div>
                                                <a href="./download_chatbot_manual" 
                                                   class="btn btn-modern btn-primary-modern" 
                                                   download="ODS_Actions_Chatbot_User_Manual.md"
                                                   title="Download Chatbot User Manual (Markdown)">
                                                    <i class="fas fa-download me-2"></i>
                                                    Download Chatbot User Manual
                                                </a>
                                            </div>
                                        </div>
                                        
                                        <!-- Chat Container -->
                                        <div class="chatbot-container">
                                            <div class="chat-messages" id="chatMessages" ref="chatMessages">
                                                <div class="message bot-message">
                                                    <div class="message-avatar">
                                                        <i class="fas fa-robot"></i>
                                                    </div>
                                                    <div class="message-content">
                                                        <div class="message-text">
                                                            Hello! I'm your ODS Actions assistant. I can help you with:
                                                            <ul>
                                                                <li>How to use the Display Metadata feature</li>
                                                                <li>How to send metadata to ODS</li>
                                                                <li>How to upload files</li>
                                                                <li>Understanding the database structure</li>
                                                                <li>API endpoints and technical details</li>
                                                            </ul>
                                                            What would you like to know?
                                                        </div>
                                                        <div class="message-time">{{ getCurrentTime() }}</div>
                                                    </div>
                                                </div>
                                                
                                                <div v-for="(msg, index) in chatMessages" :key="index" :class="['message', msg.type + '-message']">
                                                    <div class="message-avatar">
                                                        <i :class="msg.type === 'user' ? 'fas fa-user' : 'fas fa-robot'"></i>
                                                    </div>
                                                    <div class="message-content">
                                                        <div class="message-text" v-html="formatMessage(msg.text)"></div>
                                                        <div class="message-time">{{ msg.time }}</div>
                                                    </div>
                                                </div>
                                                
                                                <div v-if="chatLoading" class="message bot-message">
                                                    <div class="message-avatar">
                                                        <i class="fas fa-robot"></i>
                                                    </div>
                                                    <div class="message-content">
                                                        <div class="message-text">
                                                            <div class="typing-indicator">
                                                                <span></span>
                                                                <span></span>
                                                                <span></span>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                            
                                            <!-- Chat Input -->
                                            <div class="chat-input-container">
                                                <input 
                                                    type="text" 
                                                    class="form-control-modern chat-input" 
                                                    v-model="chatInput" 
                                                    @keyup.enter="sendChatMessage"
                                                    :disabled="chatLoading"
                                                    placeholder="Type your question here... (Press Enter to send)"
                                                    ref="chatInput"
                                                >
                                                <div class="modern-button-group mt-2">
                                                    <button 
                                                        class="btn-modern btn-primary-modern" 
                                                        @click="sendChatMessage"
                                                        :disabled="chatLoading || !chatInput.trim()"
                                                        type="button"
                                                    >
                                                        <i class="fas fa-paper-plane me-2"></i>
                                                        Send
                                                    </button>
                                                    <button 
                                                        class="btn-modern btn-secondary-modern" 
                                                        @click="clearChat"
                                                        type="button"
                                                    >
                                                        <i class="fas fa-trash me-2"></i>
                                                        Clear Chat
                                                    </button>
                                                    <button 
                                                        class="btn-modern btn-secondary-modern" 
                                                        @click="downloadChat"
                                                        type="button"
                                                        :disabled="chatMessages.length === 0"
                                                    >
                                                        <i class="fas fa-download me-2"></i>
                                                        Download Chat
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <!-- End Help Tab -->	
                            </div>
                        </div>
                    </div>
                </div>
            </div>
             `,
created:async function(){
    this.loadLogs()
    this.loadSites()
    
    // Initialize user email for password change
    if (this.session_username && this.session_username !== 'undefined' && this.session_username !== '') {
        this.userEmail = this.session_username;
    } else {
        // Fallback: try to get email from the displayed username in the navbar
        const usernameElement = document.querySelector('.user-name-header');
        if (usernameElement) {
            this.userEmail = usernameElement.textContent.trim();
        } else {
            this.userEmail = 'eric.attere@un.org'; // Last resort fallback
        }
    }
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
        showPasswordModal: false,
        userEmail: "",
        newPassword: "",
        confirmPassword: "",
        // Chatbot data
        chatMessages: [],
        chatInput: "",
        chatLoading: false,
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
        
        // Enable mouse wheel scrolling on textareas
        this.$nextTick(() => {
            const textareas = document.querySelectorAll('textarea.form-control-modern');
            textareas.forEach(textarea => {
                textarea.addEventListener('wheel', function(e) {
                    // Allow scrolling in textarea
                    textarea.scrollTop += e.deltaY;
                    e.preventDefault();
                });
            });
        });
    },
        
    methods:{

        formatField(field, isDateField = false) {
            // Handle null, undefined, or empty values
            if (!field || field === null || field === undefined) {
                return 'Not found';
            }
            
            // If it's already a string, return it (or format as date if needed)
            if (typeof field === 'string') {
                return isDateField ? this.formatDate(field) : field;
            }
            
            // If it's an array, join the elements with green arrows
            if (Array.isArray(field)) {
                if (field.length === 0) {
                    return 'Not found';
                }
                // Filter out empty strings and join with green arrows
                const validItems = field.filter(item => item && item.toString().trim() !== '');
                if (validItems.length === 0) {
                    return 'Not found';
                }
                return validItems.map(item => {
                    const displayValue = isDateField ? this.formatDate(item) : item;
                    return `<span class="green-arrow">➤</span> ${displayValue}`;
                }).join('\n');
            }
            
            // If it's an object, try to extract meaningful values
            if (typeof field === 'object') {
                // If it has a $date property (MongoDB date format)
                if (field.$date) {
                    return this.formatDate(field.$date);
                }
                // If it has other properties, try to get the first meaningful value
                const values = Object.values(field).filter(val => val && val.toString().trim() !== '');
                if (values.length === 0) {
                    return 'Not found';
                }
                return values.map(val => `<span class="green-arrow">➤</span> ${val}`).join('\n');
            }
            
            // For any other type, convert to string
            return field.toString();
        },

        formatDate(dateString) {
            try {
                const date = new Date(dateString);
                if (isNaN(date.getTime())) {
                    return 'Invalid date';
                }
                
                // Format as DD/MM/YYYY HH:MM:SS
                const day = String(date.getDate()).padStart(2, '0');
                const month = String(date.getMonth() + 1).padStart(2, '0');
                const year = date.getFullYear();
                const hours = String(date.getHours()).padStart(2, '0');
                const minutes = String(date.getMinutes()).padStart(2, '0');
                const seconds = String(date.getSeconds()).padStart(2, '0');
                
                return `${day}/${month}/${year} ${hours}:${minutes}:${seconds}`;
            } catch (error) {
                return 'Invalid date';
            }
        },

        formatJobNumbersWithFlags(jobNumbers) {
            if (!jobNumbers || jobNumbers === null || jobNumbers === undefined) {
                return 'Not found';
            }
            
            // Language codes only (no emojis)
            const languageFlags = {
                'AR': 'AR', // Arabic
                'ZH': 'ZH', // Chinese
                'EN': 'EN', // English
                'FR': 'FR', // French
                'RU': 'RU', // Russian
                'ES': 'ES', // Spanish
                'DE': 'DE'  // German
            };
            
            // Use the exact same LANGUAGES array as defined in the backend
            const LANGUAGES = ["AR","ZH","EN","FR","RU","ES","DE"];
            
            if (typeof jobNumbers === 'string') {
                return jobNumbers;
            }
            
            if (Array.isArray(jobNumbers)) {
                if (jobNumbers.length === 0) {
                    return 'Not found';
                }
                
                // Filter out empty or invalid job numbers
                const validJobNumbers = jobNumbers.filter(job => job && job.toString().trim() !== '');
                
                if (validJobNumbers.length === 0) {
                    return 'Not found';
                }
                
                // Create formatted job numbers with green thick arrows
                const formattedJobs = validJobNumbers.map((jobNumber, index) => {
                    return `<span class="green-arrow">➤</span> ${jobNumber}`;
                });
                
                return formattedJobs.join('\n');
            }
            
            return jobNumbers.toString();
        },

        async loadLogs(){
        // loading the logs
        try {
        const my_response = await fetch("./display_logs",{
            "method":"GET",
            });
            
            if (!my_response.ok) {
                throw new Error(`HTTP error! status: ${my_response.status}`);
            }
            
            const contentType = my_response.headers.get("content-type");
            if (!contentType || !contentType.includes("application/json")) {
                throw new Error("Response is not JSON");
            }
            
        const my_data = await my_response.json();
            
            // Robust error handling for malformed responses
            if (Array.isArray(my_data)) {
        my_data.forEach(element => {
                    if (element && typeof element === 'object') {
                        this.listOfLogs.push(element);
                    } else {
                        console.error("Unexpected log element type:", element);
                    }
                });
            } else {
                console.error("Expected array response for logs, got:", typeof my_data, my_data);
                notifications.warning("Unexpected response format from logs API", 'Response Error');
            }
        } catch (error) {
            notifications.error(`Failed to load logs: ${error.message}`, 'Load Error');
        }
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
        
        
        // Change password from tab
        async changePasswordFromTab() {
            // Validate passwords
            if (!this.newPassword || !this.confirmPassword) {
                notifications.warning('Please fill in all password fields', 'Validation Error');
                return;
            }
            
            if (this.newPassword !== this.confirmPassword) {
                notifications.error('Passwords do not match', 'Validation Error');
                return;
            }
            
            if (this.newPassword.length < 6) {
                notifications.error('Password must be at least 6 characters long', 'Validation Error');
                return;
            }
            
            try {
                const formData = new FormData();
                formData.append('email', this.userEmail);
                formData.append('new_password', this.newPassword);
                
                const response = await fetch('./change_password', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    notifications.success(data.message, 'Password Changed');
                    this.clearPasswordFields();
                } else {
                    notifications.error(data.message, 'Error');
                }
                
            } catch (error) {
                console.error('Error:', error);
                notifications.error('An error occurred while changing password', 'Error');
            }
        },
        
        clearPasswordFields() {
            this.newPassword = "";
            this.confirmPassword = "";
        },
        
        async changePassword() {
            // Validate passwords
            if (!this.newPassword || !this.confirmPassword) {
                notifications.warning('Please fill in all password fields', 'Validation Error');
                return;
            }
            
            if (this.newPassword !== this.confirmPassword) {
                notifications.error('Passwords do not match', 'Validation Error');
                return;
            }
            
            if (this.newPassword.length < 6) {
                notifications.warning('Password must be at least 6 characters long', 'Validation Error');
                return;
            }
            
            try {
                const formData = new FormData();
                formData.append('email', this.userEmail);
                formData.append('new_password', this.newPassword);
                
                const response = await fetch('./change_password', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const contentType = response.headers.get("content-type");
                if (!contentType || !contentType.includes("application/json")) {
                    throw new Error("Response is not JSON");
                }
                
                const result = await response.json();
                
                if (result.success) {
                    notifications.success('Password changed successfully', 'Success');
                    this.closePasswordModal();
                } else {
                    notifications.error(result.message || 'Failed to change password', 'Error');
                }
            } catch (error) {
                notifications.error(`Failed to change password: ${error.message}`, 'Error');
            }
        },
        
        // Validation function to check for duplicates and empty values
        validateDocumentSymbols(inputString, fieldName) {
            if (!inputString || inputString.trim() === '') {
                notifications.warning(`Please enter at least one document symbol in ${fieldName}`, 'Validation Error');
                return false;
            }
            
            // Split by new lines and clean - remove only leading/trailing spaces, preserve internal spaces
            const symbols = inputString
                .split('\n')
                .map(symbol => symbol.trim()) // Remove only leading and trailing spaces
                .filter(symbol => symbol !== '');
            
            if (symbols.length === 0) {
                notifications.warning(`Please enter at least one valid document symbol in ${fieldName}`, 'Validation Error');
                return false;
            }
            
            // Check for duplicates
            const uniqueSymbols = [...new Set(symbols)];
            if (uniqueSymbols.length !== symbols.length) {
                const duplicates = symbols.filter((symbol, index) => symbols.indexOf(symbol) !== index);
                notifications.warning(`Duplicate document symbols found in ${fieldName}: ${[...new Set(duplicates)].join(', ')}`, 'Validation Error');
                return false;
            }
            
            return true;
        },
        
        // Helper function to clean document symbols by removing only leading/trailing spaces
        cleanDocumentSymbols(inputString) {
            return inputString
                .split('\n')
                .map(symbol => symbol.trim()) // Remove only leading and trailing spaces
                .filter(symbol => symbol !== '')
                .join('\n');
        },
        async loadSites(){
        // loading the sites
        try {
        const my_response1 = await fetch("./get_sites",{
            "method":"GET",
            });
            
            if (!my_response1.ok) {
                throw new Error(`HTTP error! status: ${my_response1.status}`);
            }
            
            const contentType = my_response1.headers.get("content-type");
            if (!contentType || !contentType.includes("application/json")) {
                throw new Error("Response is not JSON");
            }
            
        const my_data1 = await my_response1.json();
            
            // Robust error handling for malformed responses
            if (Array.isArray(my_data1)) {
        my_data1.forEach(element => {
                    if (element && typeof element === 'object' && element["code_site"]) {
                        this.site.push(element["code_site"]);
                    } else {
                        console.error("Unexpected site element type:", element);
                    }
                });
            } else {
                console.error("Expected array response for sites, got:", typeof my_data1, my_data1);
                notifications.warning("Unexpected response format from sites API", 'Response Error');
            }
        } catch (error) {
            notifications.error(`Failed to load sites: ${error.message}`, 'Load Error');
        }
        },
        async displayMetaData(){

        // Validate input before processing
        if (!this.validateDocumentSymbols(this.docsymbols, 'Display Metadata')) {
            return;
        }

        // just in case
        this.displayResult=false;

        // display Progress bar
        this.displayProgress1=true
        
        // No timeout for display metadata - let it run until completion

        // Just to refresh the UI
        this.listOfRecordsDiplayMetaData=[]
        
        let dataset = new FormData()
        
        // Clean the document symbols: remove all spaces and convert to uppercase
        let cleanedDocSymbols = this.cleanDocumentSymbols(this.docsymbols).toUpperCase();
            
        dataset.append('docsymbols',cleanedDocSymbols)
    
        // loading all the data
        try {
            const my_response = await fetch("./loading_symbol",{
                "method":"POST",
                "body":dataset
                });
                
            if (!my_response.ok) {
                throw new Error(`HTTP error! status: ${my_response.status}`);
            }
            
            const contentType = my_response.headers.get("content-type");
            if (!contentType || !contentType.includes("application/json")) {
                throw new Error("Response is not JSON");
            }
                
            const my_data = await my_response.json()

            // loading data
            my_data.forEach(element => {

                // check the length of the data array to see if we found the information
                
                // use case 1 : we found the data
                if (element && element["body"] && element["body"]["data"] && element["body"]["data"].length !== 0) {
                    this.listOfRecordsDiplayMetaData.push(element["body"]["data"])
                }
                // use case 2 : we did not find the data
                else if (element && element["body"] && element["body"]["data"] && element["body"]["data"].length === 0) {
                    // creation of the object
                    this.listOfRecordsDiplayMetaData.push(
                        [{
                            symbol: element["docsymbol"] || "Unknown",
                            agendas:"Not found",
                            sessions:"Not found",
                            distribution:"Not found",
                            area:"Not found",
                            subjects:"Not found",
                            job_numbers:"Not found",
                            title:"Not found",
                            publication_date:"Not found",
                            agenpublication_datedas:"Not found",
                            release_dates:"Not found"
                        }])
                }
                // use case 3 : API error or malformed response
                else {
                    console.error("Malformed API response:", element);
                    this.listOfRecordsDiplayMetaData.push(
                        [{
                            symbol: element && element["docsymbol"] ? element["docsymbol"] : "Error",
                            agendas:"API Error",
                            sessions:"API Error",
                            distribution:"API Error",
                            area:"API Error",
                            subjects:"API Error",
                            job_numbers:"API Error",
                            title:"API Error",
                            publication_date:"API Error",
                            agenpublication_datedas:"API Error",
                            release_dates:"API Error"
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

            // Validate input before processing
            if (!this.validateDocumentSymbols(this.docsymbols1, 'Create/Update Metadata')) {
                return;
            }

            // just in case
            this.displayResult1=false;

            // display Progress bar
            this.displayProgress2=true
            
            // No timeout for create/update - let it run until completion

            // Just to refresh the UI
            this.listOfResult1=[]
            


            // Clean the document symbols: remove all spaces
            this.docsymbols1 = this.cleanDocumentSymbols(this.docsymbols1);

            let dataset = new FormData()
            dataset.append('docsymbols1',this.docsymbols1)

            // loading all the data
            try {
                const my_response = await fetch("./create_metadata_ods",{
                    "method":"POST",
                    "body":dataset
                    });
                
                if (!my_response.ok) {
                    throw new Error(`HTTP error! status: ${my_response.status}`);
                }
                
                const contentType = my_response.headers.get("content-type");
                if (!contentType || !contentType.includes("application/json")) {
                    throw new Error("Response is not JSON");
                }
                
                const my_data = await my_response.json();

                // Robust error handling for malformed responses
                if (Array.isArray(my_data)) {
                my_data.forEach(elements => {
                        if (Array.isArray(elements)) {
                            this.listOfResult1 = this.listOfResult1.concat(elements);
                        } else if (elements && typeof elements === 'object') {
                            // Handle single object response
                            this.listOfResult1.push(elements);
                        } else {
                            console.error("Unexpected element type in response:", elements);
                            this.listOfResult1.push({
                                docsymbol: "Unknown",
                                text: "Malformed response data"
                            });
                        }
                    });
                } else {
                    console.error("Expected array response, got:", typeof my_data, my_data);
                    notifications.warning("Unexpected response format from server", 'Response Error');
                }
                
            } catch (error) {
                // Stop spinner on error
                this.displayProgress2=false
                notifications.error(error.message || error, 'Send Error');
            }
            finally{
                // display Progress bar
                this.displayProgress2=false
            }

            // display the results of the query
            this.displayResult1=true;
            
            // Show success notification
            notifications.success(`Processed ${this.listOfResult1.length} metadata records`, 'Send Complete');
            
            },

            async displayResultSendFile(){

                // Validate input before processing
                if (!this.validateDocumentSymbols(this.docsymbols2, 'Send Files')) {
                    return;
                }

                // just in case
                this.displayResult2=false;

                // display Progress bar
                this.displayProgress3=true
                
                // No timeout for send files - let it run until completion
                
                // Clean the document symbols: remove all spaces
                this.docsymbols2 = this.cleanDocumentSymbols(this.docsymbols2);

                let dataset = new FormData()
                dataset.append('docsymbols2',this.docsymbols2)
            
                // loading all the data
                try {
                    const my_response = await fetch("./exporttoodswithfile",{
                        "method":"POST",
                        "body":dataset
                        });
                    
                    if (!my_response.ok) {
                        throw new Error(`HTTP error! status: ${my_response.status}`);
                    }
                    
                    // Check if response is JSON
                    const contentType = my_response.headers.get('content-type');
                    if (!contentType || !contentType.includes('application/json')) {
                        throw new Error('Response is not JSON');
                    }
                                       
                    const my_data = await my_response.json()
                    // console.log(my_data)
                    // loading data
                    try {        
                    my_data.forEach(elements => {
                        //console.log(typeof(elements))
                        this.listOfResult2=this.listOfResult2.concat(elements)
                    })
                        
                    } catch (error) {
                        // Stop spinner on error
                        this.displayProgress3=false
                        notifications.error(error.message || error, 'Data Processing Error');
                    }
                    
                } catch (error) {
                    // Stop spinner on error
                    this.displayProgress3=false
                    notifications.error(error.message || error, 'Upload Error');
                }
                finally{
                    // Ensure spinner is always stopped
                    this.displayProgress3=false
                }

                // Always show results table if we have any results
                if (this.listOfResult2.length > 0){
                    this.displayResult2 = true;
                    notifications.success(`Processed ${this.listOfResult2.length} file(s)`, 'Upload Complete');
                } else {
                    this.displayResult2 = true;
                    notifications.warning('No files were processed', 'No Results');
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
                    
                    if (!my_response.ok) {
                        throw new Error(`HTTP error! status: ${my_response.status}`);
                    }
                    
                    const contentType = my_response.headers.get("content-type");
                    if (!contentType || !contentType.includes("application/json")) {
                        throw new Error("Response is not JSON");
                    }
                                    
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
                    
                    if (!my_response.ok) {
                        throw new Error(`HTTP error! status: ${my_response.status}`);
                    }
                    
                    const contentType = my_response.headers.get("content-type");
                    if (!contentType || !contentType.includes("application/json")) {
                        throw new Error("Response is not JSON");
                    }
                                    
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
        
                for (let j = 0; j < cols.length; j++) {
                    // Get the text content and replace line breaks with spaces for CSV
                    let cellText = cols[j].innerText;
                    // Replace line breaks with spaces to keep data in single column
                    cellText = cellText.replace(/\n/g, ' ');
                    // Escape commas and quotes for proper CSV formatting
                    if (cellText.includes(',') || cellText.includes('"') || cellText.includes('\n')) {
                        cellText = '"' + cellText.replace(/"/g, '""') + '"';
                    }
                    row.push(cellText);
                }
        
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
            // Clone the table to modify it for Excel export
            var tableElement = document.getElementById(tableName);
            var clonedTable = tableElement.cloneNode(true);
            
            // Process all cells to replace line breaks with spaces
            var cells = clonedTable.querySelectorAll('td, th');
            cells.forEach(function(cell) {
                var text = cell.textContent || cell.innerText;
                // Replace line breaks with spaces for Excel
                cell.textContent = text.replace(/\n/g, ' ');
            });
            
            var toExcel = clonedTable.outerHTML;
            var ctx = {
            worksheet: name || '',
            table: toExcel
            };
            var link = document.createElement("a");
            link.download = "export.xls";
            link.href = uri + base64(format(template, ctx))
            link.click();
        },
        
        // Chatbot methods
        async sendChatMessage() {
            if (!this.chatInput.trim() || this.chatLoading) {
                return;
            }
            
            const userMessage = this.chatInput.trim();
            
            // Add user message to chat
            this.chatMessages.push({
                type: 'user',
                text: userMessage,
                time: this.getCurrentTime()
            });
            
            // Clear input
            this.chatInput = '';
            
            // Set loading state
            this.chatLoading = true;
            
            // Scroll to bottom
            this.$nextTick(() => {
                this.scrollChatToBottom();
            });
            
            try {
                // Send message to backend
                const formData = new FormData();
                formData.append('message', userMessage);
                
                const response = await fetch('./chatbot', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const contentType = response.headers.get("content-type");
                if (!contentType || !contentType.includes("application/json")) {
                    throw new Error("Response is not JSON");
                }
                
                const data = await response.json();
                
                if (data.success) {
                    // Add bot response to chat
                    this.chatMessages.push({
                        type: 'bot',
                        text: data.response,
                        time: this.getCurrentTime()
                    });
                } else {
                    // Show error message
                    this.chatMessages.push({
                        type: 'bot',
                        text: `Sorry, I encountered an error: ${data.error || 'Unknown error'}. Please try again.`,
                        time: this.getCurrentTime()
                    });
                    notifications.error(data.error || 'Failed to get response from chatbot', 'Chatbot Error');
                }
                
            } catch (error) {
                console.error('Chatbot error:', error);
                this.chatMessages.push({
                    type: 'bot',
                    text: `Sorry, I'm having trouble connecting. Please check your connection and try again. Error: ${error.message}`,
                    time: this.getCurrentTime()
                });
                notifications.error('Failed to send message to chatbot', 'Connection Error');
            } finally {
                this.chatLoading = false;
                
                // Scroll to bottom after response
                this.$nextTick(() => {
                    this.scrollChatToBottom();
                });
            }
        },
        
        clearChat() {
            this.chatMessages = [];
            notifications.success('Chat cleared', 'Chat');
        },
        
        downloadChat() {
            if (this.chatMessages.length === 0) {
                notifications.warning('No chat messages to download', 'Download');
                return;
            }
            
            // Create chat history text
            let chatText = 'ODS Actions - Chat History\n';
            chatText += '='.repeat(50) + '\n';
            chatText += `Date: ${new Date().toLocaleString()}\n`;
            chatText += '='.repeat(50) + '\n\n';
            
            // Add initial bot message
            chatText += '[Bot] Hello! I\'m your ODS Actions assistant...\n';
            chatText += `Time: ${this.getCurrentTime()}\n\n`;
            
            // Add all messages
            this.chatMessages.forEach((msg, index) => {
                const sender = msg.type === 'user' ? 'You' : 'Bot';
                chatText += `[${sender}]\n`;
                chatText += `${msg.text}\n`;
                chatText += `Time: ${msg.time}\n`;
                chatText += '-'.repeat(50) + '\n\n';
            });
            
            // Create and download file
            const blob = new Blob([chatText], { type: 'text/plain' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `ods_chat_history_${new Date().toISOString().split('T')[0]}_${Date.now()}.txt`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            notifications.success('Chat history downloaded', 'Download');
        },
        
        getCurrentTime() {
            const now = new Date();
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            return `${hours}:${minutes}`;
        },
        
        formatMessage(text) {
            // Simple formatting - convert line breaks to <br>
            if (!text) return '';
            return text.replace(/\n/g, '<br>');
        },
        
        scrollChatToBottom() {
            const chatMessages = this.$refs.chatMessages;
            if (chatMessages) {
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        },
    },
})
  
let app_ods = new Vue({
  el: '#ods_component'
})

// Global function for manual modal password change
window.changePasswordManual = function() {
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const email = app_ods.userEmail;
    
    if (!newPassword || !confirmPassword) {
        notifications.error('Please fill in all fields', 'Validation Error');
        return;
    }
    
    if (newPassword !== confirmPassword) {
        notifications.error('Passwords do not match', 'Validation Error');
        return;
    }
    
    if (newPassword.length < 6) {
        notifications.error('Password must be at least 6 characters long', 'Validation Error');
        return;
    }
    
    // Send request to backend
    const formData = new FormData();
    formData.append('email', email);
    formData.append('new_password', newPassword);
    
    fetch('./change_password', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            notifications.success(data.message, 'Password Changed');
            document.getElementById('manual-modal').remove();
        } else {
            notifications.error(data.message, 'Error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        notifications.error('An error occurred while changing password', 'Error');
    });
};