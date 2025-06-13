// 摩点爬虫Web UI JavaScript

class SpiderUI {
    constructor() {
        this.socket = null;
        this.currentTaskId = null;
        this.tasks = new Map();
        
        this.init();
    }
    
    init() {
        this.initSocket();
        this.initEventListeners();
        this.loadConfig();
        this.refreshTasks();
        this.refreshDatabaseStats();
    }
    
    initSocket() {
        this.socket = io();
        
        this.socket.on('connect', () => {
            console.log('WebSocket连接成功');
            this.updateConnectionStatus(true);
        });
        
        this.socket.on('disconnect', () => {
            console.log('WebSocket连接断开');
            this.updateConnectionStatus(false);
        });
        
        this.socket.on('task_update', (data) => {
            this.handleTaskUpdate(data);
        });
    }
    
    initEventListeners() {
        // 表单提交
        document.getElementById('crawl-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.startCrawl();
        });
        
        // 停止按钮
        document.getElementById('stop-btn').addEventListener('click', () => {
            this.stopCrawl();
        });
    }
    
    async loadConfig() {
        try {
            const response = await fetch('/api/config');
            const data = await response.json();
            
            if (data.success) {
                this.populateCategories(data.config.categories);
                this.setDefaultValues(data.config);
            }
        } catch (error) {
            console.error('加载配置失败:', error);
        }
    }
    
    populateCategories(categories) {
        const select = document.getElementById('category');
        select.innerHTML = '';
        
        categories.forEach(cat => {
            const option = document.createElement('option');
            option.value = cat.value;
            option.textContent = cat.label;
            select.appendChild(option);
        });
    }
    
    setDefaultValues(config) {
        document.getElementById('max-concurrent').value = config.max_concurrent;
        document.getElementById('delay-min').value = config.delay_min;
        document.getElementById('delay-max').value = config.delay_max;
    }
    
    async startCrawl() {
        const formData = {
            start_page: parseInt(document.getElementById('start-page').value),
            end_page: parseInt(document.getElementById('end-page').value),
            category: document.getElementById('category').value,
            max_concurrent: parseInt(document.getElementById('max-concurrent').value),
            delay_min: parseFloat(document.getElementById('delay-min').value),
            delay_max: parseFloat(document.getElementById('delay-max').value)
        };
        
        // 验证表单
        if (formData.start_page > formData.end_page) {
            this.showNotification('起始页不能大于结束页', 'error');
            return;
        }
        
        if (formData.delay_min > formData.delay_max) {
            this.showNotification('最小延迟不能大于最大延迟', 'error');
            return;
        }
        
        try {
            this.setButtonState(true);
            
            const response = await fetch('/api/start_crawl', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.currentTaskId = data.task_id;
                this.showCurrentTask();
                this.showNotification('爬虫任务已启动', 'success');
            } else {
                this.setButtonState(false);
                this.showNotification(data.message, 'error');
            }
        } catch (error) {
            this.setButtonState(false);
            this.showNotification('启动失败: ' + error.message, 'error');
        }
    }
    
    async stopCrawl() {
        if (!this.currentTaskId) return;
        
        try {
            const response = await fetch(`/api/stop_crawl/${this.currentTaskId}`, {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showNotification('任务已停止', 'warning');
                this.setButtonState(false);
            } else {
                this.showNotification(data.message, 'error');
            }
        } catch (error) {
            this.showNotification('停止失败: ' + error.message, 'error');
        }
    }
    
    handleTaskUpdate(data) {
        const { task_id, stats } = data;
        this.tasks.set(task_id, stats);
        
        if (task_id === this.currentTaskId) {
            this.updateCurrentTaskDisplay(stats);
        }
        
        this.updateSystemStats();
    }
    
    updateCurrentTaskDisplay(stats) {
        // 更新进度条
        const progress = Math.round(stats.progress || 0);
        document.getElementById('progress-bar').style.width = `${progress}%`;
        document.getElementById('progress-text').textContent = `${progress}%`;
        
        // 更新统计信息
        document.getElementById('pages-crawled').textContent = stats.pages_crawled || 0;
        document.getElementById('projects-found').textContent = stats.projects_found || 0;
        document.getElementById('projects-processed').textContent = stats.projects_processed || 0;
        document.getElementById('errors-count').textContent = stats.errors || 0;
        
        // 更新日志
        this.updateLogs(stats.logs || []);
        
        // 检查任务状态
        if (stats.status === 'completed' || stats.status === 'failed' || stats.status === 'stopped') {
            this.setButtonState(false);
            if (stats.status === 'completed') {
                this.showNotification('任务完成！', 'success');
            }
        }
    }
    
    updateLogs(logs) {
        const container = document.getElementById('log-container');
        
        // 清空现有日志
        container.innerHTML = '';
        
        if (logs.length === 0) {
            container.innerHTML = '<div class="text-muted text-center p-3">暂无日志</div>';
            return;
        }
        
        // 添加日志条目
        logs.forEach(log => {
            const logEntry = document.createElement('div');
            logEntry.className = `log-entry ${log.level}`;
            logEntry.innerHTML = `
                <span class="log-timestamp">[${log.timestamp}]</span>
                <span class="log-message">${log.message}</span>
            `;
            container.appendChild(logEntry);
        });
        
        // 滚动到底部
        container.scrollTop = container.scrollHeight;
    }
    
    updateSystemStats() {
        let active = 0, completed = 0, failed = 0;
        
        this.tasks.forEach(stats => {
            switch (stats.status) {
                case 'running':
                case 'starting':
                    active++;
                    break;
                case 'completed':
                    completed++;
                    break;
                case 'failed':
                case 'error':
                    failed++;
                    break;
            }
        });
        
        document.getElementById('active-tasks').textContent = active;
        document.getElementById('completed-tasks').textContent = completed;
        document.getElementById('failed-tasks').textContent = failed;
    }
    
    showCurrentTask() {
        const card = document.getElementById('current-task-card');
        const taskIdSpan = document.getElementById('current-task-id');
        
        card.style.display = 'block';
        taskIdSpan.textContent = this.currentTaskId.substring(0, 8);
        card.classList.add('fade-in');
    }
    
    setButtonState(running) {
        const startBtn = document.getElementById('start-btn');
        const stopBtn = document.getElementById('stop-btn');
        
        startBtn.disabled = running;
        stopBtn.disabled = !running;
        
        if (running) {
            startBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>运行中...';
        } else {
            startBtn.innerHTML = '<i class="bi bi-play-fill"></i> 开始爬取';
        }
    }
    
    updateConnectionStatus(connected) {
        const status = document.getElementById('connection-status');
        
        if (connected) {
            status.textContent = '已连接';
            status.className = 'badge bg-success me-2 connected';
        } else {
            status.textContent = '连接断开';
            status.className = 'badge bg-danger me-2 disconnected';
        }
    }
    
    showNotification(message, type = 'info') {
        const toast = document.getElementById('notification-toast');
        const messageEl = document.getElementById('toast-message');
        const icon = toast.querySelector('.toast-header i');
        
        messageEl.textContent = message;
        
        // 更新图标和颜色
        icon.className = `bi me-2 ${this.getIconClass(type)} ${this.getColorClass(type)}`;
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
    }
    
    getIconClass(type) {
        const icons = {
            'info': 'bi-info-circle',
            'success': 'bi-check-circle',
            'warning': 'bi-exclamation-triangle',
            'error': 'bi-x-circle'
        };
        return icons[type] || icons.info;
    }
    
    getColorClass(type) {
        const colors = {
            'info': 'text-primary',
            'success': 'text-success',
            'warning': 'text-warning',
            'error': 'text-danger'
        };
        return colors[type] || colors.info;
    }
    
    async refreshTasks() {
        try {
            const response = await fetch('/api/tasks');
            const data = await response.json();
            
            if (data.success) {
                this.updateHistoryTable(data.tasks);
            }
        } catch (error) {
            console.error('刷新任务失败:', error);
        }
    }
    
    updateHistoryTable(tasks) {
        const tbody = document.getElementById('history-table');
        
        if (tasks.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">暂无历史任务</td></tr>';
            return;
        }
        
        tbody.innerHTML = '';
        
        tasks.forEach(task => {
            const row = document.createElement('tr');
            const startTime = new Date(task.stats.start_time).toLocaleString();
            const statusBadge = this.getStatusBadge(task.stats.status);
            
            row.innerHTML = `
                <td><code>${task.task_id.substring(0, 8)}</code></td>
                <td>${statusBadge}</td>
                <td>${task.config.start_page}-${task.config.end_page}</td>
                <td>${task.config.category}</td>
                <td>${startTime}</td>
                <td>
                    <button class="btn btn-outline-primary btn-sm" onclick="downloadTaskResults('${task.task_id}')">
                        <i class="bi bi-download"></i>
                    </button>
                </td>
            `;
            
            tbody.appendChild(row);
        });
    }
    
    getStatusBadge(status) {
        const badges = {
            'running': '<span class="badge bg-success">运行中</span>',
            'completed': '<span class="badge bg-primary">已完成</span>',
            'failed': '<span class="badge bg-danger">失败</span>',
            'stopped': '<span class="badge bg-secondary">已停止</span>',
            'error': '<span class="badge bg-danger">错误</span>'
        };
        return badges[status] || '<span class="badge bg-secondary">未知</span>';
    }

    async refreshDatabaseStats() {
        """刷新数据库统计信息"""
        try {
            const response = await fetch('/api/database/stats');
            const data = await response.json();

            if (data.success) {
                this.updateDatabaseStats(data.stats);
            }
        } catch (error) {
            console.error('刷新数据库统计失败:', error);
        }
    }

    updateDatabaseStats(stats) {
        """更新数据库统计显示"""
        document.getElementById('db-total-projects').textContent = stats.total_projects || 0;
        document.getElementById('db-today-projects').textContent = stats.today_projects || 0;
        document.getElementById('db-week-projects').textContent = stats.week_projects || 0;
    }

    async viewDatabaseData() {
        """查看数据库数据"""
        try {
            const period = document.getElementById('time-period-select').value;
            const response = await fetch(`/api/database/projects?period=${period}&limit=10`);
            const data = await response.json();

            if (data.success) {
                this.displayDatabasePreview(data.projects);
            } else {
                this.showNotification(data.message, 'error');
            }
        } catch (error) {
            this.showNotification('查看数据失败: ' + error.message, 'error');
        }
    }

    displayDatabasePreview(projects) {
        """显示数据库数据预览"""
        const preview = document.getElementById('database-preview');
        const tbody = document.getElementById('database-preview-table');

        if (projects.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">暂无数据</td></tr>';
        } else {
            tbody.innerHTML = '';

            projects.forEach(project => {
                const row = document.createElement('tr');
                const crawlTime = new Date(project.crawl_time).toLocaleString();

                row.innerHTML = `
                    <td>${project.project_name || '未知'}</td>
                    <td>${project.category || '未知'}</td>
                    <td>¥${project.raised_amount || 0}</td>
                    <td>${project.backer_count || 0}</td>
                    <td>${crawlTime}</td>
                `;

                tbody.appendChild(row);
            });
        }

        preview.style.display = 'block';
    }

    async exportDatabaseData() {
        """导出数据库数据"""
        try {
            const period = document.getElementById('time-period-select').value;
            const url = `/api/database/export?period=${period}`;

            // 创建下载链接
            const link = document.createElement('a');
            link.href = url;
            link.download = `database_export_${period}_${new Date().toISOString().slice(0, 10)}.xlsx`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            this.showNotification('数据导出已开始', 'success');
        } catch (error) {
            this.showNotification('导出失败: ' + error.message, 'error');
        }
    }
}

// 全局函数
function downloadResults() {
    if (window.spiderUI && window.spiderUI.currentTaskId) {
        downloadTaskResults(window.spiderUI.currentTaskId);
    }
}

function downloadTaskResults(taskId) {
    window.open(`/api/download/${taskId}`, '_blank');
}

function clearLogs() {
    const container = document.getElementById('log-container');
    container.innerHTML = '<div class="text-muted text-center p-3">日志已清空</div>';
}

function refreshTasks() {
    if (window.spiderUI) {
        window.spiderUI.refreshTasks();
    }
}

function refreshDatabaseStats() {
    if (window.spiderUI) {
        window.spiderUI.refreshDatabaseStats();
    }
}

function viewDatabaseData() {
    if (window.spiderUI) {
        window.spiderUI.viewDatabaseData();
    }
}

function exportDatabaseData() {
    if (window.spiderUI) {
        window.spiderUI.exportDatabaseData();
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    window.spiderUI = new SpiderUI();
});
