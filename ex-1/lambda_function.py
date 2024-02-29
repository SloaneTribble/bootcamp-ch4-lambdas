import json
import boto3
import csv
# DDB doesn't accept floats
from decimal import *

def lambda_handler(event, context):
    table_name = "stribble-dob-zillow"
    
    try:
        record = event['Records'][0]  # Assuming only one record is present
        
        # Initialize AWS resources
        s3 = boto3.resource('s3')
        dynamodb = boto3.resource('dynamodb')
        ddb_table = dynamodb.Table(table_name)
        
        # Extract bucket name and object key
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']
        
        # Read the CSV file content
        s3_object = s3.Object(bucket_name, object_key)
        data = s3_object.get()['Body'].read().decode("utf-8").splitlines()
        rows = csv.reader(data)
        headers = next(rows)
        
        # Process and store each row in DynamoDB
        for row in rows:
            item = {
                'Index': int(row[0].strip()),
                'LivingSpaceSqFt': int(row[1].strip()),
                'Beds': int(row[2].strip()),
                'Baths': Decimal(row[3].strip()),
                'Zip': row[4].strip(),
                'Year': int(row[5].strip()),
                'ListPrice': int(row[6].strip())
            }
            ddb_table.put_item(Item=item)

    except Exception as e:
        print(f"Error processing S3 event: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps('Error processing CSV')
        }

    return {
        'statusCode': 200,
        'body': json.dumps('CSV processed successfully')
    }
