output "kms_key_arn" {
  description = "KMS Key ARN for encryption"
  value       = aws_kms_key.project_encryption.arn
}

output "secret_arn" {
  description = "Secrets Manager secret ARN"
  value       = aws_secretsmanager_secret.database_credentials.arn
}