output "api_url" {
  description = "Base URL of the API Gateway"
  value       = "${aws_api_gateway_deployment.ecom_api.invoke_url}"
}

output "api_id" {
  description = "ID of the API Gateway"
  value       = aws_api_gateway_rest_api.ecom_api.id
}

output "api_execution_arn" {
  description = "Execution ARN of the API Gateway"
  value       = aws_api_gateway_rest_api.ecom_api.execution_arn
}
