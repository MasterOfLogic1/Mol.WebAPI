import requests
from django.conf import settings
from apps.shared.models import InternalServerError
from apps.shared.serializers import SendVerificationEmailSerializer
from minio import Minio
from minio.error import S3Error
import os

def send_email(subject, body, recipients):
    # Initialize email data using the serializer
    email_serializer = SendVerificationEmailSerializer(data={
        "subject": subject,
        "body": body,
        "to": recipients
    })

    # Validate the email data
    email_serializer.is_valid(raise_exception=True)

    # Send email via SMTP API
    response = requests.post(
        settings.SMTP_SEND_MAIL_URL,
        json=email_serializer.validated_data,
        headers={"Authorization": f"Bearer {settings.SMTP_API_KEY}"}
    )

    # Check if the email was sent successfully
    if response.status_code != 200:
        raise InternalServerError(f"Failed to send email: {response.text}")

    return {"message": "Email sent successfully."}


def upload_file_to_minio(file, object_name, bucket_name=None, content_type=None):
    """
    Upload a file to MinIO storage bucket on Railway.
    
    Args:
        file: File object (Django UploadedFile, file-like object, or file path string)
        object_name: Name/path of the object in the bucket (e.g., 'uploads/image.jpg')
        bucket_name: Name of the bucket (defaults to MINIO_BUCKET_NAME from settings)
        content_type: MIME type of the file (e.g., 'image/jpeg', 'application/pdf')
    
    Returns:
        dict: Contains 'url' (full URL to the file) and 'object_name' (path in bucket)
    
    Raises:
        InternalServerError: If upload fails or MinIO is not configured
    """
    # Validate MinIO configuration
    if not all([settings.MINIO_ENDPOINT, settings.MINIO_ACCESS_KEY, settings.MINIO_SECRET_KEY]):
        raise InternalServerError("MinIO configuration is missing. Please set MINIO_ENDPOINT, MINIO_ACCESS_KEY, and MINIO_SECRET_KEY in environment variables.")
    
    # Use provided bucket name or default from settings
    bucket = bucket_name or settings.MINIO_BUCKET_NAME
    if not bucket:
        raise InternalServerError("Bucket name is required. Provide bucket_name parameter or set MINIO_BUCKET_NAME in environment variables.")
    
    try:
        # Initialize MinIO client
        minio_client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        
        # Ensure bucket exists
        if not minio_client.bucket_exists(bucket):
            minio_client.make_bucket(bucket)
        
        # Handle different file input types
        if isinstance(file, str):
            # File path string
            file_path = file
            file_size = os.path.getsize(file_path)
            with open(file_path, 'rb') as file_data:
                minio_client.put_object(
                    bucket,
                    object_name,
                    file_data,
                    file_size,
                    content_type=content_type
                )
        elif hasattr(file, 'read'):
            # File-like object (Django UploadedFile, BytesIO, etc.)
            if hasattr(file, 'size'):
                # Django UploadedFile
                file_size = file.size
                if not content_type and hasattr(file, 'content_type'):
                    content_type = file.content_type
            else:
                # Generic file-like object - need to read to get size
                file.seek(0, os.SEEK_END)
                file_size = file.tell()
                file.seek(0)
            
            minio_client.put_object(
                bucket,
                object_name,
                file,
                file_size,
                content_type=content_type
            )
        else:
            raise InternalServerError("Invalid file type. Expected file path string, file-like object, or Django UploadedFile.")
        
        # Construct the file URL
        protocol = 'https' if settings.MINIO_SECURE else 'http'
        file_url = f"{protocol}://{settings.MINIO_ENDPOINT}/{bucket}/{object_name}"
        
        return {
            "url": file_url,
            "object_name": object_name,
            "bucket": bucket,
            "message": "File uploaded successfully."
        }
        
    except S3Error as e:
        raise InternalServerError(f"Failed to upload file to MinIO: {str(e)}")
    except Exception as e:
        raise InternalServerError(f"Unexpected error uploading file to MinIO: {str(e)}")
