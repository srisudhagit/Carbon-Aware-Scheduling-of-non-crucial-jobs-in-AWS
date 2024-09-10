import boto3
import json

def lambda_handler(event, context):
    # Extract information from the S3 event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    #bucket = "gc-project-bucket"
    #key = "Ground_2CK_0003.tif"
    
    # Start the Step Function execution with input data
    stepfunctions = boto3.client('stepfunctions')
    input_data = {
        "bucket": bucket,
        "key": key
    }
    response = stepfunctions.start_execution(
        stateMachineArn='arn:aws:states:us-east-2:360914461006:stateMachine:Schedule_for_besttime_workflow',
        input=json.dumps(input_data)
    )

    return {
        'statusCode': 200,
        #'body': json.dumps(response)
    }
