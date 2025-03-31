terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }

  backend "s3" {
    bucket         = "air-ai-terraform-state"
    key            = "terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC Configuration
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"

  name = "air-ai-vpc"
  cidr = var.vpc_cidr

  azs             = var.availability_zones
  private_subnets = var.private_subnet_cidrs
  public_subnets  = var.public_subnet_cidrs

  enable_nat_gateway = true
  single_nat_gateway = var.environment == "production" ? false : true

  tags = {
    Environment = var.environment
    Project     = "air-ai"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "air-ai-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Environment = var.environment
    Project     = "air-ai"
  }
}

# S3 Buckets
resource "aws_s3_bucket" "assets" {
  bucket = "air-ai-assets-${var.environment}"

  tags = {
    Environment = var.environment
    Project     = "air-ai"
  }
}

resource "aws_s3_bucket_versioning" "assets" {
  bucket = aws_s3_bucket.assets.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "assets" {
  bucket = aws_s3_bucket.assets.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# RDS Aurora PostgreSQL
module "aurora_postgresql" {
  source  = "terraform-aws-modules/rds-aurora/aws"
  version = "~> 8.0"

  name           = "air-ai-db"
  engine         = "aurora-postgresql"
  engine_version = "14.6"
  instance_class = var.environment == "production" ? "db.r5.large" : "db.t3.medium"

  vpc_id                 = module.vpc.vpc_id
  db_subnet_group_name   = module.vpc.database_subnet_group_name
  create_security_group  = true
  allowed_cidr_blocks    = module.vpc.private_subnets_cidr_blocks

  serverlessv2_scaling_configuration = {
    min_capacity = 0.5
    max_capacity = 16
  }

  tags = {
    Environment = var.environment
    Project     = "air-ai"
  }
}

# ElastiCache Redis
resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "air-ai-redis"
  engine              = "redis"
  node_type           = var.environment == "production" ? "cache.r5.large" : "cache.t3.micro"
  num_cache_nodes     = var.environment == "production" ? 2 : 1
  parameter_group_family = "redis6.x"
  port                = 6379
  security_group_ids  = [aws_security_group.redis.id]

  tags = {
    Environment = var.environment
    Project     = "air-ai"
  }
}

# SQS Queue
resource "aws_sqs_queue" "processing" {
  name = "air-ai-processing-${var.environment}"

  visibility_timeout_seconds = 300
  message_retention_seconds = 345600  # 4 days

  tags = {
    Environment = var.environment
    Project     = "air-ai"
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "app" {
  name              = "/ecs/air-ai-${var.environment}"
  retention_in_days = 30

  tags = {
    Environment = var.environment
    Project     = "air-ai"
  }
}

# IAM Roles
resource "aws_iam_role" "ecs_task" {
  name = "air-ai-ecs-task-${var.environment}"

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
    Project     = "air-ai"
  }
}

# Security Groups
resource "aws_security_group" "redis" {
  name        = "air-ai-redis-${var.environment}"
  description = "Security group for Redis cluster"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
  }

  tags = {
    Environment = var.environment
    Project     = "air-ai"
  }
}

resource "aws_security_group" "ecs_tasks" {
  name        = "air-ai-ecs-tasks-${var.environment}"
  description = "Security group for ECS tasks"
  vpc_id      = module.vpc.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Environment = var.environment
    Project     = "air-ai"
  }
} 