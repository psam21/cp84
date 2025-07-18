#!/usr/bin/env python3
"""
Deployment verification script for Streamlit Community Cloud
Run this before deploying to check for potential issues.
"""

import sys
import subprocess
import os

def check_syntax():
    """Check Python syntax for all files"""
    files = ['app.py', 'bitcoin_metrics.py', 'mempool_data.py', 'binance_data.py', 
             'bitfinex_data.py', 'multi_exchange.py', 'coinbase_data.py', 'kucoin_data.py']
    
    print("🔍 Checking Python syntax...")
    for file in files:
        if os.path.exists(file):
            try:
                result = subprocess.run([sys.executable, '-m', 'py_compile', file], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"  ✅ {file}")
                else:
                    print(f"  ❌ {file}: {result.stderr}")
                    return False
            except Exception as e:
                print(f"  ❌ {file}: {e}")
                return False
        else:
            print(f"  ⚠️  {file}: File not found")
    return True

def check_requirements():
    """Check if requirements.txt exists and is valid"""
    print("\n📦 Checking requirements.txt...")
    if not os.path.exists('requirements.txt'):
        print("  ❌ requirements.txt not found")
        return False
    
    with open('requirements.txt', 'r') as f:
        reqs = f.read().strip()
        if not reqs:
            print("  ❌ requirements.txt is empty")
            return False
        
        lines = reqs.split('\n')
        for line in lines:
            if line.strip() and not line.startswith('#'):
                print(f"  ✅ {line.strip()}")
    return True

def check_streamlit_config():
    """Check Streamlit configuration"""
    print("\n⚙️  Checking Streamlit configuration...")
    config_path = '.streamlit/config.toml'
    if os.path.exists(config_path):
        print(f"  ✅ {config_path} exists")
        # Check if it has required settings
        with open(config_path, 'r') as f:
            content = f.read()
            if 'headless = true' in content:
                print("  ✅ Headless mode enabled")
            else:
                print("  ⚠️  Headless mode not set")
    else:
        print(f"  ⚠️  {config_path} not found (optional)")
    return True

def check_imports():
    """Check critical imports work"""
    print("\n📚 Checking critical imports...")
    critical_imports = ['streamlit', 'pandas', 'plotly', 'requests']
    
    for module in critical_imports:
        try:
            result = subprocess.run([sys.executable, '-c', f'import {module}'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"  ✅ {module}")
            else:
                print(f"  ❌ {module}: {result.stderr}")
                return False
        except Exception as e:
            print(f"  ❌ {module}: {e}")
            return False
    return True

def check_git_status():
    """Check git status"""
    print("\n📝 Checking git status...")
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            if result.stdout.strip():
                print("  ⚠️  Uncommitted changes found:")
                for line in result.stdout.strip().split('\n'):
                    print(f"    {line}")
            else:
                print("  ✅ All changes committed")
        else:
            print("  ⚠️  Not a git repository or git not available")
    except Exception as e:
        print(f"  ⚠️  Git check failed: {e}")
    return True

def check_file_structure():
    """Check required files exist"""
    print("\n📁 Checking file structure...")
    required_files = ['app.py', 'requirements.txt']
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - REQUIRED FILE MISSING")
            return False
    
    optional_files = ['.gitignore', 'README.md', '.streamlit/config.toml']
    for file in optional_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ⚠️  {file} - Optional but recommended")
    return True

def main():
    """Run all checks"""
    print("🚀 Bitcoin Crypto Dashboard - Deployment Verification")
    print("=" * 55)
    
    checks = [
        check_file_structure,
        check_syntax,
        check_requirements,
        check_streamlit_config,
        check_imports,
        check_git_status
    ]
    
    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
    
    print("\n" + "=" * 55)
    if all_passed:
        print("🎉 All checks passed! Ready for deployment to Streamlit Community Cloud")
        print("\n📋 Deployment Steps:")
        print("1. Push to GitHub: git push origin main")
        print("2. Go to https://share.streamlit.io")
        print("3. Connect your repository")
        print("4. Deploy!")
    else:
        print("❌ Some checks failed. Please fix the issues above before deploying.")
    
    return all_passed

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
