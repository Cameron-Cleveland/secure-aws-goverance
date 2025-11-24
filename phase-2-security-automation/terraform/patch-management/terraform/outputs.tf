# outputs.tf
output "ssm_managed_instance_id" {
  description = "ID of the SSM-managed EC2 instance"
  value       = aws_instance.ssm_managed_instance.id
}

output "non_ssm_instance_id" {
  description = "ID of the non-SSM-managed EC2 instance"
  value       = aws_instance.non_ssm_instance.id
}

output "ssm_instance_profile_arn" {
  description = "ARN of the SSM instance profile"
  value       = aws_iam_instance_profile.ssm_instance_profile.arn
}

output "security_group_id" {
  description = "ID of the security group"
  value       = aws_security_group.demo_sg.id
}
