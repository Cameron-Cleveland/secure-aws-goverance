variable "sso_instance_arn" {
  description = "IAM Identity Center Instance ARN"
  type        = string
  default     = "arn:aws:sso:::instance/ssoins-7223a8440737d354"
}

variable "management_account_id" {
  description = "AWS Management Account ID"
  type        = string
  default     = "867344469617"
}
