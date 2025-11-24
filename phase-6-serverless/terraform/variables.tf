variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment"
  type        = string
}

variable "get_products_lambda_arn" {
  description = "ARN of the get products Lambda function"
  type        = string
}

variable "create_order_lambda_arn" {
  description = "ARN of the create order Lambda function"
  type        = string
}

variable "get_order_status_lambda_arn" {
  description = "ARN of the get order status Lambda function"
  type        = string
}

variable "get_products_lambda_arn_invoke" {
  description = "Invoke ARN of the get products Lambda function"
  type        = string
}

variable "create_order_lambda_arn_invoke" {
  description = "Invoke ARN of the create order Lambda function"
  type        = string
}

variable "get_order_status_lambda_arn_invoke" {
  description = "Invoke ARN of the get order status Lambda function"
  type        = string
}
