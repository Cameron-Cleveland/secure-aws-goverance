# S3 BUCKET WITH KMS ENCRYPTION
resource "aws_s3_bucket" "project_data" {
  bucket = "${var.project_name}-data-${random_id.suffix.hex}"

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "project_data" {
  bucket = aws_s3_bucket.project_data.id
  
  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = var.kms_key_arn
      sse_algorithm     = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "project_data" {
  bucket = aws_s3_bucket.project_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "random_id" "suffix" {
  byte_length = 8
}