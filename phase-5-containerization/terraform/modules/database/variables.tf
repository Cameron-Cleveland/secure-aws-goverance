variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID for security groups"
  type        = string
}

variable "private_subnets" {
  description = "List of private subnet IDs for database"
  type        = list(string)
}

variable "ecs_security_group_id" {
  description = "ECS security group ID to allow database connections"
  type        = string
}
