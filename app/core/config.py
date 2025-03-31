from pydantic import BaseSettings


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Air Applied AI Challenge"

    # AWS Configuration
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "us-east-2"

    # S3 Configuration
    S3_BUCKET_NAME: str = "air-ai-storage"

    # SQS Configuration
    SQS_QUEUE_URL: str = (
        "https://sqs.us-east-2.amazonaws.com/"
        "your-account-id/air-ai-processing-development"
    )

    # Database Configuration
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # Qdrant Configuration
    QDRANT_CLUSTER: str
    QDRANT_PORT: int = 6333

    # Security Settings
    SECRET_KEY: str = "your-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Model Settings
    MODEL_PATH: str = "models"
    BATCH_SIZE: int = 32

    class Config:
        case_sensitive = True
