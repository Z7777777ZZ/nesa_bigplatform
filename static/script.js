// 全局变量
let testResults = null;

// DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeFileUpload();
    initializeForm();
});

// 初始化文件上传功能
function initializeFileUpload() {
    const fileInput = document.getElementById('agentFile');
    const fileUploadArea = document.getElementById('fileUploadArea');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');

    // 文件选择事件
    fileInput.addEventListener('change', function(e) {
        handleFileSelect(e.target.files[0]);
    });

    // 拖拽功能
    fileUploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        fileUploadArea.classList.add('dragover');
    });

    fileUploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        fileUploadArea.classList.remove('dragover');
    });

    fileUploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        fileUploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            if (file.name.endsWith('.py')) {
                fileInput.files = files;
                handleFileSelect(file);
            } else {
                showAlert('请选择Python文件 (.py)', 'warning');
            }
        }
    });

    function handleFileSelect(file) {
        if (file) {
            fileName.textContent = file.name;
            fileSize.textContent = formatFileSize(file.size);
            fileInfo.style.display = 'block';
            
            // 隐藏上传提示
            const uploadHelp = fileUploadArea.querySelector('.file-upload-help');
            uploadHelp.style.display = 'none';
        }
    }
}

// 初始化表单功能
function initializeForm() {
    const form = document.getElementById('uploadForm');
    const submitBtn = document.getElementById('submitBtn');

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // 验证表单
        if (!validateForm()) {
            return;
        }

        // 开始测试
        startSecurityTest();
    });
}

// 验证表单
function validateForm() {
    const fileInput = document.getElementById('agentFile');
    const testMethods = document.querySelectorAll('input[name="test_methods"]:checked');

    if (!fileInput.files.length) {
        showAlert('请选择要测试的Agent文件', 'warning');
        return false;
    }

    if (testMethods.length === 0) {
        showAlert('请至少选择一种测试方法', 'warning');
        return false;
    }

    return true;
}

// 开始安全测试
async function startSecurityTest() {
    const form = document.getElementById('uploadForm');
    const submitBtn = document.getElementById('submitBtn');
    const progressCard = document.getElementById('progressCard');
    const resultsCard = document.getElementById('resultsCard');

    // 隐藏之前的结果
    resultsCard.style.display = 'none';
    
    // 显示进度
    progressCard.style.display = 'block';
    progressCard.classList.add('fade-in');
    
    // 禁用提交按钮
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>测试进行中...';

    try {
        // 准备表单数据
        const formData = new FormData(form);
        
        // 模拟测试进度
        await simulateTestProgress();
        
        // 发送请求
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.status === 'success') {
            testResults = result;
            displayResults(result);
        } else {
            throw new Error(result.message || '测试失败');
        }

    } catch (error) {
        showAlert('测试过程中发生错误: ' + error.message, 'danger');
        console.error('Test error:', error);
    } finally {
        // 恢复按钮状态
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-play me-2"></i>开始安全测试';
        
        // 隐藏进度
        progressCard.style.display = 'none';
    }
}

// 模拟测试进度
async function simulateTestProgress() {
    const progressBar = document.getElementById('progressBar');
    const currentTest = document.getElementById('currentTest');
    
    const testSteps = [
        '解析Agent代码结构...',
        '检测提示词注入漏洞...',
        '分析工具返回值安全性...',
        '扫描敏感数据暴露...',
        '检测代码注入风险...',
        '评估权限升级可能性...',
        '生成安全报告...'
    ];

    for (let i = 0; i < testSteps.length; i++) {
        currentTest.textContent = testSteps[i];
        progressBar.style.width = `${((i + 1) / testSteps.length) * 100}%`;
        
        // 随机延迟模拟真实测试时间
        await new Promise(resolve => setTimeout(resolve, 800 + Math.random() * 400));
    }
}

// 显示测试结果
function displayResults(result) {
    const resultsCard = document.getElementById('resultsCard');
    const resultsContent = document.getElementById('resultsContent');

    // 生成结果HTML
    const resultsHTML = generateResultsHTML(result);
    resultsContent.innerHTML = resultsHTML;

    // 显示结果卡片
    resultsCard.style.display = 'block';
    resultsCard.classList.add('fade-in');

    // 滚动到结果区域
    resultsCard.scrollIntoView({ behavior: 'smooth', block: 'start' });

    // 绑定下载报告按钮
    const downloadBtn = document.getElementById('downloadReportBtn');
    downloadBtn.addEventListener('click', downloadReport);
    
    // 绑定详细信息展开/折叠功能
    bindDetailToggle();
}

// 生成结果HTML
function generateResultsHTML(result) {
    const report = result.report;
    const summary = report.executive_summary;
    const testDetails = result.test_details;
    const agentInfo = result.agent_info;
    
    let html = `
        <!-- 测试详情信息 -->
        <div class="mb-4">
            <div class="card">
                <div class="card-header">
                    <h6 class="mb-0">
                        <button class="btn btn-link text-decoration-none p-0" type="button" 
                                data-bs-toggle="collapse" data-bs-target="#testDetailsCollapse">
                            <i class="fas fa-info-circle me-2"></i>测试详情信息
                            <i class="fas fa-chevron-down float-end"></i>
                        </button>
                    </h6>
                </div>
                <div id="testDetailsCollapse" class="collapse">
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <p><strong>文件名:</strong> ${testDetails.file_name}</p>
                                <p><strong>文件大小:</strong> ${formatFileSize(testDetails.file_size)}</p>
                                <p><strong>选择的测试:</strong> ${testDetails.selected_tests.length}项</p>
                            </div>
                            <div class="col-md-6">
                                <p><strong>发现工具:</strong> ${testDetails.execution_details.tools_found}个</p>
                                <p><strong>发现提示词:</strong> ${testDetails.execution_details.prompts_found}个</p>
                                <p><strong>静态漏洞:</strong> ${testDetails.execution_details.static_vulnerabilities}个</p>
                            </div>
                        </div>
                        <div class="mt-3">
                            <strong>测试项目:</strong>
                            <ul class="mt-2">
                                ${testDetails.selected_tests.map(test => `<li>${getTestDisplayName(test)}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 概览指标 -->
        <div class="result-summary">
            <div class="result-metric">
                <h3>整体风险等级</h3>
                <div class="value ${summary.overall_risk_level.toLowerCase()}">${summary.overall_risk_level}</div>
            </div>
            <div class="result-metric">
                <h3>测试通过率</h3>
                <div class="value">${summary.pass_rate}</div>
            </div>
            <div class="result-metric">
                <h3>总测试数</h3>
                <div class="value">${summary.total_tests}</div>
            </div>
            <div class="result-metric">
                <h3>风险分数</h3>
                <div class="value">${report.risk_assessment.percentage}%</div>
            </div>
        </div>

        <!-- Agent信息 -->
        <div class="mb-4">
            <div class="card">
                <div class="card-header">
                    <h6 class="mb-0">
                        <button class="btn btn-link text-decoration-none p-0" type="button" 
                                data-bs-toggle="collapse" data-bs-target="#agentInfoCollapse">
                            <i class="fas fa-robot me-2"></i>Agent结构分析
                            <i class="fas fa-chevron-down float-end"></i>
                        </button>
                    </h6>
                </div>
                <div id="agentInfoCollapse" class="collapse">
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <p><strong>Agent类型:</strong> ${agentInfo.agent_type}</p>
                                <p><strong>工具数量:</strong> ${agentInfo.tools.length}</p>
                                <p><strong>提示词数量:</strong> ${agentInfo.prompts.length}</p>
                            </div>
                            <div class="col-md-6">
                                <p><strong>LLM配置:</strong> ${Object.keys(agentInfo.llm_config).length}项</p>
                                <p><strong>静态漏洞:</strong> ${agentInfo.vulnerabilities.length}个</p>
                            </div>
                        </div>
                        
                        ${agentInfo.tools.length > 0 ? `
                            <div class="mt-3">
                                <strong>检测到的工具:</strong>
                                <div class="mt-2">
                                    ${agentInfo.tools.map(tool => `
                                        <div class="border rounded p-2 mb-2">
                                            <h6 class="mb-1">${tool.name}</h6>
                                            <p class="text-muted mb-1 small">${tool.description || '无描述'}</p>
                                            <small class="text-muted">参数: ${Object.keys(tool.parameters).length}个</small>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        ` : ''}
                        
                        ${agentInfo.vulnerabilities.length > 0 ? `
                            <div class="mt-3">
                                <strong>静态漏洞分析:</strong>
                                <ul class="mt-2">
                                    ${agentInfo.vulnerabilities.map(vuln => `<li class="text-warning">${vuln}</li>`).join('')}
                                </ul>
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        </div>

        <!-- 详细测试结果 -->
        <div class="mb-4">
            <h5><i class="fas fa-list-alt me-2"></i>详细测试结果</h5>
    `;

    // 添加每个测试结果
    for (const testResult of report.detailed_results) {
        const statusIcon = testResult.status === 'passed' ? 'fa-check-circle text-success' : 
                          testResult.status === 'failed' ? 'fa-times-circle text-danger' : 
                          'fa-exclamation-triangle text-warning';
        
        const findingClass = testResult.status === 'passed' ? 'finding-passed' : 
                            `finding-${testResult.severity}`;

        html += `
            <div class="security-finding ${findingClass}">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <h6 class="mb-0">
                        <i class="fas ${statusIcon} me-2"></i>
                        ${testResult.test_name}
                    </h6>
                    <span class="severity-badge severity-${testResult.severity}">${testResult.severity}</span>
                </div>
                <p class="mb-2">${testResult.description}</p>
                
                <!-- 测试详情折叠区域 -->
                <div class="mt-2">
                    <button class="btn btn-sm btn-outline-secondary" type="button" 
                            data-bs-toggle="collapse" data-bs-target="#testDetail_${testResult.test_name.replace(/\s+/g, '_')}">
                        <i class="fas fa-eye me-1"></i>查看测试详情
                    </button>
                </div>
                
                <div id="testDetail_${testResult.test_name.replace(/\s+/g, '_')}" class="collapse">
                    <div class="mt-3 p-3 bg-light rounded">
                        ${testResult.details ? generateTestDetails(testResult.details, testResult.test_name) : '<p class="text-muted mb-0">无详细测试数据</p>'}
                    </div>
                </div>
                
                ${testResult.recommendations && testResult.recommendations.length > 0 ? `
                    <div class="mt-3">
                        <small class="text-muted"><strong>修复建议:</strong></small>
                        <ul class="mb-0 mt-1">
                            ${testResult.recommendations.map(rec => `<li><small>${rec}</small></li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;
    }

    html += `
        </div>

        <!-- 安全建议 -->
        <div class="recommendations">
            <h6><i class="fas fa-lightbulb me-2"></i>优先修复建议</h6>
    `;

    if (report.recommendations.immediate_actions.length > 0) {
        html += `
            <p class="mb-2"><strong>立即行动:</strong></p>
            <ul>
                ${report.recommendations.immediate_actions.map(action => 
                    `<li>${action.action} <span class="severity-badge severity-${action.severity}">${action.severity}</span></li>`
                ).join('')}
            </ul>
        `;
    }

    if (report.recommendations.long_term_actions.length > 0) {
        html += `
            <p class="mb-2 mt-3"><strong>长期改进:</strong></p>
            <ul class="mb-0">
                ${report.recommendations.long_term_actions.map(action => 
                    `<li>${action.action}</li>`
                ).join('')}
            </ul>
        `;
    }

    html += `
        </div>

        <!-- 风险评估解释 -->
        <div class="mt-3">
            <p class="text-muted mb-0">
                <i class="fas fa-info-circle me-1"></i>
                ${report.risk_assessment.interpretation}
            </p>
        </div>
    `;

    return html;
}

// 下载报告
function downloadReport() {
    if (!testResults) {
        showAlert('没有可下载的报告', 'warning');
        return;
    }

    // 创建下载链接
    const reportContent = JSON.stringify(testResults.report, null, 2);
    const blob = new Blob([reportContent], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `agent_security_report_${new Date().getTime()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    showAlert('报告已下载', 'success');
}

// 显示警告消息
function showAlert(message, type = 'info') {
    // 移除现有的警告
    const existingAlert = document.querySelector('.custom-alert');
    if (existingAlert) {
        existingAlert.remove();
    }

    // 创建新的警告
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show custom-alert`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    // 插入到页面顶部
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);

    // 自动消失
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 10000);
}

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 生成测试详情HTML
function generateTestDetails(details, testName) {
    let html = '';
    
    // 根据不同的测试类型生成不同的详情显示
    if (testName.includes('Prompt Injection') || testName.includes('提示词注入')) {
        html += generatePromptInjectionDetails(details);
    } else if (testName.includes('Tool Response') || testName.includes('工具返回')) {
        html += generateToolResponseDetails(details);
    } else if (testName.includes('Sensitive Data') || testName.includes('敏感数据')) {
        html += generateSensitiveDataDetails(details);
    } else if (testName.includes('Code Injection') || testName.includes('代码注入')) {
        html += generateCodeInjectionDetails(details);
    } else if (testName.includes('Privilege') || testName.includes('权限')) {
        html += generatePrivilegeDetails(details);
    } else {
        // 通用详情显示
        html += generateGenericDetails(details);
    }
    
    return html;
}

// 提示词注入测试详情
function generatePromptInjectionDetails(details) {
    let html = '<h6>测试负载和结果:</h6>';
    
    if (details.tested_payloads) {
        html += '<div class="table-responsive"><table class="table table-sm">';
        html += '<thead><tr><th>测试负载</th><th>结果</th></tr></thead><tbody>';
        
        details.tested_payloads.forEach((payload, index) => {
            const isSuccess = payload.result && (
                payload.result.includes('system prompt') || 
                payload.result.includes('HACKED') || 
                payload.result.includes('configuration') ||
                payload.result.includes('CONFIRMED')
            );
            
            const executionType = payload.execution_type || 'unknown';
            const isReal = executionType === 'real' || executionType === 'normal';
            const isNormal = executionType === 'normal' || executionType === 'normal_failed';
            const isBaseline = payload.is_baseline || false;
            
            let typeLabel, typeClass;
            if (isNormal) {
                typeLabel = '✅ 正常输入';
                typeClass = 'badge bg-success';
            } else if (isReal) {
                typeLabel = '🔴 攻击测试';
                typeClass = 'badge bg-danger';
            } else {
                typeLabel = '📊 静态分析';
                typeClass = 'badge bg-secondary';
            }
            
            const resultId = `result_${index}_${Math.random().toString(36).substr(2, 9)}`;
            const showFullResult = false; // 永远不显示"查看完整结果"按钮
            const resultPreview = payload.result || '无响应';
            
            html += `
                <tr class="${isSuccess ? 'table-danger' : 'table-success'}">
                    <td style="max-width: 300px;">
                        <code class="small">${escapeHtml(payload.payload)}</code>
                        <br><span class="${typeClass} mt-1">${typeLabel}</span>
                    </td>
                    <td class="small">
                        <div class="result-preview">
                            <pre class="small mb-0" style="white-space: pre-wrap; max-height: 400px; overflow-y: auto; background-color: #f8f9fa; padding: 8px; border-radius: 4px;">${escapeHtml(resultPreview)}</pre>
                        </div>
                        <div class="mt-2">
                            ${isReal ? '<span class="badge bg-secondary">真实Agent执行结果</span>' : '<span class="badge bg-secondary">基于代码分析的预测</span>'}
                            ${payload.api_called ? ' <span class="badge bg-warning text-dark">🌐 API调用</span>' : ''}
                            ${payload.execution_time ? ` <span class="badge bg-info">⏱️ ${payload.execution_time.toFixed(2)}秒</span>` : ''}
                        </div>
                    </td>
                </tr>
            `;
            
            // 不再需要模态框，直接显示完整结果
        });
        
        html += '</tbody></table></div>';
    }
    
    if (details.vulnerable_prompts && details.vulnerable_prompts.length > 0) {
        html += '<h6 class="mt-3">发现的易受攻击提示词:</h6>';
        html += '<ul>';
        details.vulnerable_prompts.forEach(prompt => {
            html += `<li class="text-warning"><code>${escapeHtml(prompt.substring(0, 150))}...</code></li>`;
        });
        html += '</ul>';
    }
    
    return html;
}

// 工具返回注入测试详情
function generateToolResponseDetails(details) {
    let html = '<h6>工具安全分析:</h6>';
    
    if (details.vulnerable_tools && details.vulnerable_tools.length > 0) {
        html += '<div class="alert alert-warning">';
        html += '<strong>发现易受攻击的工具:</strong><ul class="mb-0 mt-2">';
        details.vulnerable_tools.forEach(tool => {
            html += `<li><strong>${tool.name}:</strong> ${tool.reason}</li>`;
        });
        html += '</ul></div>';
    } else {
        html += '<div class="alert alert-success">未发现明显的工具返回注入漏洞</div>';
    }
    
    return html;
}

// 敏感数据暴露详情
function generateSensitiveDataDetails(details) {
    let html = '<h6>敏感数据检测结果:</h6>';
    
    if (details.exposed_data && details.exposed_data.length > 0) {
        html += '<div class="alert alert-danger">';
        html += '<strong>检测到以下类型的敏感数据暴露:</strong><ul class="mb-0 mt-2">';
        details.exposed_data.forEach(dataType => {
            html += `<li class="text-danger">${dataType}</li>`;
        });
        html += '</ul></div>';
    } else {
        html += '<div class="alert alert-success">未检测到明显的敏感数据暴露</div>';
    }
    
    return html;
}

// 代码注入详情
function generateCodeInjectionDetails(details) {
    let html = '<h6>代码安全分析:</h6>';
    
    if (details.vulnerable_code && details.vulnerable_code.length > 0) {
        html += '<div class="alert alert-danger">';
        html += '<strong>检测到危险代码模式:</strong><ul class="mb-0 mt-2">';
        details.vulnerable_code.forEach(code => {
            html += `<li class="text-danger"><code>${code}</code></li>`;
        });
        html += '</ul></div>';
    } else {
        html += '<div class="alert alert-success">未检测到明显的代码注入风险</div>';
    }
    
    return html;
}

// 权限升级详情
function generatePrivilegeDetails(details) {
    let html = '<h6>权限风险分析:</h6>';
    
    if (details.risky_operations && details.risky_operations.length > 0) {
        html += '<div class="alert alert-warning">';
        html += '<strong>检测到以下风险操作:</strong><ul class="mb-0 mt-2">';
        details.risky_operations.forEach(op => {
            html += `<li class="text-warning">${op}</li>`;
        });
        html += '</ul></div>';
    } else {
        html += '<div class="alert alert-success">未检测到明显的权限升级风险</div>';
    }
    
    return html;
}

// 通用详情显示
function generateGenericDetails(details) {
    let html = '<h6>测试详情:</h6>';
    html += '<pre class="bg-light p-2 small">' + JSON.stringify(details, null, 2) + '</pre>';
    return html;
}

// 获取测试显示名称
function getTestDisplayName(testKey) {
    const displayNames = {
        'prompt_injection': '提示词注入测试',
        'tool_response_injection': '工具返回注入测试',
        'sensitive_data_exposure': '敏感数据暴露检测',
        'code_injection': '代码注入检测',
        'privilege_escalation': '权限升级检测'
    };
    return displayNames[testKey] || testKey;
}

// 绑定详细信息展开/折叠功能
function bindDetailToggle() {
    // Bootstrap的collapse功能会自动处理，这里可以添加额外的逻辑
    const collapseButtons = document.querySelectorAll('[data-bs-toggle="collapse"]');
    collapseButtons.forEach(button => {
        button.addEventListener('click', function() {
            const icon = this.querySelector('.fa-chevron-down, .fa-chevron-up');
            if (icon) {
                setTimeout(() => {
                    icon.classList.toggle('fa-chevron-down');
                    icon.classList.toggle('fa-chevron-up');
                }, 150);
            }
        });
    });
}

// HTML转义函数
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 复制内容到剪贴板
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showAlert('已复制到剪贴板', 'success');
    }).catch(() => {
        showAlert('复制失败', 'danger');
    });
}