#!/bin/bash
# Quick Test Script for Job�co Application

echo "🧪 Running Quick Tests for Job�co Application..."
echo "===================================================="

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check if test files exist
if [ ! -f "tests/test_app.py" ]; then
    echo "❌ Error: tests/test_app.py not found"
    exit 1
fi

if [ ! -f "run_tests.py" ]; then
    echo "❌ Error: run_tests.py not found"
    exit 1
fi

echo "🔍 Running basic tests (excluding integration)..."
python run_tests.py --quick --verbose

# Store the exit code
TEST_EXIT_CODE=$?

echo ""
echo "📊 Test Results:"
echo "================"

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All quick tests passed!"
    echo "🎉 Application is ready for development"
else
    echo "❌ Some tests failed!"
    echo "🔧 Please check the output above for details"
    echo "💡 You can run specific service tests with:"
    echo "   python run_tests.py --service [database|user|group|tradesman|job]"
fi

echo ""
echo "📝 Next steps:"
echo "   - Run full tests: python run_tests.py"
echo "   - Start application: python app.py"
echo "   - View logs: tail -f logs/app.log" 
