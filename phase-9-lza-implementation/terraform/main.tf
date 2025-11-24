terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# LZA PATTERN 1: Security Hub
resource "aws_securityhub_account" "lza_security_hub" {}

# LZA PATTERN 2: GuardDuty
resource "aws_guardduty_detector" "lza_guardduty" {
  enable = true
}

# LZA PATTERN 3: Centralized Logging with PROPER CLOUDTRAIL POLICY
resource "aws_s3_bucket" "lza_phase9_logs" {
  bucket_prefix = "phase9-lza-logs-"
  force_destroy = true

  tags = {
    Project     = "enterprise-lza"
    Environment = "governance"
    Component   = "lza-central-logs"
    Phase       = "9"
  }
}
resource "aws_s3_bucket_versioning" "lza_phase9_logs" {
  bucket = aws_s3_bucket.lza_phase9_logs.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "lza_phase9_logs" {
  bucket = aws_s3_bucket.lza_phase9_logs.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "lza_phase9_logs" {
  bucket = aws_s3_bucket.lza_phase9_logs.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# CLOUDTRAIL BUCKET POLICY - FIXES THE ERROR
resource "aws_s3_bucket_policy" "cloudtrail_logs" {
  bucket = aws_s3_bucket.lza_phase9_logs.id
  policy = data.aws_iam_policy_document.cloudtrail_logs.json

  depends_on = [
    aws_s3_bucket.lza_phase9_logs,
    aws_s3_bucket_public_access_block.lza_phase9_logs
  ]
}

data "aws_iam_policy_document" "cloudtrail_logs" {
  statement {
    sid    = "AWSCloudTrailAclCheck"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["cloudtrail.amazonaws.com"]
    }

    actions   = ["s3:GetBucketAcl"]
    resources = [aws_s3_bucket.lza_phase9_logs.arn]
  }

  statement {
    sid    = "AWSCloudTrailWrite"
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["cloudtrail.amazonaws.com"]
    }

    actions   = ["s3:PutObject"]
    resources = ["${aws_s3_bucket.lza_phase9_logs.arn}/AWSLogs/${data.aws_caller_identity.current.account_id}/*"]

    condition {
      test     = "StringEquals"
      variable = "s3:x-amz-acl"
      values   = ["bucket-owner-full-control"]
    }
  }
}
# LZA PATTERN 4: CloudTrail - WITH DEPENDS_ON FOR BUCKET POLICY
resource "aws_cloudtrail" "lza_phase9_trail" {
  name                          = "phase9-lza-audit-trail"
  s3_bucket_name                = aws_s3_bucket.lza_phase9_logs.id
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = true

  depends_on = [aws_s3_bucket_policy.cloudtrail_logs]

  tags = {
    Project     = "enterprise-lza"
    Environment = "governance"
    Component   = "lza-cloudtrail"
    Phase       = "9"
  }
}

# Data sources
data "aws_caller_identity" "current" {}

# OUTPUTS
output "lza_status" {
  value = "✅ LZA Patterns Implemented: Security Hub, GuardDuty, CloudTrail, S3"
}

output "security_hub_status" {
  value = "Security Hub: ACTIVE"
}

output "guardduty_status" {
  value = "GuardDuty: ${aws_guardduty_detector.lza_guardduty.enable ? "ENABLED" : "DISABLED"}"
}

output "cloudtrail_status" {
  value = "CloudTrail: ${aws_cloudtrail.lza_phase9_trail.name}"
}

output "s3_bucket" {
  value = aws_s3_bucket.lza_phase9_logs.bucket
}

output "verification_commands" {
  value = <<EOT
# Verify LZA Implementation:
aws securityhub describe-hub
aws guardduty list-detectors
aws cloudtrail describe-trails --query 'trailList[?Name==`phase9-lza-audit-trail`]'
aws s3 ls | grep phase9-lza
EOT
}
