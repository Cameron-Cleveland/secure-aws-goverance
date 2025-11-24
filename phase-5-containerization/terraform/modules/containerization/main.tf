# ECR Repository for e-commerce app
resource "aws_ecr_repository" "ecom_app" {
  name = "${var.project_name}-ecom-app"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Component   = "containerization"
  }
}

# ECR Lifecycle Policy
resource "aws_ecr_lifecycle_policy" "ecom_app" {
  repository = aws_ecr_repository.ecom_app.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 10 images"
        action       = {
          type = "expire"
        }
        selection     = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 10
        }
      }
    ]
  })
}

# ECS Cluster
resource "aws_ecs_cluster" "ecom_cluster" {
  name = "${var.project_name}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Component   = "containerization"
  }
}

# ECS Task Execution Role
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "${var.project_name}-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Component   = "containerization"
  }
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ECS Task Role
resource "aws_iam_role" "ecs_task_role" {
  name = "${var.project_name}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Component   = "containerization"
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "ecom_app" {
  name              = "/ecs/${var.project_name}-app"
  retention_in_days = 7

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Component   = "containerization"
  }
}

# ECS Security Group
resource "aws_security_group" "ecs_sg" {
  name        = "${var.project_name}-ecs-sg"
  description = "Security group for ECS tasks"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [var.alb_security_group_id]
    description     = "Allow traffic from ALB"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Component   = "containerization"
  }
}

# ECS Task Definition
resource "aws_ecs_task_definition" "ecom_app" {
  family                   = "${var.project_name}-app"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([{
    name      = "ecom-app"
    image     = "${aws_ecr_repository.ecom_app.repository_url}:latest"
    essential = true
    
    portMappings = [{
      containerPort = 80
      hostPort      = 80
      protocol      = "tcp"
    }]
    
    # DATABASE ENVIRONMENT VARIABLES
    environment = [
      {
        name  = "DB_HOST"
        value = var.database_endpoint
      },
      {
        name  = "DB_USER"
        value = "admin"
      },
      {
        name  = "DB_PASSWORD"
        value = var.database_password
      },
      {
        name  = "DB_NAME"
        value = "ecomdb"
      },
      {
        name  = "ENVIRONMENT"
        value = var.environment
      }
    ]
    
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.ecom_app.name
        awslogs-region        = "us-east-1"
        awslogs-stream-prefix = "ecs"
      }
    }
    
    healthCheck = {
      command     = ["CMD-SHELL", "curl -f http://localhost/health-check.php || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 60
    }
  }])

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Component   = "containerization"
  }
}

# ECS Service
resource "aws_ecs_service" "ecom_app" {
  name            = "${var.project_name}-service"
  cluster         = aws_ecs_cluster.ecom_cluster.id
  task_definition = aws_ecs_task_definition.ecom_app.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnets
    security_groups  = [aws_security_group.ecs_sg.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = var.target_group_arn
    container_name   = "ecom-app"
    container_port   = 80
  }

  depends_on = []

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Component   = "containerization"
  }

  # Allow external changes without Terraform plan conflict
  lifecycle {
    ignore_changes = [desired_count]
  }
}
