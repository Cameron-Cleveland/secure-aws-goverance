# API Gateway
resource "aws_api_gateway_rest_api" "ecom_api" {
  name        = "${var.project_name}-api"
  description = "E-commerce REST API"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Component   = "api-gateway"
  }
}

# API Gateway Resources
resource "aws_api_gateway_resource" "products" {
  rest_api_id = aws_api_gateway_rest_api.ecom_api.id
  parent_id   = aws_api_gateway_rest_api.ecom_api.root_resource_id
  path_part   = "products"
}

resource "aws_api_gateway_resource" "product" {
  rest_api_id = aws_api_gateway_rest_api.ecom_api.id
  parent_id   = aws_api_gateway_resource.products.id
  path_part   = "{product_id}"
}

resource "aws_api_gateway_resource" "orders" {
  rest_api_id = aws_api_gateway_rest_api.ecom_api.id
  parent_id   = aws_api_gateway_rest_api.ecom_api.root_resource_id
  path_part   = "orders"
}

resource "aws_api_gateway_resource" "order" {
  rest_api_id = aws_api_gateway_rest_api.ecom_api.id
  parent_id   = aws_api_gateway_resource.orders.id
  path_part   = "{order_id}"
}

# GET /products - Get all products
resource "aws_api_gateway_method" "get_products" {
  rest_api_id   = aws_api_gateway_rest_api.ecom_api.id
  resource_id   = aws_api_gateway_resource.products.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "get_products" {
  rest_api_id             = aws_api_gateway_rest_api.ecom_api.id
  resource_id             = aws_api_gateway_resource.products.id
  http_method             = aws_api_gateway_method.get_products.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.get_products_lambda_arn_invoke
}

# GET /products/{product_id} - Get specific product
resource "aws_api_gateway_method" "get_product" {
  rest_api_id   = aws_api_gateway_rest_api.ecom_api.id
  resource_id   = aws_api_gateway_resource.product.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "get_product" {
  rest_api_id             = aws_api_gateway_rest_api.ecom_api.id
  resource_id             = aws_api_gateway_resource.product.id
  http_method             = aws_api_gateway_method.get_product.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.get_products_lambda_arn_invoke
}

# POST /orders - Create new order
resource "aws_api_gateway_method" "create_order" {
  rest_api_id   = aws_api_gateway_rest_api.ecom_api.id
  resource_id   = aws_api_gateway_resource.orders.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "create_order" {
  rest_api_id             = aws_api_gateway_rest_api.ecom_api.id
  resource_id             = aws_api_gateway_resource.orders.id
  http_method             = aws_api_gateway_method.create_order.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.create_order_lambda_arn_invoke
}

# GET /orders/{order_id} - Get order status
resource "aws_api_gateway_method" "get_order" {
  rest_api_id   = aws_api_gateway_rest_api.ecom_api.id
  resource_id   = aws_api_gateway_resource.order.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "get_order" {
  rest_api_id             = aws_api_gateway_rest_api.ecom_api.id
  resource_id             = aws_api_gateway_resource.order.id
  http_method             = aws_api_gateway_method.get_order.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.get_order_status_lambda_arn_invoke
}

# Lambda Permissions
resource "aws_lambda_permission" "get_products" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = var.get_products_lambda_arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.ecom_api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "create_order" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = var.create_order_lambda_arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.ecom_api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "get_order_status" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = var.get_order_status_lambda_arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.ecom_api.execution_arn}/*/*"
}

# API Deployment
resource "aws_api_gateway_deployment" "ecom_api" {
  depends_on = [
    aws_api_gateway_integration.get_products,
    aws_api_gateway_integration.get_product,
    aws_api_gateway_integration.create_order,
    aws_api_gateway_integration.get_order
  ]

  rest_api_id = aws_api_gateway_rest_api.ecom_api.id
  stage_name  = var.environment

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_method.get_products.id,
      aws_api_gateway_method.get_product.id,
      aws_api_gateway_method.create_order.id,
      aws_api_gateway_method.get_order.id
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}
