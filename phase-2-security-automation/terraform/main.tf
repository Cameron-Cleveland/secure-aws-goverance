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

# Security Module
module "security" {
  source = "./modules/security"
  
  project_name = "secure-governance-demo"
  environment  = "demo"
}

# NEW: Storage Module
module "storage" {
  source = "./modules/storage"
  
  project_name = "secure-governance-demo"
  environment  = "demo"
  kms_key_arn  = module.security.kms_key_arn
}

# NEW: Compute Module  
module "compute" {
  source = "./modules/compute"
  
  project_name    = "secure-governance-demo"
  environment     = "demo"
  s3_bucket_name  = module.storage.s3_bucket_name
  s3_bucket_arn   = module.storage.s3_bucket_arn
}