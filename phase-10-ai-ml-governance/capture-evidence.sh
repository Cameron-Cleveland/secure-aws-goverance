#!/bin/bash
echo "📸 CAPTURING PHASE 10 EVIDENCE"

echo "1. Terraform Outputs:"
terraform output

echo ""
echo "2. Lambda Test:"
aws lambda invoke --function-name secure-governance-demo-secure-ai --payload '{"test": true}' /tmp/phase10-evidence.json --cli-binary-format raw-in-base64-out
cat /tmp/phase10-evidence.json

echo ""
echo "3. Lambda Configuration:"
aws lambda get-function --function-name secure-governance-demo-secure-ai --query 'Configuration.[FunctionName, Runtime, Handler, State, LastUpdateStatus]'

echo ""
echo "4. KMS Key:"
aws kms describe-key --key-id $(aws kms list-aliases --query 'Aliases[?AliasName==`alias/secure-governance-demo-ai-data`].TargetKeyId' --output text) --query 'KeyMetadata.[KeyId, KeyState, Description]'

echo ""
echo "5. IAM Role:"
aws iam get-role --role-name secure-governance-demo-ai-lambda-role --query 'Role.[RoleName, Arn]'

echo ""
echo "6. Project Files:"
find . -name "*.tf" -o -name "*.py" -o -name "*.zip" | grep -E "(main.tf|secure_ai_processor)" | head -10

echo ""
echo "✅ EVIDENCE CAPTURE COMPLETE"
