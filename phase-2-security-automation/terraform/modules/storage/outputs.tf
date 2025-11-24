output "s3_bucket_name" {
  description = "S3 Bucket name"
  value       = aws_s3_bucket.project_data.id
}

output "s3_bucket_arn" {
  description = "S3 Bucket ARN"
  value       = aws_s3_bucket.project_data.arn
}