# Air AI Integration Platform

This repository contains the implementation of Air's AI Integration Platform, providing OCR, transcription, facial recognition, and semantic search capabilities through a scalable microservices architecture.

## Architecture Overview

The system follows a modular, microservices-based architecture deployed on AWS infrastructure. Key components include:

- FastAPI Backend Service
- Qdrant Vector Database for semantic search
- AWS Infrastructure (Terraform)
- Docker-based local development
- CI/CD with GitHub Actions

### AWS Best Practices Implemented

1. **Infrastructure as Code (Terraform)**
   - Version-controlled infrastructure
   - Reproducible environments
   - State management for resources

2. **Containerization**
   - Docker for consistent development and deployment
   - ECS/Fargate for serverless container management
   - Multi-stage builds for optimized images

3. **Security**
   - VPC with private subnets
   - IAM roles with least privilege
   - Secrets management using AWS Secrets Manager

4. **Scalability**
   - Auto-scaling groups for compute resources
   - SQS for message queuing
   - S3 for scalable storage
   - ElastiCache for performance optimization

5. **Monitoring & Observability**
   - CloudWatch metrics and logs
   - X-Ray for distributed tracing
   - Structured logging

## Prerequisites

- Python 3.9+
- Docker
- AWS CLI configured with appropriate credentials
- Terraform 1.0+
- Qdrant (for local development)

## Local Development Setup

1. Clone the repository:
```bash
git clone https://github.com/your-org/air-ai-integration.git
cd air-ai-integration
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the local development environment:
```bash
docker-compose up -d
```

5. Run the FastAPI application:
```bash
uvicorn app.main:app --reload
```

## Infrastructure Deployment

### Terraform Setup

1. Initialize Terraform:
```bash
cd terraform
terraform init
```

2. Review the plan:
```bash
terraform plan
```

3. Apply the infrastructure:
```bash
terraform apply
```

### Infrastructure Components

- VPC with public and private subnets
- ECS Cluster with Fargate
- S3 buckets for asset storage
- RDS Aurora PostgreSQL
- ElastiCache Redis
- SQS queues for job processing
- CloudWatch log groups
- IAM roles and policies

## CI/CD Pipeline

The project uses GitHub Actions for continuous integration and deployment. The pipeline includes:

1. Code quality checks
2. Unit and integration tests
3. Security scanning
4. Infrastructure validation
5. Automated deployment

### GitHub Actions Workflow

1. On push to main branch:
   - Run tests
   - Build Docker image
   - Deploy to staging

2. On pull request:
   - Run tests
   - Code quality checks
   - Security scanning

## API Documentation

The API documentation is available at `/docs` when running the FastAPI application locally.

### Key Endpoints

- `POST /assets` - Upload new assets
- `GET /assets/{asset_id}/status` - Check processing status
- `GET /assets/{asset_id}/results` - Retrieve processing results
- `POST /search` - Semantic search across assets

## Batch Processing

The system supports batch processing through:

1. SQS queues for job management
2. Batch upload API endpoints
3. Parallel processing capabilities
4. Progress tracking and status updates

## Qdrant Integration

The Qdrant class provides methods for:
- Vector data upload
- Similarity search
- Collection management
- Batch operations

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and linting
4. Submit a pull request

## License

Proprietary - All rights reserved 