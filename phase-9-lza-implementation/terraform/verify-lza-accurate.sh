#!/bin/bash
echo "🔍 ACCURATE LZA VERIFICATION"
echo "============================"

echo ""
echo "1. CLOUDTRAIL (LZA Core Pattern):"
aws cloudtrail describe-trails --query 'trailList[].[Name, IsMultiRegionTrail, S3BucketName]' --output table

echo ""
echo "2. S3 BUCKETS (Centralized Logging):"
aws s3 ls | grep -E "(lza|log|audit|trail|enterprise)" || echo "No LZA buckets found"

echo ""
echo "3. SECURITY SERVICES (LZA Security Baseline):"
echo "   Security Hub: $(aws securityhub describe-hub --query 'HubArn' --output text 2>/dev/null || echo 'NOT SUBSCRIBED - LZA OPPORTUNITY')"
echo "   GuardDuty: $(aws guardduty list-detectors --query 'DetectorIds[0]' --output text 2>/dev/null || echo 'NOT ENABLED - LZA OPPORTUNITY')"

echo ""
echo "4. AWS CONFIG (Compliance):"
aws configservice describe-delivery-channels --query 'DeliveryChannels[0].name' --output text 2>/dev/null || echo "Not configured - LZA OPPORTUNITY"

echo ""
echo "5. AWS ORGANIZATIONS (Enterprise Context):"
aws organizations describe-organization --query 'Organization.[Id, FeatureSet, MasterAccountEmail]' --output table

echo ""
echo "🎯 LZA IMPLEMENTATION OPPORTUNITIES FOUND:"
echo "   - Enable Security Hub (LZA Security Baseline)"
echo "   - Enable GuardDuty (LZA Threat Detection)" 
echo "   - Configure AWS Config (LZA Compliance)"
echo "   - Verify/Create Centralized CloudTrail"
