# NESA Agent安全测试平台

一个专门用于检测和评估LangChain Agent安全性的综合平台。支持自动化红队测试，包括提示词注入、工具返回注入、敏感数据暴露等多种安全威胁检测。

## 功能特性

### 🔍 全面的安全测试
- **提示词注入检测** - 检测Agent对恶意提示词的抵抗能力
- **工具返回注入测试** - 验证工具输出的安全处理
- **敏感数据暴露扫描** - 检查API密钥、密码等敏感信息泄露
- **代码注入漏洞检测** - 识别eval、exec等危险函数使用
- **权限升级风险评估** - 评估潜在的权限提升威胁

### 🛡️ 安全沙箱执行
- 资源限制（内存、CPU、时间）
- 网络访问控制
- 文件系统隔离
- 危险函数拦截

### 📊 详细安全报告
- 风险等级评估（Critical/High/Medium/Low）
- 详细漏洞描述和修复建议
- 可视化安全指标
- JSON/HTML格式报告导出

### 🎯 支持的框架
- LangChain Agent（当前版本）
- 计划支持：AutoGen、CrewAI、Camel等

## 快速开始

### 系统要求
- Python 3.8+
- 8GB+ RAM推荐
- Unix/Linux/macOS系统

### 安装依赖
```bash
# 创建conda环境
conda create -n demo python=3.9 -y

# 激活环境
conda activate demo

# 安装依赖
pip install -r requirements.txt
```

### 启动平台

**方式一：使用启动脚本（推荐）**
```bash
# Linux/macOS
./start.sh

# Windows
start.bat
```

**方式二：手动启动**
```bash
# 确保环境已激活
conda activate demo

# 启动平台
python main.py
```

平台将在 `http://localhost:8000` 启动

### 使用示例

1. **访问Web界面**
   打开浏览器访问 `http://localhost:8000`

2. **上传Agent文件**
   - 点击文件上传区域选择您的LangChain Agent Python文件
   - 或直接拖拽文件到上传区域

3. **选择测试方法**
   - 提示词注入测试
   - 工具返回注入测试  
   - 敏感数据暴露检测
   - 代码注入检测
   - 权限升级检测

4. **运行测试**
   点击"开始安全测试"按钮，系统将自动进行安全评估

5. **查看结果**
   - 实时查看测试进度
   - 获取详细的安全报告
   - 下载完整的测试结果

## 项目结构

```
demo_project/
├── main.py                 # FastAPI主应用
├── requirements.txt        # 依赖包列表
├── app/                    # 核心应用模块
│   ├── parsers/           # Agent代码解析器
│   │   └── langchain_parser.py
│   ├── security/          # 安全测试模块
│   │   └── red_team.py
│   ├── sandbox/           # 沙箱执行环境
│   │   └── executor.py
│   └── reports/           # 报告生成器
│       └── generator.py
├── templates/             # HTML模板
│   └── index.html
├── static/               # 静态资源
│   ├── style.css
│   ├── script.js
│   └── examples/
├── examples/             # 示例Agent文件
│   └── simple_agent.py
└── uploads/              # 用户上传文件存储
```

## Agent文件要求

### 支持的LangChain模式
- `initialize_agent()` 
- `AgentExecutor`
- `create_react_agent()`
- `create_openai_tools_agent()`

### 示例Agent结构
```python
from langchain.agents import initialize_agent, AgentType
from langchain.tools import tool
from langchain_openai import ChatOpenAI

@tool
def my_tool(input: str) -> str:
    \"\"\"工具描述\"\"\"
    return f"处理结果: {input}"

def create_agent():
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    tools = [my_tool]
    
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION
    )
    return agent
```

## 安全测试详解

### 1. 提示词注入测试
检测以下攻击模式：
- 指令覆盖攻击
- 系统提示词泄露
- 角色混淆攻击
- 上下文突破

### 2. 工具返回注入
验证工具输出处理：
- 返回值净化
- 特殊字符处理
- 结构化数据验证

### 3. 敏感数据检测
扫描以下信息类型：
- API密钥和令牌
- 数据库连接字符串
- 密码和凭证
- 私钥文件

### 4. 代码注入检测
识别危险函数：
- `eval()` / `exec()`
- `subprocess` 调用
- `os.system()` 使用
- 动态导入

### 5. 权限升级评估
分析风险操作：
- 文件系统访问
- 网络请求
- 系统命令执行
- 环境变量访问

## 安全等级说明

| 等级 | 描述 | 建议行动 |
|------|------|----------|
| **Critical** | 严重漏洞，可能导致系统完全妥协 | 立即修复 |
| **High** | 高风险漏洞，可能被利用获取敏感信息 | 优先修复 |
| **Medium** | 中等风险，可能在特定条件下被利用 | 计划修复 |
| **Low** | 低风险，建议改进但不紧急 | 定期维护 |

## 开发说明

### 扩展新的测试方法
1. 在 `app/security/red_team.py` 中添加新的测试函数
2. 更新 `test_methods` 字典
3. 在前端添加对应的选项

### 支持新的Agent框架
1. 在 `app/parsers/` 中创建新的解析器
2. 更新主应用的路由处理
3. 添加框架特定的安全测试

### 自定义沙箱环境
修改 `app/sandbox/executor.py` 中的安全策略：
- 资源限制
- 访问控制
- 函数拦截

## 注意事项

⚠️ **重要安全提醒**
- 本平台仅用于防御性安全测试
- 请勿将其用于恶意目的
- 上传的Agent文件在沙箱环境中执行
- 建议在隔离环境中运行平台

## 技术支持

如遇问题或需要帮助：
1. 查看日志文件定位问题
2. 确认Agent文件格式符合要求
3. 检查系统资源和权限配置

## 版本历史

### v1.0.0 (当前版本)
- 支持LangChain Agent安全测试
- 包含5种核心测试方法
- Web界面和API接口
- 详细安全报告生成

## 未来计划

- [ ] 支持更多Agent框架
- [ ] 机器学习驱动的威胁检测
- [ ] 持续集成/持续部署集成
- [ ] 团队协作和权限管理
- [ ] 测试结果历史对比