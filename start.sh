#!/bin/bash

echo "=== NESA Agent安全测试平台启动脚本 ==="

# 检查conda是否已安装
if ! command -v conda &> /dev/null; then
    echo "❌ Conda未安装，请先安装Anaconda或Miniconda"
    exit 1
fi

# 检查demo环境是否存在
if ! conda env list | grep -q "demo"; then
    echo "❌ 未找到demo环境，请先运行 ./install.sh 进行安装"
    exit 1
fi

echo "✅ 检测到demo环境"

# 激活环境
echo "🔄 激活demo环境..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate demo

# 检查.env文件
if [ ! -f .env ]; then
    echo "⚠️  未找到.env文件，正在创建..."
    cp .env.example .env
    echo "🔧 请编辑.env文件设置您的API密钥，然后重新运行此脚本"
    echo "   必填项目：OPENAI_API_KEY"
    exit 1
fi

# 检查API密钥
if ! grep -q "OPENAI_API_KEY=sk-" .env && ! grep -q "OPENAI_API_KEY=.*[a-zA-Z0-9]" .env; then
    echo "⚠️  请在.env文件中设置有效的OPENAI_API_KEY"
    echo "   当前.env内容："
    cat .env | grep OPENAI_API_KEY || echo "   (未找到OPENAI_API_KEY设置)"
    exit 1
fi

echo "✅ 环境配置检查通过"

# 启动平台
echo "🚀 启动NESA Agent安全测试平台..."
echo "   访问地址: http://localhost:8000"
echo "   按 Ctrl+C 停止服务"
echo ""

python main.py