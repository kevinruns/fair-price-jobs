@echo off
REM Quick Test Script for Job�co Application

echo 🧪 Running Quick Tests for Job�co Application...
echo ====================================================

REM Check if we're in the right directory
if not exist "app.py" (
    echo ❌ Error: Please run this script from the project root directory
    pause
    exit /b 1
)

REM Check if test files exist
if not exist "tests\test_app.py" (
    echo ❌ Error: tests\test_app.py not found
    pause
    exit /b 1
)

if not exist "run_tests.py" (
    echo ❌ Error: run_tests.py not found
    pause
    exit /b 1
)

echo 🔍 Running basic tests (excluding integration)...
python run_tests.py --quick --verbose

REM Store the exit code
set TEST_EXIT_CODE=%errorlevel%

echo.
echo 📊 Test Results:
echo ================

if %TEST_EXIT_CODE% equ 0 (
    echo ✅ All quick tests passed!
    echo 🎉 Application is ready for development
) else (
    echo ❌ Some tests failed!
    echo 🔧 Please check the output above for details
    echo 💡 You can run specific service tests with:
    echo    python run_tests.py --service [database^|user^|group^|tradesman^|job]
)

echo.
echo 📝 Next steps:
echo    - Run full tests: python run_tests.py
echo    - Start application: python app.py
echo    - View logs: type logs\app.log
pause 
