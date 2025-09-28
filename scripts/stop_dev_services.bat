@echo off
echo 🛑 停止开发环境服务...

docker-compose -f docker-compose.dev.yml down

echo ✅ 服务已停止！
