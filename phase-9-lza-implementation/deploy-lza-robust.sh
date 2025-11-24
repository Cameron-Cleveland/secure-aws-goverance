#!/bin/bash

set -e

echo "🚀 Deploying Landing Zone Accelerator Patterns"
echo "=============================================="

cd terraform

# Clean up any existing state (if needed)
echo "🧹 Cleaning up any previous state..."
rm -rf .terraform terraform.tfstate* || true

# Initialize Terraform
echo "📦 Initializing Terraform..."
terraform init

# Validate configuration
echo "🔍 Validating Terraform configuration..."
terraform validate

# Plan deployment
echo "📋 Planning LZA patterns deployment..."
terraform plan

# Deploy infrastructure
echo "🚀 Deploying LZA patterns..."
terraform apply -auto-approve

echo ""
echo "🎉 LZA Patterns Deployment Complete!"
echo "=============================================="
echo "📋 LZA Components Deployed:"
echo "   ✅ Centralized Logging S3 Bucket"
echo "   ✅ Organization CloudTrail"
echo "   ✅ Security Hub Organization Config"
echo "   ✅ LZA Architecture Documentation"
echo ""
echo "🔗 Check AWS Console for deployed resources"