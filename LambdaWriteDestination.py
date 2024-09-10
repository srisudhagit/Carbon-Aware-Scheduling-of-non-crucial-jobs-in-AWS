import boto3
import json
import tempfile
import os

def lambda_handler(event, context):
        try:
            
            bucket = event["bucket"]
            key = event["key"]
           
            new_key = "new_" + key 
            upload_file_to_s3(bucket, key, new_key)
            return {
            'statusCode': 200,
            'body': 'Object fetched successfully'
            }
        except Exception as e:
            print(f"error processing it: {e}")
            return None
        finally:
            return None

def download_file_from_s3(bucket_name, key):
    # Create a new S3 client
    s3 = boto3.client('s3')

    try:
        # Create a temporary file to store the downloaded content
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file_path = temp_file.name
        
        # Download the object from S3 to the temporary file
        s3.download_fileobj(bucket_name, key, temp_file)
        
        # Close the temporary file
        temp_file.close()
        
        return temp_file_path
    except Exception as e:
        print(f"Error downloading file from S3: {e}")
        return None
    finally:
        temp_file.close()


def upload_file_to_s3(bucket_name, original_key, new_key):
    s3 = boto3.client('s3')
    # Download the original file from S3
    temp_file_path = download_file_from_s3(bucket_name, original_key)
    print(temp_file_path)
    if temp_file_path is None:
        print("none returning")
        return

    try:
        # Read the content of the original file
        with open(temp_file_path, 'rb') as file:
            file_content = file.read()
        print("contents read")
        # Put the object in the S3 bucket with the new key
        s3.put_object(Bucket=bucket_name, Key=new_key, Body=file_content)
        print(f"File with key '{original_key}' successfully uploaded to S3 with new key '{new_key}'")
    except Exception as e:
        print(f"Error uploading file to S3: {e}")
    finally:
        # Delete the temporary file
        os.unlink(temp_file_path)
