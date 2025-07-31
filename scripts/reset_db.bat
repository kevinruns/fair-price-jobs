@echo off
REM Database Reset Script for Job�co Application

echo 🔄 Resetting Job�co Application Database...
echo ================================================

REM Check if we're in the right directory
if not exist "app.py" (
    echo ❌ Error: Please run this script from the project root directory
    pause
    exit /b 1
)

REM Backup existing database if it exists
if exist "application.db" (
    echo 📦 Creating backup of existing database...
    copy "application.db" "backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.db"
    echo ✅ Backup created
)

REM Remove existing database
echo 🗑️  Removing existing database...
del /f "application.db" 2>nul

REM Initialize new database
echo 🏗️  Initializing new database...
python sql\init_db.py

if %errorlevel% equ 0 (
    echo ✅ Database initialized successfully
) else (
    echo ❌ Failed to initialize database
    pause
    exit /b 1
)

REM Load sample data
echo 📊 Loading sample data...
python sql\load_db.py

if %errorlevel% equ 0 (
    echo ✅ Sample data loaded successfully
) else (
    echo ❌ Failed to load sample data
    pause
    exit /b 1
)

echo.
echo 🎉 Database reset complete!
echo 📁 New database: application.db
echo 📊 You can now start the application with: python app.py
pause 
