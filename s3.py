import boto3
from botocore.exceptions import NoCredentialsError
from django.conf import settings


def upload_file_to_s3_fileobj(file_obj, s3_key_type):
    folder_map = {
        'Pickup': 'waste_pickups',
        'agreements': 'agreements',
        'Audits': 'audit_item_images',
        'Company_profile': 'company_logo',
        'profile': 'profile_photo',
    }

    folder = folder_map.get(s3_key_type, 'misc')
    filename = getattr(file_obj, 'name', str(file_obj))  # Support both file-like and raw strings
    s3_key = f"{folder}/{filename}"

    try:
        s3 = boto3.client(
            's3',
            region_name=getattr(settings, 'AWS_S3_REGION_NAME', 'us-east-1'),
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        s3.upload_fileobj(file_obj, settings.AWS_STORAGE_BUCKET_NAME, s3_key)
        s3_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{s3_key}"
        return s3_url
    except NoCredentialsError:
        return None
