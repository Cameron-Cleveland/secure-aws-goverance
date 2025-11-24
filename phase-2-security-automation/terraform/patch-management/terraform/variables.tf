# variables.tf
variable "region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type for test instances"
  type        = string
  default     = "t3.micro"
}

variable "ami_id" {
  description = "AMI ID for EC2 instances (Amazon Linux 2023)"
  type        = string
  default     = "ami-0c02fb55956c7d316"
}

variable "project_name" {
  description = "Name of the project for tagging"
  type        = string
  default     = "secure-governance-demo"
}

variable "environment" {
  description = "Environment for tagging"
  type        = string
  default     = "demo"
}
