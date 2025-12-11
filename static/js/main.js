let selectedType = null;
let selectedLogName = null;
let charts = {};

const palette = [
    '#4e79a7', '#f28e2b', '#e15759', '#76b7b2', '#59a14f', '#edc949', '#af7aa1', '#ff9da7',
    '#9c755f', '#bab0ab'
];

// Map backend log type names to frontend log type names
const logTypeMap = {
    'Apache Logs': 'apache',
    'Docker Logs': 'docker',
    'Ejabberd Logs': 'ejabberd',
    'MongoDB Logs': 'mongodb',
    'MySQL Logs': 'mysql',
    'Nginx Logs': 'nginx',
    'PostgreSQL Logs': 'postgresql',
    'Redis Logs': 'redis'
};

// Modal functions
function openModal(logType, logName) {
    selectedType = logType;
    selectedLogName = logName;
    document.getElementById('modalTitle').textContent = 'Upload ' + logName;
    document.getElementById('modalOverlay').classList.add('active');
    // Reset file input
    document.getElementById('fileInput').value = '';
    const uploadZone = document.querySelector('.upload-zone');
    const firstP = uploadZone.querySelector('p');
    if (firstP) {
        firstP.innerHTML = 'Supports .txt, .log, .csv, .xlsx files';
    }
}

function closeModal() {
    document.getElementById('modalOverlay').classList.remove('active');
    // Reset file input
    document.getElementById('fileInput').value = '';
    const uploadZone = document.querySelector('.upload-zone');
    const firstP = uploadZone.querySelector('p');
    if (firstP) {
        firstP.innerHTML = 'Supports .txt, .log, .csv, .xlsx files';
    }
}

// Close modal when clicking outside
document.addEventListener('click', function(e) {
    const modal = document.getElementById('modalOverlay');
    if (e.target === modal) {
        closeModal();
    }
});

// Close modal with Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeModal();
    }
});

document.querySelectorAll('.log-card').forEach(card => {
    card.addEventListener('click', function() {
        document.querySelectorAll('.log-card').forEach(c => c.classList.remove('selected'));
        this.classList.add('selected');
        const logType = this.dataset.type;
        const logName = this.querySelector('h3').textContent;
        openModal(logType, logName);
        // Hide dashboard if it's visible and show main container and header
        document.getElementById('dashboard').classList.remove('active');
        document.getElementById('mainContainer').classList.remove('main-container-hidden');
        document.getElementById('mainHeader').classList.remove('header-hidden');
    });
});

document.getElementById('fileInput').addEventListener('change', function(e) {
    if (e.target.files.length > 0) {
        const fileName = e.target.files[0].name;
        const sizeKB = (e.target.files[0].size / 1024).toFixed(2);
        const uploadZone = document.querySelector('.upload-zone');
        const firstP = uploadZone.querySelector('p');
        if (firstP) {
            firstP.innerHTML = 'Selected: <strong>' + fileName + '</strong> (' + sizeKB + ' KB)';
        }
    }
});

function goBackToMain() {
    document.getElementById('dashboard').classList.remove('active');
    document.getElementById('mainContainer').classList.remove('main-container-hidden');
    document.getElementById('mainHeader').classList.remove('header-hidden');
    // Reset scroll position
    window.scrollTo(0, 0);
}

function uploadFile() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    if (!file) {
        alert('Please select a file first');
        return;
    }
    
    // Map frontend log type to backend log type name
    const backendLogType = Object.keys(logTypeMap).find(key => logTypeMap[key] === selectedType) || selectedType;
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('log_type', backendLogType);
    closeModal();
    document.getElementById('loading').classList.add('active');
    document.getElementById('dashboard').classList.remove('active');
    fetch('/analyze', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('loading').classList.remove('active');
        if (data.error) {
            alert('Error: ' + data.error);
            if (selectedLogName) {
                openModal(selectedType, selectedLogName);
            }
            return;
        }
        if (data.success && data.analysis) {
            displayResults(data);
        } else {
            alert('Error: Invalid response from server');
            if (selectedLogName) {
                openModal(selectedType, selectedLogName);
            }
        }
    })
    .catch(error => {
        document.getElementById('loading').classList.remove('active');
        alert('Error analyzing file: ' + error);
        if (selectedLogName) {
            openModal(selectedType, selectedLogName);
        }
    });
}

function destroyChart(key) {
    if (charts[key]) {
        try {
            charts[key].destroy();
        } catch (e) {}
        delete charts[key];
    }
}

function buildTableFromList(rows, cols) {
    if (!rows || rows.length === 0) return '<div style="color:#718096;padding:1rem">No data</div>';
    let html = '<table><thead><tr>';
    cols.forEach(c => html += '<th>' + c.header + '</th>');
    html += '</tr></thead><tbody>';
    rows.forEach(r => {
        html += '<tr>';
        cols.forEach(c => html += '<td>' + (r[c.key] === undefined ? '' : r[c.key]) + '</td>');
        html += '</tr>';
    });
    html += '</tbody></table>';
    return html;
}

function displayResults(data) {
    console.log('Displaying results:', data);
    
    // Handle new backend response format
    const analysis = data.analysis || data;
    const backendLogType = data.log_type || 'Auto-detected';
    
    // Extract metrics from analysis object
    const totalLogs = analysis.total_logs || analysis.total_requests || 0;
    const errorCount = analysis.total_errors || analysis.error_count || 0;
    const warningCount = analysis.total_warnings || analysis.warning_count || 0;
    const noticeCount = analysis.total_notices || analysis.notice_count || 0;
    const infoCount = analysis.info_count || (totalLogs - errorCount - warningCount - noticeCount);
    
    // Common metrics
    document.getElementById('totalLogs').textContent = totalLogs.toLocaleString();
    document.getElementById('errorCount').textContent = errorCount.toLocaleString();
    document.getElementById('warningCount').textContent = warningCount.toLocaleString();
    document.getElementById('noticeCount').textContent = noticeCount.toLocaleString();
    document.getElementById('infoCount').textContent = infoCount.toLocaleString();

    // DB-specific metrics: show only for mysql/postgresql/mongodb
    const dbTypes = ['mysql', 'postgresql', 'mongodb'];
    const frontendLogType = logTypeMap[backendLogType] || backendLogType.toLowerCase().replace(' logs', '');
    const showDB = dbTypes.includes(frontendLogType) || dbTypes.includes((selectedType || '').toLowerCase());

    document.getElementById('cardFailedLogins').style.display = showDB ? 'block' : 'none';
    document.getElementById('cardUniqueUsers').style.display = showDB ? 'block' : 'none';
    document.getElementById('cardActiveUsers').style.display = showDB ? 'block' : 'none';
    document.getElementById('cardQueryErrors').style.display = showDB ? 'block' : 'none';

    if (showDB) {
        document.getElementById('failedLogins').textContent = (analysis.failed_logins || 0).toLocaleString();
        document.getElementById('uniqueUsers').textContent = (analysis.unique_users || 0).toLocaleString();
        document.getElementById('activeUsers').textContent = (analysis.active_users_24h || analysis.active_users || 0).toLocaleString();
        document.getElementById('queryErrors').textContent = (analysis.total_query_errors || 0).toLocaleString();
    }

    // Alerts / Root causes
    const alertPanel = document.getElementById('alertPanel');
    const alertList = document.getElementById('alertList');
    alertList.innerHTML = '';
    if (analysis.root_causes && analysis.root_causes.length > 0) {
        analysis.root_causes.forEach(rc => {
            const li = document.createElement('li');
            li.textContent = rc;
            alertList.appendChild(li);
        });
        alertPanel.style.display = 'block';
        if (analysis.root_causes.some(x => x.toLowerCase().includes('high'))) {
            alertPanel.className = 'alert-panel error';
        } else if (analysis.root_causes.some(x => x.toLowerCase().includes('moderate'))) {
            alertPanel.className = 'alert-panel warning';
        } else {
            alertPanel.className = 'alert-panel';
        }
    } else {
        alertPanel.style.display = 'none';
    }

    // Level distribution (pie) - use log_level_distribution or level_distribution
    destroyChart('levelChart');
    const levelCtx = document.getElementById('levelChart').getContext('2d');
    const levels = analysis.log_level_distribution || analysis.level_distribution || analysis.log_by_levels || analysis.logs_by_level || {};
    const labels = Object.keys(levels);
    const values = labels.map(l => levels[l]);
    const colors = labels.map((_, i) => palette[i % palette.length]);
    
    if (labels.length > 0 && values.some(v => v > 0)) {
        charts['levelChart'] = new Chart(levelCtx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: colors,
                    hoverOffset: 8
                }]
            },
            options: {
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    } else {
        levelCtx.canvas.parentElement.innerHTML = '<div style="color:#718096;padding:2rem;text-align:center">No level distribution data available</div>';
    }

    // Time series (line) - use logs_over_time, log_levels_over_time, or time_series
    destroyChart('timeChart');
    const timeCtx = document.getElementById('timeChart').getContext('2d');
    const timeSeries = analysis.logs_over_time || analysis.log_levels_over_time || analysis.time_series || analysis.query_volume_over_time || [];
    
    if (timeSeries.length > 0) {
        // Build 0-23 filled array for stable x-axis if using hours
        const hours = Array.from({ length: 24 }, (_, i) => i);
        const hourMap = {};
        timeSeries.forEach(d => {
            const hour = d.hour !== undefined ? d.hour : (d.time ? parseInt(d.time.split(':')[0]) : null);
            if (hour !== null && hour !== undefined) {
                hourMap[hour] = d.count || d.volume || 0;
            }
        });
        const hourCounts = hours.map(h => hourMap[h] || 0);
        
        charts['timeChart'] = new Chart(timeCtx, {
            type: 'line',
            data: {
                labels: hours.map(h => (h < 10 ? '0' : '') + h + ':00'),
                datasets: [{
                    label: 'Logs per hour',
                    data: hourCounts,
                    tension: 0.3,
                    fill: true
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    } else {
        timeCtx.canvas.parentElement.innerHTML = '<div style="color:#718096;padding:2rem;text-align:center">No time series data available</div>';
    }

    // Extra charts (status codes / top errors / top ips)
    const extra = document.getElementById('extraCharts');
    extra.innerHTML = '';
    
    // Status codes chart
    if (analysis.status_codes && analysis.status_codes.length > 0) {
        const panel = document.createElement('div');
        panel.className = 'chart-panel';
        panel.innerHTML = '<div class="chart-title">Top Status Codes</div><div class="chart-subtitle">Most frequent response statuses</div><div class="chart-container"><canvas id="statusChart"></canvas></div>';
        extra.appendChild(panel);
        const ctx = document.getElementById('statusChart').getContext('2d');
        const scLabels = analysis.status_codes.map(s => s.status);
        const scValues = analysis.status_codes.map(s => s.count);
        destroyChart('statusChart');
        charts['statusChart'] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: scLabels,
                datasets: [{
                    label: 'Count',
                    data: scValues,
                    backgroundColor: palette[0]
                }]
            },
            options: {
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    } else if (analysis.status_distribution && Object.keys(analysis.status_distribution).length > 0) {
        const panel = document.createElement('div');
        panel.className = 'chart-panel';
        panel.innerHTML = '<div class="chart-title">Status Distribution</div><div class="chart-subtitle">HTTP status codes</div><div class="chart-container"><canvas id="statusChart"></canvas></div>';
        extra.appendChild(panel);
        const ctx = document.getElementById('statusChart').getContext('2d');
        const scLabels = Object.keys(analysis.status_distribution);
        const scValues = Object.values(analysis.status_distribution);
        destroyChart('statusChart');
        charts['statusChart'] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: scLabels,
                datasets: [{
                    label: 'Count',
                    data: scValues,
                    backgroundColor: palette[0]
                }]
            },
            options: {
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Top errors table
    const eTable = document.getElementById('errorTable');
    const eTableContent = document.getElementById('errorTableContent');
    if (analysis.top_errors && analysis.top_errors.length > 0) {
        eTable.style.display = 'block';
        eTableContent.innerHTML = buildTableFromList(analysis.top_errors, [
            { header: 'Error Message', key: 'message' },
            { header: 'Count', key: 'count' }
        ]);
    } else {
        eTable.style.display = 'none';
        eTableContent.innerHTML = '';
    }

    // Top IPs table
    const ipTable = document.getElementById('ipTable');
    const ipTableContent = document.getElementById('ipTableContent');
    if (analysis.top_ips && analysis.top_ips.length > 0) {
        ipTable.style.display = 'block';
        ipTableContent.innerHTML = buildTableFromList(analysis.top_ips, [
            { header: 'IP', key: 'ip' },
            { header: 'Count', key: 'count' }
        ]);
    } else if (analysis.top_client_ips && analysis.top_client_ips.length > 0) {
        ipTable.style.display = 'block';
        ipTableContent.innerHTML = buildTableFromList(analysis.top_client_ips.map(ip => ({ip: ip.ip, count: ip.requests})), [
            { header: 'IP', key: 'ip' },
            { header: 'Requests', key: 'count' }
        ]);
    } else {
        ipTable.style.display = 'none';
        ipTableContent.innerHTML = '';
    }

    // Failed login examples (DB-specific)
    const failedPanel = document.getElementById('failedTablePanel');
    const failedContent = document.getElementById('failedTableContent');
    if (showDB && analysis.failed_login_examples && analysis.failed_login_examples.length > 0) {
        failedPanel.style.display = 'block';
        failedContent.innerHTML = buildTableFromList(analysis.failed_login_examples, [
            { header: 'Message', key: 'message' },
            { header: 'Count', key: 'count' }
        ]);
    } else {
        failedPanel.style.display = 'none';
        failedContent.innerHTML = '';
    }

    // Top users (DB-specific)
    const topUsersPanel = document.getElementById('topUsersPanel');
    const topUsersContent = document.getElementById('topUsersContent');
    if (showDB && (analysis.top_users && analysis.top_users.length > 0 || analysis.top_active_users && analysis.top_active_users.length > 0)) {
        topUsersPanel.style.display = 'block';
        const users = analysis.top_users || analysis.top_active_users || [];
        topUsersContent.innerHTML = buildTableFromList(users.map(u => ({user: u.user, count: u.count || u.queries})), [
            { header: 'User', key: 'user' },
            { header: 'Count', key: 'count' }
        ]);
    } else {
        topUsersPanel.style.display = 'none';
        topUsersContent.innerHTML = '';
    }

    // Update dashboard title based on log type
    let logTypeName = backendLogType || 'Log';
    
    // Handle special cases
    if (logTypeName.toLowerCase() === 'auto-detected') {
        logTypeName = 'Log';
    }
    
    // Format the log type name (capitalize first letter, handle camelCase)
    const formattedLogType = logTypeName
        .toLowerCase()
        .split(/[-_\s]+/)
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
    
    document.getElementById('dashboardTitle').textContent = formattedLogType + ' Log Analysis Results';

    // Hide main container and header, show dashboard (full page)
    document.getElementById('mainHeader').classList.add('header-hidden');
    document.getElementById('mainContainer').classList.add('main-container-hidden');
    document.getElementById('dashboard').classList.add('active');
    // Scroll to top of dashboard page
    window.scrollTo(0, 0);

    // update sidebar active (select detected log type if provided)
    try {
        const detected = frontendLogType;
        document.querySelectorAll('.sidebar-item').forEach(it => {
            it.classList.remove('active');
            if (it.dataset.type === detected) it.classList.add('active');
        });
    } catch (e) {}
}

// sidebar click to switch type (UI only)
document.querySelectorAll('.sidebar-item').forEach(it => {
    it.addEventListener('click', function() {
        document.querySelectorAll('.sidebar-item').forEach(s => s.classList.remove('active'));
        this.classList.add('active');
    });
});
