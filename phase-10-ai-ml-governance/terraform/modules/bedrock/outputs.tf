output "bedrock_role_arn" {
  description = "ARN of the BedRock access role"
  value       = aws_iam_role.bedrock_access_role.arn
}

output "bedrock_governance_rule" {
  description = "Name of the BedRock governance config rule"
  value       = aws_config_config_rule.bedrock_governance.name
}
