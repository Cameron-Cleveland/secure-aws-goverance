#!/bin/bash

set -e

echo "🚀 DEPLOYING PHASE 10: AI/ML Governance (Updated for Auto-Enablement)"
echo "======================================================================"

# Deploy Terraform
cd terraform
echo "📦 Deploying Terraform infrastructure..."
terraform init
terraform apply -auto-approve

echo "✅ Terraform deployment complete!"
echo "   - IAM Roles created"
echo "   - S3 buckets provisioned" 
echo "   - Governance policies deployed"

# Test BedRock access
cd ../src/ai-scripts
echo "🤖 Testing BedRock auto-enablement..."
python3 bedrock_actual_test.py

echo ""
echo "🎉 PHASE 10 DEPLOYMENT COMPLETE!"
echo "======================================================================"
echo "📋 WHAT'S BEEN DEPLOYED:"
echo "   ✅ IAM Governance Roles & Policies"
echo "   ✅ BedRock Model Access (Auto-enabled)"
echo "   ✅ AI Guardrails Framework"
echo "   ✅ Responsible AI Controls"
echo "   ✅ Compliance Monitoring"
echo ""
echo "🚀 Next: Your AI/ML Governance platform is ready!"
