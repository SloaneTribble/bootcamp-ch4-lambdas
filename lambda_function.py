import json
import boto3
import csv

def lambda_handler(event,context):
    record_list = []
    
    table_name = "stribble-dob-zillow"

    try:
        
        record_list = event['Records']
        # we're only interested in the first record for this exercise
        record = record_list[0]
        
        # Create an S3 resource
        s3 = boto3.resource('s3')

        # Create a DynamoDB resource
        dynamodb = boto3.resource('dynamodb')

        # grab dynamoDB table using dynamodb resource 
        ddb_table = dynamodb.Table(table_name)

        # grab s3 object using your s3 resource, bucket name and object key from event record
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']
        
        s3_object = s3.Object(bucket_name, object_key)
        print("object: ", s3_object)
        
        data = s3_object.get()['Body'].read().decode("utf-8").splitlines()
        lines=csv.reader(data)
        headers=next(lines)
        print(headers)

        for user_data in lines:
           print(user_data)

         # Create items here for your dynamodb table based on provided .csv file

    except Exception as e:
        print(str(e))

    return {
        'statusCode': 200,
        'body': json.dumps('CSV success')
        }