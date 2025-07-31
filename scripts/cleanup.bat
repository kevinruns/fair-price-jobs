@echo off
REM Cleanup Script for Job�co Application

echo 🧹 Cleanup Script for Job�co Application
echo ============================================

REM Check if we're in the right directory
if not exist "app.py" (
    echo ❌ Error: Please run this script from the project root directory
    pause
    exit /b 1
)

echo 🗑️  Starting cleanup process...

REM Remove Python cache files
echo 📁 Removing Python cache files...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul
echo ✅ Python cache files removed

REM Remove .pyc files
echo 🐍 Removing .pyc files...
del /s /q *.pyc 2>nul
echo ✅ .pyc files removed

REM Remove temporary files
echo 📄 Removing temporary files...
del /q *.tmp *.log *.bak 2>nul
echo ✅ Temporary files removed

REM Remove test databases
echo 🧪 Removing test databases...
del /q test_*.db 2>nul
echo ✅ Test databases removed

REM Clean up old log files (keep last 5)
echo 📋 Cleaning up old log files...
if exist "logs" (
    cd logs
    for /f "skip=5 delims=" %%i in ('dir /b /o-d *.log 2^>nul') do del "%%i" 2>nul
    cd ..
    echo ✅ Old log files cleaned up
)

REM Show disk usage
echo.
echo 📊 Disk usage summary:
echo ======================
echo Current directory size:
dir /s | find "File(s)"

echo.
echo 🎉 Cleanup complete!
echo.
echo 📝 What was cleaned:
echo    - Python cache directories (__pycache__)
echo    - Compiled Python files (.pyc)
echo    - Temporary files (.tmp, .log, .bak)
echo    - Test databases (test_*.db)
echo    - Old log files (kept last 5)
echo.
echo 💡 Next steps:
echo    - Run tests: python run_tests.py
echo    - Start application: python app.py
pause 
