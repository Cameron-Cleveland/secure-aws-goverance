variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment"
  type        = string
}

variable "products_table_name" {
  description = "DynamoDB products table name"
  type        = string
}

variable "orders_table_name" {
  description = "DynamoDB orders table name"
  type        = string
}
