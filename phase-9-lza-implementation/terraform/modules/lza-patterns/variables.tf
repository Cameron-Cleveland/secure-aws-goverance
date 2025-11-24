# variables.tf - LZA Configuration
variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "enterprise-lza"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "governance"
}

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}
