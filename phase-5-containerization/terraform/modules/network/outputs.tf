output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnets" {
  description = "List of public subnet IDs"
  value       = [aws_subnet.public_zone1.id, aws_subnet.public_zone2.id]
}

output "private_subnets" {
  description = "List of private subnet IDs"
  value       = [aws_subnet.private_zone1.id, aws_subnet.private_zone2.id]
}

output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = aws_lb.ecom_app.dns_name
}

output "alb_security_group_id" {
  description = "ALB security group ID"
  value       = aws_security_group.alb_sg.id
}

output "target_group_arn" {
  description = "ALB target group ARN"
  value       = aws_lb_target_group.ecom_app.arn
}

output "vpc_cidr" {
  description = "VPC CIDR block"
  value       = aws_vpc.main.cidr_block
}
