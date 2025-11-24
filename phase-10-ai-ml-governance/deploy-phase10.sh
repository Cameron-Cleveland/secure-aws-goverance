#!/bin/bash

set -e

echo "🚀 Deploying Phase 10: AI/ML Governance with AWS BedRock"
echo "=========================================================="

cd terraform

# Initialize Terraform
echo "📦 Initializing Terraform..."
terraform init

# Validate Terraform configuration
echo "🔍 Validating Terraform configuration..."
terraform validate

# Plan deployment
echo "📋 Planning deployment..."
terraform plan -out=phase10.plan

# Deploy infrastructure
echo "🚀 Deploying AI/ML Governance infrastructure..."
terraform apply -auto-approve phase10.plan

echo "🎉 Phase 10 Deployment Complete!"
echo "=========================================================="

# Run AI governance demonstrations
echo "🤖 Running AI Governance Demonstrations..."
cd ../src/ai-scripts

echo "1. Testing BedRock Governance..."
python3 bedrock_governance_demo.py

echo ""
echo "2. Setting up AI Guardrails..."
python3 ai_guardrails_setup.py

echo ""
echo "📊 AI/ML Governance Summary:"
echo "   ✅ BedRock IAM Roles & Policies"
echo "   ✅ AI Guardrails Configuration"
echo "   ✅ Responsible AI Framework"
echo "   ✅ Training Data Governance"
echo "   ✅ Compliance Monitoring"

