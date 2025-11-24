output "kms_key_arn" {
  description = "KMS Key ARN for encryption"
  value       = module.security.kms_key_arn
}

output "s3_bucket_name" {
  description = "S3 Bucket name for data storage"
  value       = module.storage.s3_bucket_name
}

/*output "security_hub_status" {
  description = "Security Hub enabled status"
  value       = module.security.security_hub_enabled
}

output "lambda_function_name" {
  description = "Lambda function name"
  value       = module.compute.lambda_function_name
}

output "secret_arn" {
  description = "Secrets Manager secret ARN"
  value       = module.security.secret_arn
}*/