Vue.component('dashboard-analytics', {
    template: `
        <div class="dashboard-container">
            <div class="dashboard-header">
                <h2>Analytics Dashboard</h2>
                <div class="date-filter">
                    <select v-model="selectedTimeRange" @change="loadAnalytics">
                        <option value="today">Today</option>
                        <option value="week">Last 7 Days</option>
                        <option value="month">Last 30 Days</option>
                        <option value="year">Last Year</option>
                    </select>
                </div>
            </div>
            
            <div class="summary-cards">
                <div class="card">
                    <h3>Total Actions</h3>
                    <p class="number">[[ analytics.totalActions ]]</p>
                </div>
                <div class="card">
                    <h3>Unique Users</h3>
                    <p class="number">[[ analytics.uniqueUsers ]]</p>
                </div>
                <div class="card">
                    <h3>Most Active User</h3>
                    <p class="number">[[ analytics.mostActiveUser ]]</p>
                </div>
            </div>
            
            <div class="charts-grid">
                <div class="chart-container">
                    <h3>Actions Over Time</h3>
                    <canvas ref="timeChart"></canvas>
                </div>
                <div class="chart-container">
                    <h3>Tasks per User</h3>
                    <canvas ref="userTasksChart"></canvas>
                </div>
            </div>
            
            <div class="recent-activity">
                <h3>Recent Activity</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>User</th>
                            <th>Action</th>
                            <th>Details</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="activity in analytics.recentActivity" :key="activity._id.$oid">
                            <td>[[ formatDate(activity.date.$date) ]]</td>
                            <td>[[ activity.user ]]</td>
                            <td>[[ activity.action ]]</td>
                            <td>[[ activity.details ]]</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    `,
    data() {
        return {
            selectedTimeRange: 'week',
            analytics: {
                totalActions: 0,
                uniqueUsers: 0,
                mostActiveUser: 'No activity',
                recentActivity: [],
                actionTypes: {},
                timeSeriesData: [],
                userTasks: {}
            },
            timeChart: null,
            userTasksChart: null
        }
    },
    mounted() {
        console.log('Dashboard component mounted');
        this.loadAnalytics();
    },
    methods: {
        async loadAnalytics() {
            try {
                console.log('Loading analytics for time range:', this.selectedTimeRange);
                const response = await fetch(`/get_analytics?timeRange=${this.selectedTimeRange}`);
                const data = await response.json();
                console.log('Received analytics data:', data);
                
                this.analytics = {
                    totalActions: data.totalActions,
                    uniqueUsers: data.uniqueUsers,
                    mostActiveUser: data.mostActiveUser,
                    recentActivity: data.recentActivity,
                    actionTypes: data.actionTypes,
                    timeSeriesData: data.timeSeriesData,
                    userTasks: data.userTasks
                };
                
                console.log('Updated component data:', this.analytics);
                
                this.updateCharts();
            } catch (error) {
                console.error('Error loading analytics:', error);
            }
        },
        updateCharts() {
            console.log('Updating charts');
            this.updateTimeChart();
            this.updateUserTasksChart();
        },
        updateTimeChart() {
            console.log('Updating time chart with data:', this.analytics.timeSeriesData);
            const ctx = this.$refs.timeChart.getContext('2d');
            
            if (this.timeChart) {
                this.timeChart.destroy();
            }
            
            this.timeChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: this.analytics.timeSeriesData.map(d => d.date),
                    datasets: [{
                        label: 'Actions',
                        data: this.analytics.timeSeriesData.map(d => d.count),
                        borderColor: '#4CAF50',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        },
        updateUserTasksChart() {
            console.log('Updating user tasks chart with data:', this.analytics.userTasks);
            const ctx = this.$refs.userTasksChart.getContext('2d');
            
            if (this.userTasksChart) {
                this.userTasksChart.destroy();
            }
            
            const labels = Object.keys(this.analytics.userTasks);
            const data = Object.values(this.analytics.userTasks);
            
            this.userTasksChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: [
                            '#4CAF50',
                            '#2196F3',
                            '#FFC107',
                            '#F44336',
                            '#9C27B0',
                            '#00BCD4',
                            '#FF9800',
                            '#795548'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: {
                                font: {
                                    size: 12
                                }
                            }
                        },
                        title: {
                            display: true,
                            text: 'Tasks Distribution by User',
                            font: {
                                size: 16
                            }
                        }
                    }
                }
            });
        },
        formatDate(dateString) {
            const date = new Date(dateString);
            return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
        }
    }
}); 