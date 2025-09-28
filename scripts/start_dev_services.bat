@echo off
echo 🚀 启动开发环境服务...

echo 📊 启动PostgreSQL和Redis...
docker-compose -f docker-compose.dev.yml up -d

echo ⏳ 等待服务启动...
timeout /t 5 /nobreak > nul

echo ✅ 服务启动完成！
echo 📊 PostgreSQL: localhost:5432
echo 📊 Redis: localhost:6379
echo.
echo 🔧 现在可以设置环境变量使用PostgreSQL:
echo    $env:DATABASE_URL="postgresql://oj_user:oj_password@localhost:5432/django_oj"
echo    $env:REDIS_URL="redis://localhost:6379/1"
echo.
echo 🛑 停止服务: docker-compose -f docker-compose.dev.yml down
