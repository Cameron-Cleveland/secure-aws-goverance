output "vpc_id" {
  description = "ID of the AI VPC"
  value       = aws_vpc.ai_vpc.id
}

output "private_subnet_ids" {
  description = "IDs of private subnets"
  value       = aws_subnet.ai_private[*].id
}

output "bedrock_endpoint_id" {
  description = "ID of BedRock VPC endpoint"
  value       = aws_vpc_endpoint.bedrock_runtime.id
}

output "bedrock_security_group_id" {
  description = "ID of BedRock security group"
  value       = aws_security_group.bedrock_access.id
}

output "kms_key_id" {
  description = "ID of AI data KMS key"
  value       = aws_kms_key.ai_data.key_id
}

output "bedrock_role_arn" {
  description = "ARN of secure BedRock IAM role"
  value       = aws_iam_role.bedrock_secure.arn
}

output "security_summary" {
  description = "AI/ML security implementation summary"
  value = <<EOT
✅ ENTERPRISE AI/ML SECURITY IMPLEMENTED:

Network Security:
• Private VPC: ${aws_vpc.ai_vpc.id}
• Private Subnets: ${length(aws_subnet.ai_private)} subnets
• VPC Endpoints: BedRock Runtime
• Security Groups: Least privilege access

Data Security:
• KMS Encryption: ${aws_kms_key.ai_data.arn}
• VPC-Only Access: Enforced via IAM conditions

Access Controls:
• IAM Role: ${aws_iam_role.bedrock_secure.arn}
• VPC Restrictions: SourceVpc condition
• Minimal Permissions: BedRock-specific only

🎯 PRODUCTION-READY AI SECURITY ARCHITECTURE
EOT
}
