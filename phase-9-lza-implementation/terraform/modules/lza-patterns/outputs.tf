# outputs.tf - LZA Outputs
output "central_logs_bucket" {
  description = "Centralized logging bucket"
  value       = aws_s3_bucket.central_logs.bucket
}

output "cloudtrail_trail" {
  description = "CloudTrail trail name"
  value       = aws_cloudtrail.main_trail.name
}

output "deployment_summary" {
  description = "LZA deployment summary"
  value       = "✅ LZA Patterns Implemented: Centralized CloudTrail + S3 Logging"
}

output "verification_commands" {
  description = "Commands to verify deployment"
  value = <<EOT
Run these commands to verify:

aws cloudtrail describe-trails
aws s3 ls | grep enterprise-lza
aws cloudtrail get-trail-status --name enterprise-lza-main-trail
EOT
}
