import os
import subprocess
import logging
import boto3
import json

client = boto3.client('s3')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def run_command(command):
    command_list = command.split(' ')

    try:
        logger.info("Running shell command: \"{}\"".format(command))
        logger.info("Running shell command list: \"{}\"".format(command_list))
        result = subprocess.run(command,shell=True, capture_output=True)
        #result = subprocess.run(command_list, stdout=subprocess.PIPE);
        #logger.info("Command output:\n---\n{}\n---".format(result.stdout.decode('UTF-8')))
        if result.returncode != 0:
            print(result.stderr)
            raise ValueError(result.stderr)
        
    except Exception as e:
        logger.error("Exception: {}".format(e))
        return {
                "statusCode": 400,
                "headers": {
                "Content-Type": "application/json"
                },
                "body": str(e)
                }  
    return {
    "statusCode": 200,
    "headers": {
    "Content-Type": "application/json"
    },
    "body": "Site Upload Complete"
    }

def lambda_handler(event, context):
    body = json.loads(event['body'])
    siteId = body['siteId']
    siteDictionary = getSiteDictionary()
    sourceBucketFolder = ""
    targetBucket = ""
    for site in siteDictionary:
        if siteId == site["siteId"]:
            # USER PARAMS:
            sourceBucketFolder = site["previewBucketFolder"]
            targetBucket = site["productionBucket"]
            print(f'Site found! {site}')
            return run_command(f'/opt/aws s3 sync s3://{sourceBucket}/{sourcePrefix}/ s3://{targetBucket}')
    print(f'Site not found for id: {siteId}')
    return {
    "statusCode": 400,
    "headers": {
    "Content-Type": "application/json"
    },
    "body": "Site Not Found"
    }

def getSiteDictionary():
    bucket = os.environ['DICTIONARY_BUCKET'] #dictionary bucket environment variable
    key = os.environ['DICTIONARY_KEY'] #name of the file inside the bucket that contains the sites dictionary
    response = client.get_object(Bucket=bucket, Key=key)
    response = json.loads(response['Body'].read())
    return response
