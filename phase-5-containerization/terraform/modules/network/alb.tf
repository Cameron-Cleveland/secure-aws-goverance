# Application Load Balancer
resource "aws_lb" "ecom_app" {
  name               = "${local.project_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets           = [aws_subnet.public_zone1.id, aws_subnet.public_zone2.id]

  enable_deletion_protection = false

  tags = merge(local.common_tags, {
    Name = "${local.project_name}-alb"
  })
}

# ALB Security Group
resource "aws_security_group" "alb_sg" {
  name        = "${local.project_name}-alb-sg"
  description = "Security group for Application Load Balancer"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${local.project_name}-alb-sg"
  })
}

# ALB Target Group
resource "aws_lb_target_group" "ecom_app" {
  name        = "${local.project_name}-tg"
  port        = 80
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = aws_vpc.main.id

  health_check {
    enabled             = true
    path                = "/health-check.php"
    port                = "traffic-port"
    protocol            = "HTTP"
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }

  tags = merge(local.common_tags, {
    Name = "${local.project_name}-tg"
  })
}

# ALB Listener
resource "aws_lb_listener" "ecom_app" {
  load_balancer_arn = aws_lb.ecom_app.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ecom_app.arn
  }

  tags = merge(local.common_tags, {
    Name = "${local.project_name}-listener"
  })
}
