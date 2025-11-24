output "products_table_name" {
  description = "DynamoDB products table name"
  value       = aws_dynamodb_table.products.name
}

output "orders_table_name" {
  description = "DynamoDB orders table name"
  value       = aws_dynamodb_table.orders.name
}

output "lambda_role_arn" {
  description = "Lambda execution role ARN"
  value       = aws_iam_role.lambda_role.arn
}

output "lambda_functions" {
  description = "Lambda function ARNs"
  value = {
    get_products     = aws_lambda_function.get_products.arn
    create_order     = aws_lambda_function.create_order.arn
    get_order_status = aws_lambda_function.get_order_status.arn
  }
}

output "api_url" {
  description = "Base URL of the API Gateway"
  value       = "${aws_api_gateway_deployment.ecom_api.invoke_url}"
}

output "api_endpoints" {
  description = "Available API endpoints"
  value = {
    "GET /products"          = "${aws_api_gateway_deployment.ecom_api.invoke_url}/products"
    "GET /products/{id}"     = "${aws_api_gateway_deployment.ecom_api.invoke_url}/products/{product_id}"
    "POST /orders"           = "${aws_api_gateway_deployment.ecom_api.invoke_url}/orders"
    "GET /orders/{id}"       = "${aws_api_gateway_deployment.ecom_api.invoke_url}/orders/{order_id}"
  }
}

output "deployment_status" {
  description = "Current deployment status"
  value       = "Stage 4 Complete - Full Serverless Backend Deployed! 🎉"
}
