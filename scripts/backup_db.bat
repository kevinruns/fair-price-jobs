@echo off
REM Database Backup Script for Job�co Application

echo 💾 Database Backup Script for Job�co Application
echo ===================================================

REM Check if we're in the right directory
if not exist "app.py" (
    echo ❌ Error: Please run this script from the project root directory
    pause
    exit /b 1
)

REM Check if database exists
if not exist "application.db" (
    echo ❌ Error: application.db not found
    pause
    exit /b 1
)

REM Create backup directory if it doesn't exist
set BACKUP_DIR=backups\%date:~-4,4%%date:~-10,2%%date:~-7,2%
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

REM Create timestamped backup
set TIMESTAMP=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_FILE=%BACKUP_DIR%\application_%TIMESTAMP%.db

echo 📦 Creating backup...
copy "application.db" "%BACKUP_FILE%"

if %errorlevel% equ 0 (
    echo ✅ Backup created successfully: %BACKUP_FILE%
    
    REM Show backup file size
    for %%A in ("%BACKUP_FILE%") do echo 📊 Backup size: %%~zA bytes
    
    REM Show backup directory contents
    echo.
    echo 📁 Backup directory contents:
    dir "%BACKUP_DIR%"
    
    echo ✅ Backup process complete!
) else (
    echo ❌ Failed to create backup
    pause
    exit /b 1
)

echo.
echo 📝 Backup information:
echo    - Location: %BACKUP_FILE%
echo    - Date: %date% %time%
echo.
echo 💡 To restore from backup:
echo    copy "%BACKUP_FILE%" application.db
pause 
