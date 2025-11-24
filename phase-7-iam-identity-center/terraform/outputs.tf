output "permission_sets" {
  description = "Created IAM Identity Center permission sets"
  value = {
    administrator    = aws_ssoadmin_permission_set.administrator.name
    power_user       = aws_ssoadmin_permission_set.power_user.name
    read_only        = aws_ssoadmin_permission_set.read_only.name
    security_auditor = aws_ssoadmin_permission_set.security_auditor.name
  }
}

output "sso_instance_arn" {
  description = "IAM Identity Center Instance ARN"
  value       = var.sso_instance_arn
}

output "management_account_id" {
  description = "Management Account ID"
  value       = var.management_account_id
}
