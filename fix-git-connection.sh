#!/bin/bash
# Git连接问题快速修复脚本

set -e

echo "🔧 修复Git连接问题..."

# 检查是否在正确的目录
if [ ! -d ".git" ]; then
    echo "❌ 当前目录不是Git仓库"
    echo "请先克隆项目或进入正确的目录"
    exit 1
fi

echo "📝 更新Git配置..."
# 方案1: 更新Git配置
git config --global http.sslVerify false
git config --global http.postBuffer 1048576000
git config --global http.lowSpeedLimit 0
git config --global http.lowSpeedTime 999999

echo "🔄 尝试重新拉取代码..."
# 方案2: 尝试重新拉取
if git pull origin main; then
    echo "✅ Git拉取成功！"
    echo "🚀 现在可以继续部署："
    echo "   chmod +x deploy-linux.sh"
    echo "   ./deploy-linux.sh"
    exit 0
fi

echo "⚠️ Git拉取失败，尝试手动下载..."

# 方案3: 手动下载项目文件
echo "📥 手动下载项目文件..."
cd ..

# 下载项目压缩包
if wget -O main.zip https://github.com/blackjackandLisa/OJ_web/archive/main.zip; then
    echo "✅ 项目文件下载成功"
    
    # 解压文件
    if unzip -o main.zip; then
        echo "✅ 项目文件解压成功"
        
        # 重命名目录
        if [ -d "OJ_web-main" ]; then
            rm -rf OJ_web
            mv OJ_web-main OJ_web
            echo "✅ 项目目录重命名完成"
        fi
        
        # 进入项目目录
        cd OJ_web
        echo "✅ 进入项目目录"
        
        echo ""
        echo "🎉 项目文件下载完成！"
        echo "🚀 现在可以继续部署："
        echo "   chmod +x deploy-linux.sh"
        echo "   ./deploy-linux.sh"
        
    else
        echo "❌ 项目文件解压失败"
        exit 1
    fi
else
    echo "❌ 项目文件下载失败"
    echo ""
    echo "🔧 请尝试以下解决方案："
    echo "1. 检查网络连接: ping github.com"
    echo "2. 使用代理: export http_proxy=http://proxy:port"
    echo "3. 手动上传代码到服务器"
    echo "4. 使用SSH方式: git remote set-url origin git@github.com:blackjackandLisa/OJ_web.git"
    exit 1
fi
