import os
import boto3
import base64
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class TestDataUploader:
    def __init__(self):
        # Initialize AWS S3 client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )
        
        # Initialize Qdrant client
        self.qdrant_client = QdrantClient(
            url=os.getenv('QDRANT_CLUSTER'),
            port=int(os.getenv('QDRANT_PORT')),
            api_key=os.getenv('QDRANT_API_KEY')
        )
        
        self.bucket_name = os.getenv('S3_BUCKET_NAME')
        
    def upload_to_s3(self, file_path: str, file_type: str) -> str:
        """Upload file to S3 and return the S3 URL"""
        try:
            file_name = os.path.basename(file_path)
            s3_key = f"test_data/{file_type}/{file_name}"
            
            self.s3_client.upload_file(file_path, self.bucket_name, s3_key)
            s3_url = f"s3://{self.bucket_name}/{s3_key}"
            
            logger.info(f"Successfully uploaded {file_name} to S3: {s3_url}")
            return s3_url
        except Exception as e:
            logger.error(f"Error uploading {file_path} to S3: {str(e)}")
            raise

    def upload_to_qdrant(self, file_path: str, file_type: str, metadata: dict):
        """Upload file content to Qdrant"""
        try:
            # Read and encode file content
            with open(file_path, 'rb') as file:
                content = base64.b64encode(file.read()).decode()
            
            # Create point with metadata
            point = models.PointStruct(
                id=hash(file_path),
                vector=self._get_vector(file_type, content),
                payload={
                    "file_type": file_type,
                    "file_name": os.path.basename(file_path),
                    "s3_url": metadata.get('s3_url'),
                    **metadata
                }
            )
            
            # Upload to appropriate collection
            self.qdrant_client.upsert(
                collection_name=file_type,
                points=[point]
            )
            
            logger.info(f"Successfully uploaded {file_path} to Qdrant")
        except Exception as e:
            logger.error(f"Error uploading {file_path} to Qdrant: {str(e)}")
            raise

    def _get_vector(self, file_type: str, content: str):
        """Get vector representation based on file type"""
        # This is a placeholder - implement actual vectorization logic
        # based on your QdrantHandler implementation
        return [0.0] * 512  # Placeholder vector

def main():
    # Initialize uploader
    uploader = TestDataUploader()
    
    # Test data directory
    test_data_dir = "test_data"
    
    # File types and their corresponding directories
    file_types = {
        'text': 'txt',
        'image': 'jpg',
        'audio': 'mp3',
        'video': 'mp4'
    }
    
    # Process each file type
    for collection, extension in file_types.items():
        for file_name in os.listdir(os.path.join(test_data_dir, collection)):
            if file_name.endswith(f'.{extension}'):
                file_path = os.path.join(test_data_dir, collection, file_name)
                
                try:
                    # Upload to S3
                    s3_url = uploader.upload_to_s3(file_path, collection)
                    
                    # Upload to Qdrant
                    uploader.upload_to_qdrant(
                        file_path,
                        collection,
                        metadata={'s3_url': s3_url}
                    )
                except Exception as e:
                    logger.error(f"Failed to process {file_path}: {str(e)}")

if __name__ == "__main__":
    main() 