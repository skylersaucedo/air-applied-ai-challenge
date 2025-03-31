# Air AI Integration - System Architecture PRD

## Executive Summary

This document outlines a scalable system architecture designed to integrate various AI capabilities into Air's product. The architecture supports OCR, transcription, facial recognition, and semantic search while ensuring high performance, cost optimization, and future extensibility.

## 1. System Architecture Overview

### 1.1 High-Level Architecture

The proposed system follows a modular, microservices-based architecture deployed on AWS infrastructure. This approach enables independent scaling of AI services and facilitates future AI model integration.

![System Architecture Diagram]

#### Core Components:

1. **API Gateway Layer**: Serves as the entry point for all client requests
2. **Orchestration Service**: Coordinates workflow between services and manages job queuing
3. **AI Service Modules**: Independent services for each AI capability 
4. **Data Processing Pipeline**: Handles asset ingestion, preprocessing, and persistence
5. **Storage Solutions**: Tiered storage approach for different data requirements
6. **Metadata & Search Engine**: Manages indexing and retrieval of processed assets

### 1.2 Infrastructure (AWS)

- **Compute**: Combination of AWS Fargate (for consistent workloads) and Lambda (for event-driven processing)
- **Storage**: S3 for raw assets, with lifecycle policies for cost optimization
- **Database**: Aurora PostgreSQL for relational data, DynamoDB for metadata
- **AI Services**: Mix of managed services and custom model deployments on ECS/Fargate
- **Networking**: VPC with private subnets for secure communication
- **Caching**: ElastiCache for Redis to improve performance of frequent operations
- **Monitoring**: CloudWatch, X-Ray for observability

## 2. AI Model Implementation Strategy

### 2.1 OCR (Optical Character Recognition)

**Model Selection**: Google Cloud Vision API (Gemini 2.5 Flash)

**Implementation Approach**:
- Managed API integration through AWS API Gateway
- Request packet preprocessing to optimize image quality
- Structured schema for standardized output format
- Batch processing capability for high volume workloads

**Scaling Strategy**:
- Increase TPM (Tokens Per Minute) limits with Google for batch processing
- Implement request throttling and queuing for load management
- Caching of results for repeated asset processing

### 2.2 Transcription (Speech-to-Text)

**Model Selection**: OpenAI Whisper model through API

**Implementation Approach**:
- Audio preprocessing service to improve quality:
  - Noise reduction
  - Audio normalization
  - Channel separation for multi-speaker content
- Asynchronous processing for long-form content
- Speaker diarization for multi-speaker content

**Optimization Considerations**:
- Chunking strategy for long audio files
- Transcription confidence scoring for quality assurance
- Language detection and specialized models for multilingual content

### 2.3 Facial Recognition

**Model Selection**: YOLOv8 for face detection + RetinaFace for facial landmarks

**Implementation Approach**:
- Containerized deployment on ECS/Fargate
- Multi-stage pipeline:
  1. Face detection using YOLOv8
  2. Feature extraction using RetinaFace
  3. Embedding generation for search/matching
- Privacy-preserving design with opt-in requirements

**Storage Considerations**:
- Secure storage of facial embeddings
- Compliance with privacy regulations
- Regular purging policies for unused data

### 2.4 Semantic Search

**Model Selection**: OpenAI text-embedding-3-large for vectorization + Qdrant for vector storage and search

**Implementation Approach**:
- Asynchronous document processing and embedding generation
- Efficient storage of embeddings in Qdrant vector database
- Query understanding and expansion for improved results
- Hybrid search combining vector and keyword approaches

**Performance Optimization**:
- Index partitioning for large-scale deployments
- Caching of common search patterns
- Approximate nearest neighbor (ANN) algorithms for speed

## 3. Data Pipeline Architecture

### 3.1 Ingestion Layer

- **S3-triggered Lambda** for new asset detection
- **SQS queues** for managing processing backlog
- **Batch ingestion API** for high-volume uploads
- **Validation service** to ensure asset integrity

### 3.2 Processing Workflow

```
Asset Upload → Validation → Metadata Extraction → AI Processing Queue → 
Model-specific Processing → Result Standardization → Storage & Indexing
```

### 3.3 Storage Strategy

- **Raw Assets**: S3 Standard for active assets, Glacier for archival
- **Processed Results**: DynamoDB for metadata, S3 for large result sets
- **Embeddings**: Qdrant for vector data, with regular backup to S3
- **Temporary Storage**: Ephemeral storage for processing, with automatic cleanup

## 4. API & Workflow Design

### 4.1 Core APIs

#### 4.1.1 Asset Management API
```json
POST /assets
{
  "file": "binary_data",
  "metadata": {
    "name": "string",
    "type": "image|video|audio|document",
    "tags": ["string"]
  },
  "processing_options": {
    "ai_services": ["ocr", "facial_recognition", "transcription", "semantic_indexing"],
    "priority": "normal|high|batch"
  }
}
```

#### 4.1.2 Processing Status API
```json
GET /assets/{asset_id}/status
Response:
{
  "asset_id": "string",
  "status": "pending|processing|completed|failed",
  "services": {
    "ocr": {"status": "string", "progress": "number"},
    "facial_recognition": {"status": "string", "progress": "number"},
    "transcription": {"status": "string", "progress": "number"},
    "semantic_indexing": {"status": "string", "progress": "number"}
  },
  "estimated_completion": "timestamp"
}
```

#### 4.1.3 Results Retrieval API
```json
GET /assets/{asset_id}/results?service={service_name}
Response:
{
  "asset_id": "string",
  "service": "string",
  "results": {
    // Service-specific result structure
  },
  "metadata": {
    "processed_at": "timestamp",
    "model_version": "string",
    "confidence": "number"
  }
}
```

#### 4.1.4 Search API
```json
POST /search
{
  "query": "string",
  "filters": {
    "asset_types": ["image", "video", "audio", "document"],
    "date_range": {"start": "timestamp", "end": "timestamp"},
    "tags": ["string"]
  },
  "search_type": "semantic|keyword|hybrid",
  "limit": "number",
  "offset": "number"
}
```

### 4.2 Data Structures & Metadata Schema

#### 4.2.1 Asset Metadata
```json
{
  "asset_id": "uuid",
  "filename": "string",
  "file_type": "string",
  "mime_type": "string",
  "size_bytes": "number",
  "created_at": "timestamp",
  "modified_at": "timestamp",
  "uploaded_by": "user_id",
  "tags": ["string"],
  "custom_metadata": "object"
}
```

#### 4.2.2 OCR Result Schema
```json
{
  "text": "string",
  "confidence": "number",
  "blocks": [
    {
      "text": "string",
      "bounding_box": {"x": "number", "y": "number", "width": "number", "height": "number"},
      "confidence": "number",
      "type": "paragraph|line|word"
    }
  ],
  "language": "string"
}
```

#### 4.2.3 Transcription Result Schema
```json
{
  "full_text": "string",
  "segments": [
    {
      "text": "string",
      "start_time": "number",
      "end_time": "number",
      "speaker": "string|null",
      "confidence": "number"
    }
  ],
  "language": "string",
  "duration_seconds": "number"
}
```

#### 4.2.4 Facial Recognition Result Schema
```json
{
  "faces": [
    {
      "bounding_box": {"x": "number", "y": "number", "width": "number", "height": "number"},
      "confidence": "number",
      "landmarks": {
        "left_eye": {"x": "number", "y": "number"},
        "right_eye": {"x": "number", "y": "number"},
        "nose": {"x": "number", "y": "number"},
        "mouth_left": {"x": "number", "y": "number"},
        "mouth_right": {"x": "number", "y": "number"}
      },
      "embedding_id": "string",  // Reference to securely stored embedding
      "attributes": {
        "age_estimate": "number",
        "gender": "string",
        "emotion": "string"
      }
    }
  ],
  "image_id": "string",
  "processing_time": "number"
}
```

#### 4.2.5 Vector Embedding Metadata
```json
{
  "embedding_id": "string",
  "source_asset_id": "string",
  "model_version": "string",
  "vector_dimension": "number",
  "created_at": "timestamp",
  "embedding_type": "text|image|face|audio",
  "collection": "string"
}
```

### 4.3 Data Flow Diagrams

#### 4.3.1 Image Processing Flow
```
Image Upload → S3 → Lambda Trigger → 
Metadata Extraction → SQS → 
[OCR Processing, Facial Recognition] (parallel) → 
Results Storage → Embedding Generation → 
Vector Storage → Indexing Completion
```

#### 4.3.2 Audio Processing Flow
```
Audio Upload → S3 → Lambda Trigger → 
Metadata Extraction → Audio Preprocessing → 
Transcription Queue → Transcription Processing → 
Results Storage → Text Embedding Generation → 
Vector Storage → Indexing Completion
```

## 5. Performance Considerations

### 5.1 Eliminating Unnecessary Reprocessing

- **Fingerprinting** system for asset deduplication
- **Change detection** to only process modified portions of assets
- **Caching** of processing results with TTL based on usage patterns
- **Processing history** database to track previous operations

### 5.2 Compute Scaling Strategy

- **On-demand processing** for user-initiated, interactive workflows
- **Batch processing** for background operations and bulk uploads
- **Auto-scaling** based on queue depth and processing latency
- **Reserved capacity** for critical operations with AWS Capacity Reservations

### 5.3 Inference Optimization

- **GPU instances** (g4dn, g5) for facial recognition and intensive neural network operations
- **CPU optimization** for text processing and metadata operations
- **Serverless** functions for event-driven, bursty workloads
- **Container optimization** with right-sized resources based on model requirements

### 5.4 Storage Scaling

- **Vector database partitioning** for handling growth beyond single-node capacity
- **Tiered storage** approach to balance cost and performance
- **Read replicas** for high-query workloads
- **Caching layer** for frequently accessed embeddings and metadata

## 6. CI/CD Pipeline

### 6.1 Development Workflow

- **Feature branches** with automated testing
- **Model versioning** with clear tracking between code and model versions
- **Infrastructure as Code** using Terraform for all AWS resources
- **Containerization** of all services using Docker

### 6.2 Deployment Strategy

- **GitHub Actions** for CI/CD automation
- **Blue/Green deployments** for zero-downtime updates
- **Canary releases** for AI model updates to validate performance
- **AWS CodeDeploy** integration for managed deployments

### 6.3 Terraform Configuration Strategy

- **Modular approach** with reusable components
- **Environment segregation** (dev, staging, production)
- **State management** in S3 with locking via DynamoDB
- **Secret management** via AWS Secrets Manager

## 7. Phased Rollout Plan

### 7.1 Phase 1: Foundation (Weeks 1-4)
- Core infrastructure deployment with Terraform
- Base API implementation
- Integration of OCR capabilities
- Initial data pipeline for images

### 7.2 Phase 2: Core AI Services (Weeks 5-8)
- Transcription service integration
- Facial recognition pipeline
- Basic semantic search implementation
- Enhanced metadata schema

### 7.3 Phase 3: Scaling & Optimization (Weeks 9-12)
- Performance tuning and bottleneck resolution
- Advanced batch processing capabilities
- Extended API features
- Comprehensive monitoring and alerting

### 7.4 Phase 4: Advanced Features (Weeks 13-16)
- Enhanced semantic search with hybrid approaches
- Cross-modal search capabilities
- Advanced analytics dashboard
- Self-healing system components

## 8. Proof of Concept Implementation

### 8.1 Terraform Configuration Sample

```hcl
# Example Terraform configuration for AI processing pipeline

provider "aws" {
  region = "us-west-2"
}

# VPC and networking
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  
  name = "air-ai-vpc"
  cidr = "10.0.0.0/16"
  
  azs             = ["us-west-2a", "us-west-2b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]
  
  enable_nat_gateway = true
}

# S3 Bucket for asset storage
resource "aws_s3_bucket" "assets" {
  bucket = "air-ai-assets"
  
  lifecycle_rule {
    id      = "archive-rule"
    enabled = true
    
    transition {
      days          = 90
      storage_class = "GLACIER"
    }
  }
}

# SQS Queue for processing jobs
resource "aws_sqs_queue" "processing_queue" {
  name                       = "air-ai-processing-queue"
  visibility_timeout_seconds = 900
  message_retention_seconds  = 86400
  
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.processing_dlq.arn
    maxReceiveCount     = 5
  })
}

resource "aws_sqs_queue" "processing_dlq" {
  name = "air-ai-processing-dlq"
}

# Fargate cluster for AI processing
resource "aws_ecs_cluster" "ai_cluster" {
  name = "air-ai-cluster"
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# Task definition for OCR processing
resource "aws_ecs_task_definition" "ocr_task" {
  family                   = "air-ocr-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 1024
  memory                   = 2048
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn
  
  container_definitions = jsonencode([
    {
      name      = "ocr-service"
      image     = "${aws_ecr_repository.ocr_repo.repository_url}:latest"
      essential = true
      
      portMappings = [
        {
          containerPort = 8080
          hostPort      = 8080
        }
      ]
      
      environment = [
        {
          name  = "GOOGLE_APPLICATION_CREDENTIALS"
          value = "/secrets/google-credentials.json"
        }
      ]
      
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/air-ocr-task"
          "awslogs-region"        = "us-west-2"
          "awslogs-stream-prefix" = "ocr"
        }
      }
    }
  ])
}
```

### 8.2 Sample AWS Lambda Function for Asset Processing

```python
import json
import boto3
import os
import uuid
from datetime import datetime

s3_client = boto3.client('s3')
sqs_client = boto3.client('sqs')
dynamodb = boto3.resource('dynamodb')

PROCESSING_QUEUE_URL = os.environ['PROCESSING_QUEUE_URL']
METADATA_TABLE = os.environ['METADATA_TABLE']

def lambda_handler(event, context):
    # Process S3 event
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        
        # Generate unique asset ID
        asset_id = str(uuid.uuid4())
        
        # Extract basic metadata
        response = s3_client.head_object(Bucket=bucket, Key=key)
        content_type = response['ContentType']
        size = response['ContentLength']
        
        # Determine which AI services to apply based on content type
        ai_services = []
        if content_type.startswith('image/'):
            ai_services.extend(['ocr', 'facial_recognition'])
        elif content_type.startswith('audio/') or content_type.startswith('video/'):
            ai_services.append('transcription')
        
        # Add semantic indexing for all content types
        ai_services.append('semantic_indexing')
        
        # Store metadata in DynamoDB
        table = dynamodb.Table(METADATA_TABLE)
        table.put_item(
            Item={
                'asset_id': asset_id,
                'bucket': bucket,
                'key': key,
                'mime_type': content_type,
                'size_bytes': size,
                'created_at': datetime.now().isoformat(),
                'status': 'pending',
                'ai_services': ai_services
            }
        )
        
        # Queue processing tasks
        for service in ai_services:
            sqs_client.send_message(
                QueueUrl=PROCESSING_QUEUE_URL,
                MessageBody=json.dumps({
                    'asset_id': asset_id,
                    'bucket': bucket,
                    'key': key,
                    'service': service
                })
            )
        
    return {
        'statusCode': 200,
        'body': json.dumps('Processing initiated')
    }
```

## 9. Evaluation Success Metrics

### 9.1 Performance Metrics
- Processing latency under 2 seconds for interactive requests
- Batch processing throughput of 1000+ assets per hour
- API response time under 100ms for metadata operations
- Search query response under 200ms for 99th percentile

### 9.2 Reliability Metrics
- 99.9% uptime for core services
- Zero data loss during processing
- Automatic recovery from transient failures
- Graceful degradation under load

### 9.3 Cost Efficiency Metrics
- Processing cost under $0.05 per asset
- Storage optimization reducing costs by 40% vs. naive approach
- Compute utilization above 70% for reserved resources
- Predictable scaling with linear cost growth

## 10. Conclusion & Next Steps

The proposed architecture provides a robust foundation for integrating AI capabilities into Air's product while ensuring scalability, reliability, and cost-effectiveness. By leveraging AWS's managed services and implementing a modular design, the system can easily evolve to incorporate new AI models and capabilities in the future.

Immediate next steps include:

1. Finalize infrastructure as code templates
2. Develop core API specifications
3. Implement initial proof-of-concept for the OCR pipeline
4. Establish monitoring and alerting infrastructure
5. Begin iterative development following the phased rollout plan

This architecture aligns with the challenge objectives while providing a clear path to implementation and future growth.
