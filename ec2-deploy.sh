#!/bin/bash

# EC2 Deployment Script for Flask Application
# This script sets up and deploys app.py on an EC2 instance
# Run this from your project root directory after cloning the repository

set -e  # Exit on error

echo "=== EC2 Flask Application Deployment Script ==="
echo ""

# Check if we're in the right directory (has app.py)
if [ ! -f "app.py" ]; then
    echo "ERROR: Please run this script from the project root directory"
    echo "Expected file: app.py"
    exit 1
fi

echo "✓ Project structure looks good"
echo ""

# Detect OS
OS_TYPE="unknown"
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS_TYPE="macos"
    echo "Detected: macOS (skipping system package updates)"
elif command -v yum &> /dev/null; then
    OS_TYPE="linux-yum"
    echo "Detected: Amazon Linux / CentOS (using yum)"
elif command -v dnf &> /dev/null; then
    OS_TYPE="linux-dnf"
    echo "Detected: Fedora / Amazon Linux 2023 (using dnf)"
elif command -v apt-get &> /dev/null; then
    OS_TYPE="linux-apt"
    echo "Detected: Ubuntu / Debian (using apt-get)"
else
    OS_TYPE="unknown"
    echo "WARNING: Could not detect Linux distribution."
    echo "Skipping system package updates. Assuming Python 3 is already installed."
fi
echo ""

# Update system packages (only on Linux)
if [[ "$OS_TYPE" == "linux-yum" ]]; then
    echo "Step 1: Updating system packages..."
    sudo yum update -y > /dev/null 2>&1
    echo "✓ System updated"
    echo ""
elif [[ "$OS_TYPE" == "linux-dnf" ]]; then
    echo "Step 1: Updating system packages..."
    sudo dnf update -y > /dev/null 2>&1
    echo "✓ System updated"
    echo ""
elif [[ "$OS_TYPE" == "linux-apt" ]]; then
    echo "Step 1: Updating system packages..."
    sudo apt-get update -y > /dev/null 2>&1
    echo "✓ System updated"
    echo ""
else
    echo "Step 1: Skipping system package updates (not a standard Linux distribution)"
    echo ""
fi

# Check and install Python
echo "Step 2: Checking Python..."
if ! command -v python3 &> /dev/null; then
    if [[ "$OS_TYPE" == "linux-yum" ]]; then
        echo "Installing Python..."
        sudo yum install -y python3 python3-pip > /dev/null 2>&1
    elif [[ "$OS_TYPE" == "linux-dnf" ]]; then
        echo "Installing Python..."
        sudo dnf install -y python3 python3-pip > /dev/null 2>&1
    elif [[ "$OS_TYPE" == "linux-apt" ]]; then
        echo "Installing Python..."
        sudo apt-get install -y python3 python3-pip python3-venv > /dev/null 2>&1
    else
        echo "ERROR: Python 3 is not installed and we cannot auto-install it."
        echo "Please install Python 3 manually and try again."
        exit 1
    fi
fi
echo "✓ Python $(python3 --version) is installed"
echo ""

# Setup Python virtual environment
echo "Step 3: Setting up Python virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

. .venv/bin/activate
pip install --upgrade pip --quiet
echo "✓ Virtual environment activated"
echo ""

# Install Python dependencies
echo "Step 4: Installing Python dependencies..."
if [ ! -f "requirements.txt" ]; then
    echo "WARNING: requirements.txt not found. Creating a basic one..."
    echo "Flask==3.0.0" > requirements.txt
    echo "gunicorn==23.0.0" >> requirements.txt
fi

pip install -r requirements.txt --quiet
echo "✓ Python dependencies installed"
echo ""

# Get EC2 public IP (using standard AWS metadata endpoint)
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "your-ec2-ip")

echo "=== Deployment Complete! ==="
echo ""
echo "Your Flask app is ready to run!"
echo ""
echo "To run the app in development mode:"
echo "  source .venv/bin/activate"
echo "  python3 app.py"
echo ""
echo "To run the app in production mode (recommended):"
echo "  source .venv/bin/activate"
echo "  gunicorn -w 4 -b 0.0.0.0:5000 app:app"
echo ""
echo "To run in background:"
echo "  nohup .venv/bin/python3 app.py > app.log 2>&1 &"
echo ""
echo "Or with gunicorn in background:"
echo "  nohup .venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 app:app > app.log 2>&1 &"
echo ""
echo "App will be accessible at: http://${PUBLIC_IP}:8000"
echo ""
echo "IMPORTANT: Make sure your EC2 Security Group allows:"
echo "  - Port 5000 (Custom TCP) from 0.0.0.0/0 (or your specific IP)"
echo ""
echo "To check if the app is running:"
echo "  ps aux | grep -E '(python|gunicorn)' | grep app"
echo ""
echo "To stop the app:"
echo "  pkill -f 'python.*app.py'"
echo "  # or"
echo "  pkill -f gunicorn"
echo ""

