// API 配置
const API_BASE = '/api/v1/api';
let currentModelId = null;

// 页面加载时检查登录状态
window.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('admin_token');
    if (!token) {
        window.location.href = 'login.html';
        return;
    }
    
    // 显示用户名
    const username = localStorage.getItem('admin_username');
    document.getElementById('username').textContent = username || 'Admin';
    
    // 加载数据
    loadModels();
});

// 获取认证头
function getAuthHeaders() {
    const token = localStorage.getItem('admin_token');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}

// 页面切换
function showPage(pageName) {
    // 隐藏所有页面
    document.querySelectorAll('.page-content').forEach(page => {
        page.style.display = 'none';
    });
    
    // 移除所有导航激活状态
    document.querySelectorAll('.sidebar-nav a').forEach(link => {
        link.classList.remove('active');
    });
    
    // 显示目标页面
    if (pageName === 'models') {
        document.getElementById('modelsPage').style.display = 'block';
        document.getElementById('pageTitle').textContent = 'AI 模型管理';
        document.querySelector('[href="#models"]').classList.add('active');
        loadModels();
    } else if (pageName === 'prompts') {
        document.getElementById('promptsPage').style.display = 'block';
        document.getElementById('pageTitle').textContent = '提示词管理';
        document.querySelector('[href="#prompts"]').classList.add('active');
        loadPrompts();
    }
}

// 退出登录
function logout() {
    if (confirm('确定要退出登录吗？')) {
        localStorage.clear();
        window.location.href = 'login.html';
    }
}

// ==================== AI 模型管理 ====================

// 加载模型列表
async function loadModels() {
    try {
        const response = await fetch(`${API_BASE}/admin/ai-models`, {
            headers: getAuthHeaders()
        });
        
        if (response.status === 401) {
            alert('登录已过期，请重新登录');
            logout();
            return;
        }
        
        const result = await response.json();
        
        if (result.code === 200) {
            displayModels(result.data.items);
        } else {
            showError('加载模型列表失败：' + result.message);
        }
    } catch (error) {
        showError('网络错误：' + error.message);
    }
}

// 显示模型列表
function displayModels(models) {
    const tbody = document.getElementById('modelsTableBody');
    
    if (models.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">暂无数据</td></tr>';
        return;
    }
    
    tbody.innerHTML = models.map(model => `
        <tr>
            <td><strong>${model.name}</strong></td>
            <td>${getProviderName(model.provider)}</td>
            <td><code>${model.model_id}</code></td>
            <td>
                <span class="badge ${model.is_active ? 'badge-active' : 'badge-inactive'}">
                    ${model.is_active ? '启用' : '禁用'}
                </span>
            </td>
            <td>${model.is_default ? '<i class="fas fa-star text-warning"></i>' : ''}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="editModel('${model.id}')">
                    <i class="fas fa-edit"></i> 编辑
                </button>
                <button class="btn btn-sm btn-outline-success" onclick="testModel('${model.id}')">
                    <i class="fas fa-vial"></i> 测试
                </button>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteModel('${model.id}', '${model.name}')">
                    <i class="fas fa-trash"></i> 删除
                </button>
            </td>
        </tr>
    `).join('');
}

// 获取提供商名称
function getProviderName(provider) {
    const names = {
        'openai': 'OpenAI',
        'anthropic': 'Anthropic',
        'doubao': '字节豆包',
        'qwen': '阿里通义'
    };
    return names[provider] || provider;
}

// 显示添加模型对话框
function showAddModelModal() {
    currentModelId = null;
    document.getElementById('modelModalTitle').textContent = '添加 AI 模型';
    document.getElementById('modelForm').reset();
    document.getElementById('modelIsActive').checked = true;
    document.getElementById('modelIsDefault').checked = false;
    new bootstrap.Modal(document.getElementById('modelModal')).show();
}

// 编辑模型
async function editModel(id) {
    try {
        const response = await fetch(`${API_BASE}/admin/ai-models`, {
            headers: getAuthHeaders()
        });
        
        const result = await response.json();
        if (result.code === 200) {
            const model = result.data.items.find(m => m.id === id);
            if (model) {
                currentModelId = id;
                document.getElementById('modelModalTitle').textContent = '编辑 AI 模型';
                document.getElementById('modelName').value = model.name;
                document.getElementById('modelProvider').value = model.provider;
                document.getElementById('modelModelId').value = model.model_id;
                document.getElementById('modelApiBase').value = model.api_base_url || '';
                document.getElementById('modelApiKey').value = ''; // 不显示原密钥
                document.getElementById('modelMaxTokens').value = model.max_tokens;
                document.getElementById('modelTemperature').value = model.temperature;
                document.getElementById('modelDescription').value = model.description || '';
                document.getElementById('modelIsActive').checked = model.is_active;
                document.getElementById('modelIsDefault').checked = model.is_default;
                
                new bootstrap.Modal(document.getElementById('modelModal')).show();
            }
        }
    } catch (error) {
        showError('加载模型信息失败：' + error.message);
    }
}

// 保存模型
async function saveModel() {
    const name = document.getElementById('modelName').value;
    const provider = document.getElementById('modelProvider').value;
    const modelId = document.getElementById('modelModelId').value;
    const apiBase = document.getElementById('modelApiBase').value;
    const apiKey = document.getElementById('modelApiKey').value;
    const maxTokens = parseInt(document.getElementById('modelMaxTokens').value);
    const temperature = parseInt(document.getElementById('modelTemperature').value);
    const description = document.getElementById('modelDescription').value;
    const isActive = document.getElementById('modelIsActive').checked;
    const isDefault = document.getElementById('modelIsDefault').checked;
    
    if (!name || !provider || !modelId) {
        alert('请填写必填字段');
        return;
    }
    
    // 编辑模式下，如果没有输入新密钥，则不更新
    if (!currentModelId && !apiKey) {
        alert('请输入 API Key');
        return;
    }
    
    const data = {
        name,
        provider,
        model_id: modelId,
        api_base_url: apiBase || null,
        max_tokens: maxTokens,
        temperature: temperature,
        description: description || null,
        is_active: isActive,
        is_default: isDefault
    };
    
    // 只在有新密钥时才包含
    if (apiKey) {
        data.api_key = apiKey;
    }
    
    try {
        let response;
        if (currentModelId) {
            // 更新
            response = await fetch(`${API_BASE}/admin/ai-models/${currentModelId}`, {
                method: 'PUT',
                headers: getAuthHeaders(),
                body: JSON.stringify(data)
            });
        } else {
            // 创建
            data.api_key = apiKey; // 创建时必须有
            response = await fetch(`${API_BASE}/admin/ai-models`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify(data)
            });
        }
        
        const result = await response.json();
        
        if (result.code === 200) {
            bootstrap.Modal.getInstance(document.getElementById('modelModal')).hide();
            loadModels();
            showSuccess(currentModelId ? '模型更新成功' : '模型创建成功');
        } else {
            showError(result.message || '操作失败');
        }
    } catch (error) {
        showError('网络错误：' + error.message);
    }
}

// 测试模型
async function testModel(id) {
    const btn = event.target.closest('button');
    const originalHtml = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 测试中...';
    btn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE}/admin/ai-models/${id}/test`, {
            method: 'POST',
            headers: getAuthHeaders()
        });
        
        const result = await response.json();
        
        if (result.code === 200) {
            showSuccess('连接测试成功！');
        } else {
            showError('连接测试失败：' + result.message);
        }
    } catch (error) {
        showError('测试失败：' + error.message);
    } finally {
        btn.innerHTML = originalHtml;
        btn.disabled = false;
    }
}

// 删除模型
async function deleteModel(id, name) {
    if (!confirm(`确定要删除模型「${name}」吗？此操作不可恢复。`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/admin/ai-models/${id}`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });
        
        const result = await response.json();
        
        if (result.code === 200) {
            loadModels();
            showSuccess('模型删除成功');
        } else {
            showError(result.message || '删除失败');
        }
    } catch (error) {
        showError('网络错误：' + error.message);
    }
}

// ==================== 提示词管理 ====================

// 加载提示词列表
async function loadPrompts() {
    try {
        const response = await fetch(`${API_BASE}/admin/ai-prompts`, {
            headers: getAuthHeaders()
        });
        
        if (response.status === 401) {
            alert('登录已过期，请重新登录');
            logout();
            return;
        }
        
        const result = await response.json();
        
        if (result.code === 200) {
            displayPrompts(result.data.items);
        } else {
            showError('加载提示词列表失败：' + result.message);
        }
    } catch (error) {
        showError('网络错误：' + error.message);
    }
}

// 显示提示词列表
function displayPrompts(prompts) {
    const tbody = document.getElementById('promptsTableBody');
    
    if (prompts.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">暂无数据</td></tr>';
        return;
    }
    
    tbody.innerHTML = prompts.map(prompt => `
        <tr>
            <td><strong>${prompt.name}</strong></td>
            <td>${getScenarioName(prompt.scenario)}</td>
            <td>
                <span class="badge ${prompt.is_active ? 'badge-active' : 'badge-inactive'}">
                    ${prompt.is_active ? '启用' : '禁用'}
                </span>
            </td>
            <td>${prompt.is_default ? '<i class="fas fa-star text-warning"></i>' : ''}</td>
            <td>
                <button class="btn btn-sm btn-outline-info" onclick="viewPrompt('${prompt.id}')">
                    <i class="fas fa-eye"></i> 查看
                </button>
            </td>
        </tr>
    `).join('');
}

// 获取场景名称
function getScenarioName(scenario) {
    const names = {
        'meeting_summary': '会议摘要',
        'flash_classify': '闪记分类',
        'action_extract': '行动项提取',
        'key_points': '关键要点',
        'general_chat': '通用对话'
    };
    return names[scenario] || scenario;
}

// 查看提示词详情
async function viewPrompt(id) {
    try {
        const response = await fetch(`${API_BASE}/admin/ai-prompts`, {
            headers: getAuthHeaders()
        });
        
        const result = await response.json();
        if (result.code === 200) {
            const prompt = result.data.items.find(p => p.id === id);
            if (prompt) {
                alert(`提示词模板：${prompt.name}\n\n场景：${getScenarioName(prompt.scenario)}\n\n内容：\n${prompt.prompt_template}`);
            }
        }
    } catch (error) {
        showError('加载提示词失败：' + error.message);
    }
}

// 显示添加提示词对话框（暂未实现）
function showAddPromptModal() {
    alert('提示词模板功能开发中，当前可通过数据库直接管理默认模板。');
}

// ==================== 工具函数 ====================

// 显示成功消息
function showSuccess(message) {
    // 简单的提示，可以换成更好的 UI
    alert('✅ ' + message);
}

// 显示错误消息
function showError(message) {
    alert('❌ ' + message);
}

