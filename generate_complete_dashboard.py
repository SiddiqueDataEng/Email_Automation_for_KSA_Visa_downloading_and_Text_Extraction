# Generate complete dashboard HTML
html = open('templates/dashboard_complete.html', 'w', encoding='utf-8')

# Write the complete HTML
html.write("""<!DOCTYPE html>
<html>
<head>
    <title>Saudi eVisa Automation Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #f5f5f5; padding: 20px; }
        .container { max-width: 1600px; margin: 0 auto; }
        h1 { color: #333; margin-bottom: 30px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .stat-card h3 { color: #666; font-size: 14px; margin-bottom: 10px; }
        .stat-card .value { font-size: 36px; color: #2196F3; font-weight: bold; }
        .controls { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        button { background: #2196F3; color: white; border: none; padding: 12px 24px; border-radius: 4px; cursor: pointer; font-size: 14px; margin: 5px; }
        button:hover { background: #1976D2; }
        button:disabled { background: #ccc; cursor: not-allowed; }
        .btn-orange { background: #FF9800; } .btn-orange:hover { background: #F57C00; }
        .btn-green { background: #4CAF50; } .btn-green:hover { background: #388E3C; }
        .btn-gray { background: #666; } .btn-gray:hover { background: #555; }
        .btn-small { padding: 6px 12px; font-size: 12px; }
        .progress-bar { display: none; margin-top: 15px; }
        .progress-container { background: #e0e0e0; border-radius: 4px; height: 30px; position: relative; }
        .progress-fill { background: linear-gradient(90deg, #4CAF50, #8BC34A); height: 100%; width: 0%; transition: width 0.3s; }
        .progress-text { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 13px; font-weight: bold; }
        .tabs { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
        .tab { padding: 12px 24px; background: white; border-radius: 8px 8px 0 0; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .tab.active { background: #2196F3; color: white; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .section { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .search-bar { display: flex; gap: 10px; margin-bottom: 15px; flex-wrap: wrap; }
        .search-bar input { flex: 1; min-width: 200px; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
        table { width: 100%; border-collapse: collapse; font-size: 13px; }
        th { background: #2196F3; color: white; padding: 12px 8px; text-align: left; position: sticky; top: 0; }
        td { padding: 10px 8px; border-bottom: 1px solid #eee; }
        tr:hover { background: #f5f5f5; }
        .table-wrapper { max-height: 600px; overflow-y: auto; }
        .no-data { text-align: center; padding: 40px; color: #999; }
        .config-section { margin-top: 20px; display: none; }
        .config-section input { width: 100%; padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px; }
        .config-section label { display: block; margin-top: 10px; font-weight: bold; }
        .alert { padding: 10px; border-radius: 4px; margin-bottom: 15px; }
        .alert-info { background: #e3f2fd; border-left: 4px solid #2196F3; }
        .alert-success { background: #e8f5e9; border-left: 4px solid #4CAF50; }
        .alert-warning { background: #fff3e0; border-left: 4px solid #FF9800; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🇸🇦 Saudi eVisa Automation Dashboard</h1>
        
        <div id="alertContainer"></div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>Total Records</h3>
                <div class="value" id="totalProcessed">{{ stats.total_processed }}</div>
            </div>
            <div class="stat-card">
                <h3>Unique Employers</h3>
                <div class="value" id="employerCount">{{ stats.by_employer|length }}</div>
            </div>
            <div class="stat-card">
                <h3>Nationalities</h3>
                <div class="value" id="nationalityCount">{{ stats.by_nationality|length }}</div>
            </div>
            <div class="stat-card">
                <h3>This Month</h3>
                <div class="value" id="monthCount">0</div>
            </div>
        </div>
        
        <div class="controls">
            <div>
                <button onclick="processEmails(false)" id="processBtn">📧 Process New Emails</button>
                <button onclick="processEmails(true)" id="processAllBtn" class="btn-orange">🔄 Process All</button>
                <button onclick="openMainFolder()" class="btn-orange">📁 Open Folder</button>
                <button onclick="toggleAutoMonitor()" id="autoMonitorBtn" class="btn-green">🔔 Start Auto-Monitor</button>
                <button onclick="toggleConfig()" class="btn-gray">⚙️ Configure</button>
                <button onclick="refreshData()" class="btn-green">🔄 Refresh Data</button>
            </div>
            
            <div id="progressBar" class="progress-bar">
                <div class="progress-container">
                    <div id="progressFill" class="progress-fill"></div>
                    <div id="progressText" class="progress-text">0%</div>
                </div>
            </div>
            
            <div id="configSection" class="config-section">
                <div class="alert alert-warning">
                    <strong>⚠️ Important:</strong> Use Gmail App Password, not regular password!<br>
                    <small>Generate at: <a href="https://myaccount.google.com/apppasswords" target="_blank">myaccount.google.com/apppasswords</a></small>
                </div>
                <label>Email:</label>
                <input type="text" id="email" placeholder="your-email@gmail.com">
                <label>App Password:</label>
                <input type="password" id="password" placeholder="xxxx xxxx xxxx xxxx">
                <label>From Email:</label>
                <input type="text" id="fromEmail" placeholder="no-reply@mofa.gov.sa">
                <label>Subject Filter:</label>
                <input type="text" id="subjectFilter" placeholder="Saudi eVisa">
                <label>Save Path:</label>
                <input type="text" id="savePath" placeholder="\\\\COUNTER3\\Shared Data\\Visa_Slips_Automated">
                <label>Auto-Monitor Interval (seconds):</label>
                <input type="number" id="checkInterval" value="300" min="60">
                <button onclick="saveConfig()" style="margin-top: 10px;">💾 Save Configuration</button>
            </div>
        </div>
        
        <div class="tabs">
            <div class="tab active" onclick="switchTab('overview')">📊 Overview</div>
            <div class="tab" onclick="switchTab('records')">📋 All Records</div>
            <div class="tab" onclick="switchTab('recent')">🆕 Recent</div>
            <div class="tab" onclick="switchTab('employers')">🏢 By Employer</div>
            <div class="tab" onclick="switchTab('dates')">📅 By Date</div>
        </div>

        <div id="overview" class="tab-content active">
            <div class="section">
                <h3 style="margin-bottom: 15px;">📋 Activity Log</h3>
                <div id="logContainer" style="max-height: 400px; overflow-y: auto;"></div>
            </div>
        </div>

        <div id="records" class="tab-content">
            <div class="section">
                <h3 style="margin-bottom: 15px;">📋 All Visa Records</h3>
                <div class="search-bar">
                    <input type="text" id="searchInput" placeholder="Search by name, visa no, passport, employer..." onkeyup="searchRecords()">
                    <button onclick="exportToCSV()">📥 Export CSV</button>
                </div>
                <div class="table-wrapper">
                    <table id="recordsTable">
                        <thead>
                            <tr>
                                <th>Visa No</th>
                                <th>Name</th>
                                <th>Passport</th>
                                <th>Nationality</th>
                                <th>Employer</th>
                                <th>Valid From</th>
                                <th>Valid Until</th>
                                <th>Duration</th>
                                <th>Date</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="recordsBody">
                            <tr><td colspan="10" class="no-data">Loading...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <div id="recent" class="tab-content">
            <div class="section">
                <h3 style="margin-bottom: 15px;">🆕 Recent Records (Last 50)</h3>
                <div id="recentRecordsContainer"></div>
            </div>
        </div>

        <div id="employers" class="tab-content">
            <div class="section">
                <h3 style="margin-bottom: 15px;">🏢 Records by Employer</h3>
                <div id="employersContainer"></div>
            </div>
        </div>

        <div id="dates" class="tab-content">
            <div class="section">
                <h3 style="margin-bottom: 15px;">📅 Records by Date</h3>
                <div id="datesContainer"></div>
            </div>
        </div>
    </div>
""")

print("Part 1 written")
html.close()
print("Dashboard HTML generated!")
