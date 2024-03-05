import json
import boto3
import csv

def lambda_handler(event, context):
    region = 'us-east-1'

    try:
        ec2 = boto3.client('ec2', region_name=region)
        
        
        # Define the filter to find instances with a specific tag name and value
        filters = [{
            'Name': 'tag:lambda-ex-2',  
            'Values': ['True']  
        }]

        # Use the filter in the describe_instances call
        response = ec2.describe_instances(Filters=filters)

        # Extracting instances from the response using list comprehension
        # (for each instance in each reservation, add it to this list)
        instances = [instance for reservation in response['Reservations'] for instance in reservation['Instances']]

        # Example: print instance IDs
        for instance in instances:
            print(instance)


    except Exception as e:
        print(str(e))

    return {
       'statusCode': 200,
       'body': json.dumps('It got to the end of the function')
     }