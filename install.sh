#!/bin/bash

# BlammoBot Installation Script
# Automates dependency installation and setup

set -e  # Exit on any error

echo "🤖 BlammoBot Installation Script"
echo "================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ and try again."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1-2)
echo "✅ Found Python $PYTHON_VERSION"

# Check Python version (require 3.8+)
if [[ $(echo "$PYTHON_VERSION >= 3.8" | bc -l 2>/dev/null || echo "0") != "1" ]]; then
    echo "⚠️  Python 3.8+ is recommended. Current version: $PYTHON_VERSION"
fi

# Create virtual environment
echo ""
echo "📦 Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "ℹ️  Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
echo "✅ Virtual environment activated"

# Upgrade pip
echo ""
echo "🔄 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✅ Dependencies installed from requirements.txt"
else
    echo "⚠️  requirements.txt not found. Installing core dependencies manually..."
    pip install PythonTwitchBotFramework pandas requests urllib3
    pip install "websockets<13.0"  # Compatibility fix
    echo "✅ Core dependencies installed"
fi

# Create necessary directories
echo ""
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p mods
mkdir -p commands
echo "✅ Directories created"

# Check for private data directory
echo ""
echo "🔍 Checking for private data directory..."
if [ -d "../blammo-bot-private" ]; then
    echo "✅ Private data directory found: ../blammo-bot-private"
else
    echo "⚠️  Private data directory not found: ../blammo-bot-private"
    echo "   This directory should contain:"
    echo "   - trivia.csv (trivia questions database)"
    echo "   - scramble.csv (scramble words database)"
    echo "   - user_data.csv (user points and stats)"
    echo "   - timestamps.csv (command timestamps)"
    echo "   - record_data.csv (game records)"
    echo ""
    echo "   You can create example files with:"
    echo "   mkdir -p ../blammo-bot-private"
    echo "   python3 create_example_data.py  # (if available)"
fi

# Check configuration
echo ""
echo "⚙️  Checking configuration..."
if [ -f "configs/config.json" ]; then
    echo "✅ Configuration file found: configs/config.json"
    
    # Check if OAuth token is set
    if grep -q "your_oauth_token_here" configs/config.json; then
        echo "⚠️  OAuth token needs to be set in configs/config.json"
        echo "   Get your IRC token from: https://twitchapps.com/tmi/"
    else
        echo "✅ OAuth token appears to be configured"
    fi
else
    echo "⚠️  Configuration file not found: configs/config.json"
    echo "   Please create the configuration file before running the bot"
fi

# Run tests
echo ""
echo "🧪 Running tests..."
if [ -d "tests" ] && [ -f "tests/run_tests.py" ]; then
    python tests/run_tests.py
    echo "✅ All tests passed"
else
    echo "ℹ️  Test suite not found, skipping tests"
fi

# Installation complete
echo ""
echo "🎉 Installation Complete!"
echo "========================="
echo ""
echo "Next steps:"
echo "1. Set up your OAuth token in configs/config.json"
echo "   - Get token from: https://twitchapps.com/tmi/"
echo "   - Replace 'your_oauth_token_here' with your token"
echo ""
echo "2. Configure your bot settings in configs/config.json"
echo "   - Set your Twitch username in 'nick'"
echo "   - Set channels to join in 'channels'"
echo ""
echo "3. Create private data directory (if needed):"
echo "   mkdir -p ../blammo-bot-private"
echo ""
echo "4. Run the bot:"
echo "   ./venv/bin/python main.py"
echo ""
echo "5. Or run with scheduler (monitors stream status):"
echo "   ./venv/bin/python scheduler.py"
echo ""
echo "For troubleshooting, check logs.log or run tests:"
echo "   ./venv/bin/python tests/run_tests.py"
echo ""
echo "Happy botting! 🤖"