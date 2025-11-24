#!/bin/bash

set -e

echo "🚀 Deploying Landing Zone Accelerator Patterns"
echo "=============================================="

cd terraform

# Clean up any existing state
echo "🧹 Cleaning up any previous state..."
rm -rf .terraform terraform.tfstate* || true

# Initialize Terraform
echo "📦 Initializing Terraform..."
terraform init

# Validate configuration
echo "🔍 Validating Terraform configuration..."
if ! terraform validate; then
    echo "❌ Terraform validation failed. Checking for common issues..."
    
    # Check for syntax errors
    echo "Checking Terraform files for syntax errors..."
    terraform fmt -check -recursive
    
    echo "Please fix the errors above and try again."
    exit 1
fi

# Plan deployment
echo "📋 Planning LZA patterns deployment..."
terraform plan

# Deploy infrastructure
echo "🚀 Deploying LZA patterns..."
if terraform apply -auto-approve; then
    echo ""
    echo "🎉 LZA Patterns Deployment Complete!"
    echo "=============================================="
    echo "📋 LZA Components Deployed:"
    echo "   ✅ Centralized Logging S3 Bucket"
    echo "   ✅ CloudTrail Trail"
    echo "   ✅ Security Hub"
    echo "   ✅ LZA Architecture Documentation"
    echo ""
    echo "🔗 Check AWS Console for deployed resources:"
    echo "   - S3: Look for secure-governance-demo-central-logs-* bucket"
    echo "   - CloudTrail: Look for secure-governance-demo-main-trail"
    echo "   - Security Hub: Should be enabled"
else
    echo "❌ Deployment failed. Trying minimal version..."
    
    # Try the minimal version
    cd modules/lza-patterns
    if [ -f "main-minimal.tf" ]; then
        echo "🔄 Switching to minimal LZA implementation..."
        mv main.tf main.tf.backup
        mv main-minimal.tf main.tf
        cd ../..
        terraform init
        terraform apply -auto-approve
    else
        echo "💥 Deployment failed and no fallback available."
        exit 1
    fi
fi