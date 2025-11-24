@echo off
echo 🚀 DEPLOYING PHASE 10: AI/ML Governance
echo ======================================================================
REM Deploy Terraform
cd terraform
echo 📦 Deploying Terraform infrastructure...
terraform init
terraform apply -auto-approve
REM Test BedRock access
cd ../src/ai-scripts
echo 🤖 Testing BedRock connectivity...
python bedrock_windows_test.py
echo.
echo 🎉 PHASE 10 DEPLOYMENT COMPLETE!
echo ======================================================================
pause
