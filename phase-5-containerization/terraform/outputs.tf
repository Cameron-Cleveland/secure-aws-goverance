output "load_balancer_url" {
  description = "URL to access the e-commerce application"
  value       = "http://${module.network.alb_dns_name}"
}

output "ecr_repository_url" {
  description = "ECR repository URL for the app"
  value       = module.containerization.ecr_repository_url
}

output "database_endpoint" {
  description = "MySQL database endpoint"
  value       = module.database.database_endpoint
  sensitive   = true
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = module.containerization.ecs_cluster_name
}

output "vpc_id" {
  description = "VPC ID"
  value       = module.network.vpc_id
}
