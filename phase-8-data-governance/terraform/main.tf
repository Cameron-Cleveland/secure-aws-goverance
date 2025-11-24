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

# Local values
locals {
  project_name = "secure-governance-demo"
  environment  = "demo"
  data_bucket  = "${local.project_name}-data-${random_id.suffix.hex}"
}

# Random suffix for unique bucket names
resource "random_id" "suffix" {
  byte_length = 8
}

# Glue Module Only
module "glue" {
  source = "./modules/glue"

  project_name = local.project_name
  environment  = local.environment
  data_bucket  = local.data_bucket
  data_bucket_suffix = random_id.suffix.hex
}
