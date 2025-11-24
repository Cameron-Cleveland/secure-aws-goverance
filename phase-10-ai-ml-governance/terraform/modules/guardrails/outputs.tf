output "ai_guardrails_policy_arn" {
  description = "ARN of the AI guardrails policy"
  value       = aws_iam_policy.ai_guardrails.arn
}

output "training_data_bucket" {
  description = "Name of the AI training data bucket"
  value       = aws_s3_bucket.ai_training_data.bucket
}
