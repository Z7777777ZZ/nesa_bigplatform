#!/bin/bash

echo "=== NESA Agent安全测试平台安装脚本 ==="

# 检查conda是否已安装
if ! command -v conda &> /dev/null; then
    echo "❌ Conda未安装，请先安装Anaconda或Miniconda"
    echo "下载地址: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

echo "✅ 检测到Conda已安装"

# 创建conda环境
echo "📦 创建conda环境 'demo'..."
conda create -n demo python=3.9 -y

# 激活环境
echo "🔄 激活环境..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate demo

# 安装依赖
echo "📥 安装Python依赖包..."
pip install -r requirements.txt

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p uploads
mkdir -p static/examples

# 复制示例文件
echo "📄 复制示例文件..."
cp examples/simple_agent.py static/examples/ 2>/dev/null || echo "⚠️  示例文件复制失败，请手动复制"

# 检查.env文件
if [ ! -f .env ]; then
    echo "⚙️  创建环境配置文件..."
    cp .env.example .env
    echo "⚠️  请编辑 .env 文件，添加您的API密钥"
else
    echo "✅ 环境配置文件已存在"
fi

echo ""
echo "🎉 安装完成！"
echo ""
echo "📋 接下来的步骤："
echo "1. 编辑 .env 文件，设置您的API密钥："
echo "   OPENAI_API_KEY=your_actual_api_key_here"
echo ""
echo "2. 激活conda环境："
echo "   conda activate demo"
echo ""
echo "3. 启动平台："
echo "   python main.py"
echo ""
echo "4. 访问浏览器："
echo "   http://localhost:8000"
echo ""
echo "💡 如需帮助，请查看 README.md 文件"