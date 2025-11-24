terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# Network Module - NO ARGUMENTS (uses locals)
module "network" {
  source = "./modules/network"
}

# Containerization Module - First Pass (with placeholders)
module "containerization" {
  source = "./modules/containerization"

  project_name        = "secure-governance-demo"
  environment         = "demo"
  vpc_id              = module.network.vpc_id
  public_subnets      = module.network.public_subnets
  private_subnets     = module.network.private_subnets
  alb_security_group_id = module.network.alb_security_group_id
  target_group_arn    = module.network.target_group_arn
  database_endpoint   = "temp-placeholder.aws.com"
  database_password   = "temp-password-123"
}

# Database Module
module "database" {
  source = "./modules/database"

  project_name     = "secure-governance-demo"
  environment      = "demo"
  vpc_id           = module.network.vpc_id
  private_subnets  = module.network.private_subnets
  ecs_security_group_id = module.containerization.ecs_security_group_id
}
