variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "s3_bucket_name" {
  description = "S3 Bucket name"
  type        = string
}

variable "s3_bucket_arn" {
  description = "S3 Bucket ARN"
  type        = string
}