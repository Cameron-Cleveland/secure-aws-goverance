output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = aws_ecr_repository.ecom_app.repository_url
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.ecom_cluster.name
}

output "ecs_service_name" {
  description = "Name of the ECS service"
  value       = aws_ecs_service.ecom_app.name
}

output "ecs_security_group_id" {
  description = "ECS security group ID"
  value       = aws_security_group.ecs_sg.id
}

output "ecr_repository_name" {
  description = "ECR repository name"
  value       = aws_ecr_repository.ecom_app.name
}
