# S3 Bucket for HR Documents
resource "aws_s3_bucket" "hr_documents" {
  bucket = "${var.project_name}-hr-documents-${random_id.suffix.hex}"

  tags = {
    Environment = var.environment
    Project     = var.project_name
    DataClassification = "confidential"
    Workflow    = "hr-onboarding"
  }
}

resource "aws_s3_bucket_versioning" "hr_documents" {
  bucket = aws_s3_bucket.hr_documents.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "hr_documents" {
  bucket = aws_s3_bucket.hr_documents.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "hr_documents" {
  bucket = aws_s3_bucket.hr_documents.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# IAM Role for HR Workflow (for future Lambda function)
resource "aws_iam_role" "hr_workflow" {
  name = "${var.project_name}-hr-workflow"

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
    Environment = var.environment
    Project     = var.project_name
  }
}

# IAM Policy for HR Workflow
resource "aws_iam_policy" "hr_workflow" {
  name        = "${var.project_name}-hr-workflow"
  description = "Permissions for HR onboarding workflow"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.hr_documents.arn,
          "${aws_s3_bucket.hr_documents.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "comprehend:DetectPiiEntities",
          "comprehend:DetectEntities"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel"
        ]
        Resource = [
          "arn:aws:bedrock:*::foundation-model/amazon.titan-text-express-v1",
          "arn:aws:bedrock:*::foundation-model/anthropic.claude-instant-v1"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "hr_workflow" {
  role       = aws_iam_role.hr_workflow.name
  policy_arn = aws_iam_policy.hr_workflow.arn
}

# Output the bucket name so we can use it in our scripts
output "hr_documents_bucket" {
  description = "Name of the HR documents S3 bucket"
  value       = aws_s3_bucket.hr_documents.bucket
}

output "hr_workflow_role_arn" {
  description = "ARN of the HR workflow IAM role"
  value       = aws_iam_role.hr_workflow.arn
}

resource "random_id" "suffix" {
  byte_length = 8
}
