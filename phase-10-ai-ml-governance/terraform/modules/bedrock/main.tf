# IAM Role for BedRock Access
resource "aws_iam_role" "bedrock_access_role" {
  name = "${var.project_name}-bedrock-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "bedrock.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Component   = "bedrock"
  }
}

# BedRock Access Policy - UPDATED with correct permissions
resource "aws_iam_role_policy" "bedrock_access" {
  name = "${var.project_name}-bedrock-access"
  role = aws_iam_role.bedrock_access_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream",
          "bedrock:ListFoundationModels",
          "bedrock:GetFoundationModel"
        ]
        Resource = "*"
      }
    ]
  })
}

# Additional policy for model access
resource "aws_iam_policy" "bedrock_model_access" {
  name        = "${var.project_name}-bedrock-model-access"
  description = "Permissions for BedRock model access"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:GetModelInvocationLoggingConfiguration",
          "bedrock:ListCustomModels",
          "bedrock:ListModelCustomizationJobs"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "bedrock_model_access" {
  role       = aws_iam_role.bedrock_access_role.name
  policy_arn = aws_iam_policy.bedrock_model_access.arn
}

# Custom Config Rule for BedRock Governance
resource "aws_config_config_rule" "bedrock_governance" {
  name = "${var.project_name}-bedrock-governance"

  source {
    owner             = "AWS"
    source_identifier = "REQUIRED_TAGS"
  }

  input_parameters = jsonencode({
    tag1Key = "Environment"
    tag2Key = "Project"
  })

  scope {
    compliance_resource_types = ["AWS::Bedrock::Model"]
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# CloudWatch Dashboard for AI Governance
resource "aws_cloudwatch_dashboard" "ai_governance" {
  dashboard_name = "${var.project_name}-ai-governance"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "text"
        x      = 0
        y      = 0
        width  = 24
        height = 6
        properties = {
          markdown = "# AI/ML Governance Dashboard\n## Project: ${var.project_name}\n### Environment: ${var.environment}\n\n**Governance Controls:**\n- BedRock Model Access Policies\n- AI Guardrails Configuration\n- Responsible AI Monitoring\n- Compliance Tracking"
        }
      }
    ]
  })
}
