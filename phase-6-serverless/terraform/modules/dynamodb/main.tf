# Products Table
resource "aws_dynamodb_table" "products" {
  name           = "${var.project_name}-products"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "product_id"

  attribute {
    name = "product_id"
    type = "S"
  }

  attribute {
    name = "category"
    type = "S"
  }

  global_secondary_index {
    name               = "CategoryIndex"
    hash_key           = "category"
    projection_type    = "ALL"
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Component   = "dynamodb"
  }
}

# Orders Table
resource "aws_dynamodb_table" "orders" {
  name           = "${var.project_name}-orders"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "order_id"

  attribute {
    name = "order_id"
    type = "S"
  }

  attribute {
    name = "customer_id"
    type = "S"
  }

  global_secondary_index {
    name               = "CustomerIndex"
    hash_key           = "customer_id"
    projection_type    = "ALL"
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Component   = "dynamodb"
  }
}

# Sample Data for Products Table
resource "aws_dynamodb_table_item" "sample_products" {
  table_name = aws_dynamodb_table.products.name
  hash_key   = aws_dynamodb_table.products.hash_key

  item = <<ITEM
{
  "product_id": {"S": "1"},
  "name": {"S": "Laptop"},
  "description": {"S": "High-performance laptop"},
  "price": {"N": "999.99"},
  "category": {"S": "electronics"},
  "stock": {"N": "50"}
}
ITEM
}
