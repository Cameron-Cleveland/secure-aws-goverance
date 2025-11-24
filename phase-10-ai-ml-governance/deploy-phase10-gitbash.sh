#!/bin/bash

set -e

echo "🚀 DEPLOYING PHASE 10: AI/ML Governance (Git Bash Version)"
echo "======================================================================"

# Check if we're in the right directory
if [ ! -d "terraform" ]; then
    echo "❌ Error: terraform directory not found"
    echo "💡 Make sure you're in phase-10-ai-ml-governance directory"
    exit 1
fi

# Deploy Terraform
cd terraform
echo "📦 Deploying Terraform infrastructure..."
terraform init
terraform apply -auto-approve

echo "✅ Terraform deployment complete!"

# Test BedRock access
cd ../src/ai-scripts
echo "🤖 Testing BedRock connectivity..."

# Check if Python is available
if command -v python &> /dev/null; then
    PYTHON_CMD="python"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v py &> /dev/null; then
    PYTHON_CMD="py"
else
    echo "❌ Python not found. Installing dependencies..."
    # Try to set up Python
    if [ -f "/c/Users/$USERNAME/AppData/Local/Programs/Python/Python311/python.exe" ]; then
        PYTHON_CMD="/c/Users/$USERNAME/AppData/Local/Programs/Python/Python311/python.exe"
    else
        echo "⚠️  Python not available - skipping BedRock test"
        echo "💡 But Terraform deployment was successful!"
        exit 0
    fi
fi

echo "Using Python: $PYTHON_CMD"
$PYTHON_CMD bedrock_windows_test.py

echo ""
echo "🎉 PHASE 10 DEPLOYMENT COMPLETE!"
echo "======================================================================"
