@echo off
echo ========================================
echo PDF 转 Word 工具 - 启动脚本
echo ========================================
echo.

echo [1/2] 启动后端服务...
start cmd /k "cd backend && python app.py"

echo 等待后端服务启动...
timeout /t 3 /nobreak >nul

echo [2/2] 启动前端服务...
start cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo 服务启动完成！
echo 后端地址: http://localhost:5000
echo 前端地址: http://localhost:3000
echo ========================================
echo.
echo 按任意键退出...
pause >nul
