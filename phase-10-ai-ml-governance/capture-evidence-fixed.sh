#!/bin/bash
echo "📸 CAPTURING PHASE 10 EVIDENCE"
echo "================================="

# Navigate to terraform directory for outputs
cd terraform 2>/dev/null && echo "✓ In terraform directory" || echo "⚠ Already in terraform directory"

echo ""
echo "1. TERRAFORM OUTPUTS:"
terraform output 2>/dev/null || echo "No outputs defined or state not found"

echo ""
echo "2. TERRAFORM STATE RESOURCES:"
terraform state list 2>/dev/null || echo "State not accessible"

echo ""
echo "3. LAMBDA FUNCTION SEARCH:"
echo "Searching for Lambda functions..."
aws lambda list-functions --query 'Functions[?starts_with(FunctionName,`secure-governance`)].FunctionName' --output table

echo ""
echo "4. LAMBDA TEST (using first found function):"
LAMBDA_NAME=$(aws lambda list-functions --query 'Functions[?starts_with(FunctionName,`secure-governance`)].FunctionName' --output text | head -1)
if [ -n "$LAMBDA_NAME" ]; then
    echo "Testing Lambda: $LAMBDA_NAME"
    aws lambda invoke --function-name "$LAMBDA_NAME" --payload '{"test": true}' /tmp/phase10-evidence.json --cli-binary-format raw-in-base64-out
    echo "Lambda Response:"
    cat /tmp/phase10-evidence.json
    echo ""
else
    echo "❌ No Lambda function found"
fi

echo ""
echo "5. KMS KEY VERIFICATION:"
aws kms list-aliases --query 'Aliases[?starts_with(AliasName,`alias/secure-governance`)].AliasName' --output table

echo ""
echo "6. IAM ROLE VERIFICATION:"
aws iam list-roles --query 'Roles[?starts_with(RoleName,`secure-governance`)].RoleName' --output table

echo ""
echo "7. PROJECT STRUCTURE:"
find . -name "*.tf" -o -name "*.py" -o -name "*.zip" | grep -E "(main.tf|secure_ai_processor)" | sort | head -15

echo ""
echo "8. TERRAFORM WORKSPACE INFO:"
terraform workspace show 2>/dev/null || echo "No workspace"

echo ""
echo "✅ EVIDENCE CAPTURE COMPLETE"
