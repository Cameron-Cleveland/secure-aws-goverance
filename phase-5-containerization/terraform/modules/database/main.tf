# Random password for database
resource "random_password" "db_password" {
  length  = 16
  special = false
}

# DB Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-db-subnet-group"
  subnet_ids = var.private_subnets

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Component   = "database"
  }
}

# RDS Security Group
resource "aws_security_group" "rds_sg" {
  name        = "${var.project_name}-rds-sg"
  description = "Security group for MySQL database"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [var.ecs_security_group_id]
    description     = "Allow ECS tasks to connect to MySQL"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Component   = "database"
  }
}

# MySQL RDS Database
resource "aws_db_instance" "ecom_mysql" {
  identifier              = "${var.project_name}-mysql"
  engine                  = "mysql"
  engine_version          = "8.0"
  instance_class          = "db.t3.micro"
  allocated_storage       = 20
  storage_type            = "gp2"
  db_name                 = "ecomdb"
  username                = "admin"
  password                = random_password.db_password.result
  parameter_group_name    = "default.mysql8.0"
  skip_final_snapshot     = true
  publicly_accessible     = false
  vpc_security_group_ids  = [aws_security_group.rds_sg.id]
  db_subnet_group_name    = aws_db_subnet_group.main.name
  multi_az                = false

  # Backup settings
  backup_retention_period = 7
  backup_window           = "03:00-04:00"
  maintenance_window      = "sun:04:00-sun:05:00"

  # REMOVED Performance Insights - not supported on t3.micro
  # performance_insights_enabled = true

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Component   = "database"
  }
}

# Simple database initialization (optional)
resource "null_resource" "db_setup" {
  depends_on = [aws_db_instance.ecom_mysql]

  provisioner "local-exec" {
    command = <<EOT
      echo "Database created successfully!"
      echo "Endpoint: ${aws_db_instance.ecom_mysql.address}"
      echo "You can manually run SQL scripts to initialize your e-commerce database schema"
    EOT
  }
}
