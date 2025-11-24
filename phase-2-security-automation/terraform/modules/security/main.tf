# SECURITY HUB - Centralized Security Monitoring
resource "aws_securityhub_account" "main" {}

resource "aws_securityhub_standards_subscription" "cis" {
  standards_arn = "arn:aws:securityhub:::ruleset/cis-aws-foundations-benchmark/v/1.2.0"
  depends_on    = [aws_securityhub_account.main]
}

# KMS ENCRYPTION KEY
resource "aws_kms_key" "project_encryption" {
  description             = "Project encryption key for sensitive data"
  deletion_window_in_days = 7
  enable_key_rotation     = true
  
  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_kms_alias" "project_encryption" {
  name          = "alias/secure-governance-demo-key"
  target_key_id = aws_kms_key.project_encryption.key_id
}

# KMS KEY POLICY FOR AWS CONFIG
resource "aws_kms_grant" "config" {
  name              = "${var.project_name}-config-grant"
  key_id            = aws_kms_key.project_encryption.key_id
  grantee_principal = aws_iam_role.config_role.arn
  operations        = ["Encrypt", "Decrypt", "GenerateDataKey"]
}

# SECRETS MANAGER FOR CREDENTIALS
resource "aws_secretsmanager_secret" "database_credentials" {
  name       = "${var.project_name}/database-credentials"
  kms_key_id = aws_kms_key.project_encryption.arn
  
  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "database_credentials" {
  secret_id = aws_secretsmanager_secret.database_credentials.id
  secret_string = jsonencode({
    username = "app_user"
    password = "secure_password_123"
    host     = "database.demo.internal"
  })
}

# === AWS CONFIG - REQUIRED FOR SECURITY HUB ===

# S3 BUCKET FOR CONFIG LOGS
resource "aws_s3_bucket" "config_bucket" {
  bucket = "${var.project_name}-config-logs-${random_id.config_suffix.hex}"

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "config_bucket" {
  bucket = aws_s3_bucket.config_bucket.id
  
  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.project_encryption.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

# S3 BUCKET POLICY FOR AWS CONFIG
resource "aws_s3_bucket_policy" "config_bucket" {
  bucket = aws_s3_bucket.config_bucket.id
  policy = data.aws_iam_policy_document.config_bucket.json
}

data "aws_iam_policy_document" "config_bucket" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["config.amazonaws.com"]
    }
    actions = [
      "s3:GetBucketAcl",
      "s3:ListBucket"
    ]
    resources = [aws_s3_bucket.config_bucket.arn]
  }

  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["config.amazonaws.com"]
    }
    actions = ["s3:PutObject"]
    resources = ["${aws_s3_bucket.config_bucket.arn}/AWSLogs/${data.aws_caller_identity.current.account_id}/*"]
    condition {
      test     = "StringLike"
      variable = "s3:x-amz-acl"
      values   = ["bucket-owner-full-control"]
    }
  }
}

# Add this data source for the account ID
data "aws_caller_identity" "current" {}

# IAM ROLE FOR AWS CONFIG
resource "aws_iam_role" "config_role" {
  name = "${var.project_name}-config-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "config.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_iam_role_policy_attachment" "config_role" {
  role       = aws_iam_role.config_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWS_ConfigRole"
}

# AWS CONFIG RECORDER
resource "aws_config_configuration_recorder" "main" {
  name     = "default"
  role_arn = aws_iam_role.config_role.arn  # ← REQUIRED

  recording_group {
    all_supported                 = true
    include_global_resource_types = true
  }
}

# AWS CONFIG DELIVERY CHANNEL
resource "aws_config_delivery_channel" "main" {
  name           = "default"
  s3_bucket_name = aws_s3_bucket.config_bucket.bucket
  depends_on     = [aws_config_configuration_recorder.main]
}

# AWS CONFIG RECORDER STATUS
resource "aws_config_configuration_recorder_status" "main" {
  name       = aws_config_configuration_recorder.main.name
  is_enabled = true
  depends_on = [aws_config_delivery_channel.main]
}

resource "random_id" "config_suffix" {
  byte_length = 8
}