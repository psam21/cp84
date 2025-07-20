#!/bin/bash
# Production deployment script for Portfolio Value Calculator

echo "🚀 Portfolio Value Calculator - Production Deployment"
echo "======================================================"

# Check Python version
echo "📋 Checking Python environment..."
python --version

# Check if virtual environment is active
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment active: $VIRTUAL_ENV"
else
    echo "⚠️  Virtual environment not detected"
fi

# Install/verify dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run basic import tests
echo "🔍 Testing core imports..."
python -c "
import sys
sys.path.append('.')
try:
    from pages.portfolio_ui import initialize_portfolio_session, get_portfolio_css
    from utils.portfolio_calculator import calculate_portfolio_values
    from utils.cache import cached_get_crypto_prices
    print('✅ All core components imported successfully')
except Exception as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"

# Test API connectivity
echo "🌐 Testing API connectivity..."
python -c "
import sys
sys.path.append('.')
try:
    from utils.diagnostics import test_api_connectivity
    results = test_api_connectivity()
    working_apis = sum(1 for status in results.values() if '✅' in str(status))
    total_apis = len(results)
    print(f'📊 API Status: {working_apis}/{total_apis} APIs working')
    if working_apis == 0:
        print('⚠️  Warning: No APIs are currently working')
    else:
        print('✅ At least one API is functional')
except Exception as e:
    print(f'⚠️  API test failed: {e}')
"

# Test Streamlit app syntax
echo "🖥️  Testing Streamlit app syntax..."
python -m py_compile app.py
if [ $? -eq 0 ]; then
    echo "✅ App syntax check passed"
else
    echo "❌ App syntax check failed"
    exit 1
fi

# Run the application for 5 seconds to test startup
echo "🏃 Testing application startup..."
timeout 10s streamlit run app.py --server.headless true &
STREAMLIT_PID=$!
sleep 5

# Check if Streamlit is still running
if kill -0 $STREAMLIT_PID 2>/dev/null; then
    echo "✅ Application started successfully"
    kill $STREAMLIT_PID
else
    echo "❌ Application failed to start"
    exit 1
fi

echo ""
echo "🎉 Production readiness check complete!"
echo "💡 Deploy with: streamlit run app.py"
echo "🌐 Access at: http://localhost:8501"
