output "database_endpoint" {
  description = "MySQL database endpoint"
  value       = aws_db_instance.ecom_mysql.address
}

output "database_port" {
  description = "MySQL database port"
  value       = aws_db_instance.ecom_mysql.port
}

output "database_name" {
  description = "MySQL database name"
  value       = aws_db_instance.ecom_mysql.db_name
}

output "database_username" {
  description = "MySQL database username"
  value       = aws_db_instance.ecom_mysql.username
}

output "database_password" {
  description = "MySQL database password"
  value       = random_password.db_password.result
  sensitive   = true
}

output "rds_security_group_id" {
  description = "RDS security group ID"
  value       = aws_security_group.rds_sg.id
}
