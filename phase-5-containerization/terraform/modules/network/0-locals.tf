locals {
  env         = "staging"
  region      = "us-east-1"
  zone1       = "us-east-1a"
  zone2       = "us-east-1b"
  
  # Project naming
  project_name = "secure-governance-demo"
  
  # EKS name (needed for subnet tags)
  eks_name    = "demo"
  eks_version = "1.34"
  
  # Common tags
  common_tags = {
    Environment = local.env
    Project     = local.project_name
    Component   = "network"
  }
}
