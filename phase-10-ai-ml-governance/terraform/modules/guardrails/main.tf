# IAM Policy for AI Content Filtering
resource "aws_iam_policy" "ai_guardrails" {
  name        = "${var.project_name}-ai-guardrails"
  description = "AI content filtering and safety policies"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:ApplyGuardrail",
          "bedrock:GetGuardrail",
          "bedrock:ListGuardrails"
        ]
        Resource = "*"
      }
    ]
  })

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# S3 Bucket for AI Training Data (with governance)
resource "aws_s3_bucket" "ai_training_data" {
  bucket = "${var.project_name}-ai-data-${random_id.suffix.hex}"

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Component   = "ai-training-data"
  }
}

resource "aws_s3_bucket_versioning" "ai_training_data" {
  bucket = aws_s3_bucket.ai_training_data.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "ai_training_data" {
  bucket = aws_s3_bucket.ai_training_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "random_id" "suffix" {
  byte_length = 8
}
