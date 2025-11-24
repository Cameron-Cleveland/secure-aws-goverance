# patch-management/terraform/main.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# IAM Role for EC2 to use SSM
resource "aws_iam_role" "ssm_ec2_role" {
  name = "${var.project_name}-ssm-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Component   = "patch-management"
  }
}

# IAM Policy for SSM
resource "aws_iam_role_policy_attachment" "ssm_managed_instance" {
  role       = aws_iam_role.ssm_ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# IAM Instance Profile
resource "aws_iam_instance_profile" "ssm_instance_profile" {
  name = "${var.project_name}-ssm-profile"
  role = aws_iam_role.ssm_ec2_role.name
}

# Security Group for EC2 instances
resource "aws_security_group" "demo_sg" {
  name        = "${var.project_name}-patch-sg"
  description = "Security group for patch management demo"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Component   = "patch-management"
  }
}

# EC2 Instance that CAN be managed by SSM (with correct IAM role)
resource "aws_instance" "ssm_managed_instance" {
  ami                  = var.ami_id
  instance_type        = var.instance_type
  iam_instance_profile = aws_iam_instance_profile.ssm_instance_profile.name
  vpc_security_group_ids = [aws_security_group.demo_sg.name]

  tags = {
    Name        = "${var.project_name}-ssm-managed"
    Environment = var.environment
    Project     = var.project_name
    Component   = "patch-management"
  }

  # Ensure instance is ready for SSM
  user_data = <<-EOF
              #!/bin/bash
              sudo dnf update -y
              sudo systemctl enable amazon-ssm-agent
              sudo systemctl start amazon-ssm-agent
              EOF
}

# EC2 Instance that CANNOT be managed by SSM (no IAM role)
resource "aws_instance" "non_ssm_instance" {
  ami             = var.ami_id
  instance_type   = var.instance_type
  vpc_security_group_ids = [aws_security_group.demo_sg.name]

  tags = {
    Name        = "${var.project_name}-non-ssm"
    Environment = var.environment
    Project     = var.project_name
    Component   = "patch-management"
  }
}
