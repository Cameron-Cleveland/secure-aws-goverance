terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# Local values
locals {
  project_name = "secure-governance-demo"
  environment  = "demo"
}

# DynamoDB Tables
resource "aws_dynamodb_table" "products" {
  name           = "${local.project_name}-products"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "product_id"

  attribute {
    name = "product_id"
    type = "S"
  }

  tags = {
    Environment = local.environment
    Project     = local.project_name
    Component   = "dynamodb"
  }
}

resource "aws_dynamodb_table" "orders" {
  name           = "${local.project_name}-orders"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "order_id"

  attribute {
    name = "order_id"
    type = "S"
  }

  tags = {
    Environment = local.environment
    Project     = local.project_name
    Component   = "dynamodb"
  }
}

# IAM Role for Lambda Functions
resource "aws_iam_role" "lambda_role" {
  name = "${local.project_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Environment = local.environment
    Project     = local.project_name
    Component   = "lambda"
  }
}

# IAM Policy for Lambda to access DynamoDB and CloudWatch
resource "aws_iam_role_policy" "lambda_policy" {
  name = "${local.project_name}-lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [
          aws_dynamodb_table.products.arn,
          "${aws_dynamodb_table.products.arn}/index/*",
          aws_dynamodb_table.orders.arn,
          "${aws_dynamodb_table.orders.arn}/index/*"
        ]
      }
    ]
  })
}

# Data sources to zip Lambda functions
data "archive_file" "get_products" {
  type        = "zip"
  source_file = "${path.module}/../src/lambda-functions/get-products.py"
  output_path = "${path.module}/../src/lambda-functions/get-products.zip"
}

data "archive_file" "create_order" {
  type        = "zip"
  source_file = "${path.module}/../src/lambda-functions/create-order.py"
  output_path = "${path.module}/../src/lambda-functions/create-order.zip"
}

data "archive_file" "get_order_status" {
  type        = "zip"
  source_file = "${path.module}/../src/lambda-functions/get-order-status.py"
  output_path = "${path.module}/../src/lambda-functions/get-order-status.zip"
}

# Get Products Lambda Function
resource "aws_lambda_function" "get_products" {
  filename      = data.archive_file.get_products.output_path
  function_name = "${local.project_name}-get-products"
  role          = aws_iam_role.lambda_role.arn
  handler       = "get-products.lambda_handler"
  runtime       = "python3.9"
  timeout       = 30

  environment {
    variables = {
      PRODUCTS_TABLE = aws_dynamodb_table.products.name
    }
  }

  tags = {
    Environment = local.environment
    Project     = local.project_name
    Component   = "lambda"
  }

  depends_on = [data.archive_file.get_products]
}

# Create Order Lambda Function
resource "aws_lambda_function" "create_order" {
  filename      = data.archive_file.create_order.output_path
  function_name = "${local.project_name}-create-order"
  role          = aws_iam_role.lambda_role.arn
  handler       = "create-order.lambda_handler"
  runtime       = "python3.9"
  timeout       = 30

  environment {
    variables = {
      ORDERS_TABLE   = aws_dynamodb_table.orders.name
      PRODUCTS_TABLE = aws_dynamodb_table.products.name
    }
  }

  tags = {
    Environment = local.environment
    Project     = local.project_name
    Component   = "lambda"
  }

  depends_on = [data.archive_file.create_order]
}

# Get Order Status Lambda Function
resource "aws_lambda_function" "get_order_status" {
  filename      = data.archive_file.get_order_status.output_path
  function_name = "${local.project_name}-get-order-status"
  role          = aws_iam_role.lambda_role.arn
  handler       = "get-order-status.lambda_handler"
  runtime       = "python3.9"
  timeout       = 30

  environment {
    variables = {
      ORDERS_TABLE = aws_dynamodb_table.orders.name
    }
  }

  tags = {
    Environment = local.environment
    Project     = local.project_name
    Component   = "lambda"
  }

  depends_on = [data.archive_file.get_order_status]
}

# API Gateway
resource "aws_api_gateway_rest_api" "ecom_api" {
  name        = "${local.project_name}-api"
  description = "E-commerce REST API"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = {
    Environment = local.environment
    Project     = local.project_name
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
  uri                     = aws_lambda_function.get_products.invoke_arn
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
  uri                     = aws_lambda_function.get_products.invoke_arn
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
  uri                     = aws_lambda_function.create_order.invoke_arn
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
  uri                     = aws_lambda_function.get_order_status.invoke_arn
}

# Lambda Permissions for API Gateway
resource "aws_lambda_permission" "get_products" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.get_products.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.ecom_api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "create_order" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.create_order.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.ecom_api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "get_order_status" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.get_order_status.function_name
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
  stage_name  = local.environment

  lifecycle {
    create_before_destroy = true
  }
}
