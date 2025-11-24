#!/bin/bash

set -e

echo "🚀 Deploying Landing Zone Accelerator Patterns"
echo "=============================================="

cd terraform

# Initialize Terraform
echo "📦 Initializing Terraform..."
terraform init

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
echo "   ✅ AWS Config Organization Rules"
echo "   ✅ LZA Architecture Documentation"
echo ""
echo "🔗 LZA Architecture Doc: $(terraform output -raw lza_architecture_doc)"