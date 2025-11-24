variable "project_name" {
  description = "Name of the project for resource tagging"
  type        = string
  default     = "secure-governance-demo"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "demo"
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}