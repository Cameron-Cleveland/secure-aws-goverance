terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# VPC for AI Services
resource "aws_vpc" "ai_vpc" {
  cidr_block           = "10.1.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "secure-ai-ml-ai-vpc"
    Project = "secure-ai-ml"
  }
}

# Private Subnets
resource "aws_subnet" "ai_private" {
  count = 2

  vpc_id            = aws_vpc.ai_vpc.id
  cidr_block        = "10.1.${count.index + 1}.0/24"
  availability_zone = "us-east-1${count.index == 0 ? "a" : "b"}"

  tags = {
    Name = "secure-ai-ml-ai-private-${count.index + 1}"
    Type = "private"
  }
}
# VPC Endpoint for BedRock Runtime
resource "aws_vpc_endpoint" "bedrock_runtime" {
  vpc_id              = aws_vpc.ai_vpc.id
  service_name        = "com.amazonaws.us-east-1.bedrock-runtime"
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true
  security_group_ids  = [aws_security_group.bedrock_access.id]
  subnet_ids          = aws_subnet.ai_private[*].id

  tags = {
    Name = "secure-ai-ml-bedrock-endpoint"
  }
}

# Security Group for BedRock Access
resource "aws_security_group" "bedrock_access" {
  name_prefix = "secure-ai-ml-bedrock-sg-"
  vpc_id      = aws_vpc.ai_vpc.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["10.1.0.0/16"]
    description = "HTTPS from VPC for BedRock"
  }

  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS to AWS services"
  }

  tags = {
    Name = "secure-ai-ml-bedrock-security-group"
  }
}
# KMS Key for AI Data Encryption
resource "aws_kms_key" "ai_data" {
  description             = "KMS key for AI/ML data encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = {
    Name = "secure-ai-ml-ai-data-key"
  }
}

resource "aws_kms_alias" "ai_data" {
  name          = "alias/secure-ai-ml-ai-data"
  target_key_id = aws_kms_key.ai_data.key_id
}

# IAM Role for Secure BedRock Access
resource "aws_iam_role" "bedrock_secure" {
  name = "secure-ai-ml-bedrock-secure-role"

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
    Project = "secure-ai-ml"
  }
}

# IAM Policy for BedRock with VPC restrictions
resource "aws_iam_role_policy" "bedrock_private" {
  name = "secure-ai-ml-bedrock-private-policy"
  role = aws_iam_role.bedrock_secure.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream",
          "bedrock:ListFoundationModels"
        ]
        Resource = "arn:aws:bedrock:us-east-1::foundation-model/*"
        Condition = {
          StringEquals = {
            "aws:SourceVpc" = aws_vpc.ai_vpc.id
          }
        }
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:GenerateDataKey"
        ]
        Resource = aws_kms_key.ai_data.arn
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
