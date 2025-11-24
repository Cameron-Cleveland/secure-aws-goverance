variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment"
  type        = string
}

variable "data_bucket" {
  description = "S3 bucket name for data lake"
  type        = string
}

variable "data_bucket_suffix" {
  description = "Suffix for data bucket"
  type        = string
}
