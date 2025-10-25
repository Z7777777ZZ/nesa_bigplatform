@echo off
echo === NESA Agent安全测试平台启动脚本 ===

REM 检查conda是否已安装
where conda >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Conda未安装，请先安装Anaconda或Miniconda
    pause
    exit /b 1
)

REM 检查demo环境是否存在
conda env list | findstr "demo" >nul
if %errorlevel% neq 0 (
    echo ❌ 未找到demo环境，请先运行 install.bat 进行安装
    pause
    exit /b 1
)

echo ✅ 检测到demo环境

REM 激活环境
echo 🔄 激活demo环境...
call conda activate demo

REM 检查.env文件
if not exist .env (
    echo ⚠️  未找到.env文件，正在创建...
    copy .env.example .env
    echo 🔧 请编辑.env文件设置您的API密钥，然后重新运行此脚本
    echo    必填项目：OPENAI_API_KEY
    pause
    exit /b 1
)

REM 检查API密钥
findstr "OPENAI_API_KEY=.*[a-zA-Z0-9]" .env >nul
if %errorlevel% neq 0 (
    echo ⚠️  请在.env文件中设置有效的OPENAI_API_KEY
    echo    当前.env内容：
    type .env | findstr OPENAI_API_KEY
    pause
    exit /b 1
)

echo ✅ 环境配置检查通过

REM 启动平台
echo 🚀 启动NESA Agent安全测试平台...
echo    访问地址: http://localhost:8000
echo    按 Ctrl+C 停止服务
echo.

python main.py
pause