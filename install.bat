@echo off
echo === NESA Agent安全测试平台安装脚本 ===

REM 检查conda是否已安装
where conda >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Conda未安装，请先安装Anaconda或Miniconda
    echo 下载地址: https://docs.conda.io/en/latest/miniconda.html
    pause
    exit /b 1
)

echo ✅ 检测到Conda已安装

REM 创建conda环境
echo 📦 创建conda环境 'demo'...
call conda create -n demo python=3.9 -y

REM 激活环境
echo 🔄 激活环境...
call conda activate demo

REM 安装依赖
echo 📥 安装Python依赖包...
pip install -r requirements.txt

REM 创建必要的目录
echo 📁 创建必要的目录...
if not exist uploads mkdir uploads
if not exist static\examples mkdir static\examples

REM 复制示例文件
echo 📄 复制示例文件...
copy examples\simple_agent.py static\examples\ >nul 2>nul

REM 检查.env文件
if not exist .env (
    echo ⚙️  创建环境配置文件...
    copy .env.example .env
    echo ⚠️  请编辑 .env 文件，添加您的API密钥
) else (
    echo ✅ 环境配置文件已存在
)

echo.
echo 🎉 安装完成！
echo.
echo 📋 接下来的步骤：
echo 1. 编辑 .env 文件，设置您的API密钥：
echo    OPENAI_API_KEY=your_actual_api_key_here
echo.
echo 2. 激活conda环境：
echo    conda activate demo
echo.
echo 3. 启动平台：
echo    python main.py
echo.
echo 4. 访问浏览器：
echo    http://localhost:8000
echo.
echo 💡 如需帮助，请查看 README.md 文件
pause