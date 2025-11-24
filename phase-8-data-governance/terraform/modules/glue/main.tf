# S3 Bucket for Data Lake
resource "aws_s3_bucket" "data_lake" {
  bucket = var.data_bucket

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Component   = "data-lake"
  }
}

# Enable versioning for data recovery
resource "aws_s3_bucket_versioning" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Enable server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Block public access
resource "aws_s3_bucket_public_access_block" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# IAM Role for Glue
resource "aws_iam_role" "glue_role" {
  name = "${var.project_name}-glue-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "glue.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Component   = "glue"
  }
}

# Glue Role Policy
resource "aws_iam_role_policy_attachment" "glue_service" {
  role       = aws_iam_role.glue_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

resource "aws_iam_role_policy" "glue_s3_access" {
  name = "${var.project_name}-glue-s3-access"
  role = aws_iam_role.glue_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${var.data_bucket}",
          "arn:aws:s3:::${var.data_bucket}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = ["arn:aws:logs:*:*:*"]
      }
    ]
  })
}

# Glue Database
resource "aws_glue_catalog_database" "ecom_data" {
  name = "${var.project_name}_ecom_database"

  parameters = {
    description = "E-commerce data database"
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Glue Crawler
resource "aws_glue_crawler" "ecom_crawler" {
  name          = "${var.project_name}-ecom-crawler"
  database_name = aws_glue_catalog_database.ecom_data.name
  role          = aws_iam_role.glue_role.arn

  s3_target {
    path = "s3://${aws_s3_bucket.data_lake.bucket}/raw/"
  }

  schema_change_policy {
    delete_behavior = "LOG"
    update_behavior = "UPDATE_IN_DATABASE"
  }

  configuration = jsonencode({
    Version = 1.0
    Grouping = {
      TableGroupingPolicy = "CombineCompatibleSchemas"
    }
  })

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Glue ETL Job
resource "aws_glue_job" "ecom_etl" {
  name     = "${var.project_name}-ecom-etl"
  role_arn = aws_iam_role.glue_role.arn

  command {
    script_location = "s3://${aws_s3_bucket.data_lake.bucket}/scripts/ecom_etl.py"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language" = "python"
    "--enable-metrics" = ""
    "--enable-spark-ui" = "true"
    "--spark-event-logs-path" = "s3://${aws_s3_bucket.data_lake.bucket}/spark-logs/"
    "--enable-continuous-cloudwatch-log" = "true"
    "--TempDir" = "s3://${aws_s3_bucket.data_lake.bucket}/temp/"
    "--extra-py-files" = ""
  }

  execution_property {
    max_concurrent_runs = 2
  }

  max_retries = 1

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Upload ETL script - SIMPLIFIED: Skip file upload for now
# We'll manually upload or use a simpler approach
