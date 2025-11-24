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

# Get current account ID for reference
data "aws_caller_identity" "current" {}

# Get AWS Organizations details
data "aws_organizations_organization" "org" {}

# Permission Sets
resource "aws_ssoadmin_permission_set" "administrator" {
  name             = "Administrator"
  description      = "Full administrator access across all services"
  instance_arn     = var.sso_instance_arn
  session_duration = "PT8H"
}

resource "aws_ssoadmin_managed_policy_attachment" "administrator" {
  instance_arn       = var.sso_instance_arn
  managed_policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
  permission_set_arn = aws_ssoadmin_permission_set.administrator.arn
}

resource "aws_ssoadmin_permission_set" "power_user" {
  name             = "PowerUser"
  description      = "Power user access (no IAM management)"
  instance_arn     = var.sso_instance_arn
  session_duration = "PT8H"
}

resource "aws_ssoadmin_managed_policy_attachment" "power_user" {
  instance_arn       = var.sso_instance_arn
  managed_policy_arn = "arn:aws:iam::aws:policy/PowerUserAccess"
  permission_set_arn = aws_ssoadmin_permission_set.power_user.arn
}

resource "aws_ssoadmin_permission_set" "read_only" {
  name             = "ReadOnly"
  description      = "Read-only access for auditing and monitoring"
  instance_arn     = var.sso_instance_arn
  session_duration = "PT8H"
}

resource "aws_ssoadmin_managed_policy_attachment" "read_only" {
  instance_arn       = var.sso_instance_arn
  managed_policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
  permission_set_arn = aws_ssoadmin_permission_set.read_only.arn
}

resource "aws_ssoadmin_permission_set" "security_auditor" {
  name             = "SecurityAuditor"
  description      = "Security and compliance auditing access"
  instance_arn     = var.sso_instance_arn
  session_duration = "PT8H"
}

resource "aws_ssoadmin_managed_policy_attachment" "security_auditor" {
  instance_arn       = var.sso_instance_arn
  managed_policy_arn = "arn:aws:iam::aws:policy/SecurityAudit"
  permission_set_arn = aws_ssoadmin_permission_set.security_auditor.arn
}

# Account Assignments (commented out - requires existing SSO groups)
/*
resource "aws_ssoadmin_account_assignment" "admin_to_management" {
  instance_arn       = var.sso_instance_arn
  permission_set_arn = aws_ssoadmin_permission_set.administrator.arn
  
  principal_type = "GROUP"
  principal_id   = "Administrators"  # This would be your SSO group ID
  
  target_type = "AWS_ACCOUNT"
  target_id   = var.management_account_id
}
*/

# Create SSO Groups (if using Identity Center as identity source)
resource "aws_identitystore_group" "administrators" {
  identity_store_id = tolist(data.aws_ssoadmin_instances.sso.identity_store_ids)[0]
  
  display_name = "Administrators"
  description  = "Full administrator access group"
}

resource "aws_identitystore_group" "developers" {
  identity_store_id = tolist(data.aws_ssoadmin_instances.sso.identity_store_ids)[0]
  
  display_name = "Developers"
  description  = "Developer access group"
}

# Get SSO instances data
data "aws_ssoadmin_instances" "sso" {}

# Account Assignment - Assign Administrators group to Management account with Admin permissions
resource "aws_ssoadmin_account_assignment" "admin_assignment" {
  instance_arn       = var.sso_instance_arn
  permission_set_arn = aws_ssoadmin_permission_set.administrator.arn
  
  principal_type = "GROUP"
  principal_id   = aws_identitystore_group.administrators.group_id
  
  target_type = "AWS_ACCOUNT"
  target_id   = var.management_account_id
}

# Account Assignment - Assign Developers group to Management account with PowerUser permissions
resource "aws_ssoadmin_account_assignment" "developer_assignment" {
  instance_arn       = var.sso_instance_arn
  permission_set_arn = aws_ssoadmin_permission_set.power_user.arn
  
  principal_type = "GROUP"
  principal_id   = aws_identitystore_group.developers.group_id
  
  target_type = "AWS_ACCOUNT"
  target_id   = var.management_account_id
}
