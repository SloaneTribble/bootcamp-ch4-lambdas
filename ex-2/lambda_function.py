import json
import boto3
import csv
from datetime import datetime, timezone, timedelta

# max minutes we would like our instances to run
MAX_RUNNING_MINUTES = 5

# given an elapsed time (in timedelta format), use a timedelta to determine whether 5 minutes have elapsed
# if so, return True; else False
def check_duration(elapsed_time):
    # convert our desired amount of time into a timedelta representing an amount of elapsed time
    threshold = timedelta(minutes=MAX_RUNNING_MINUTES)
    return elapsed_time > threshold
    
    
    

def lambda_handler(event, context):
    region = 'us-east-1'
    
    print(event)

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
            # eventbridge uses utc timezone so we base our calculations on that
            launch_time = instance['LaunchTime']
            current_time = datetime.now(timezone.utc)
            
            # running_duration is of type datetime.timedelta
            running_duration = current_time - launch_time
            print("Launch time: ", instance['LaunchTime'])
            print("Current time: ", current_time)
            print("Running duration: ", running_duration)
            time_limit_reached = check_duration(running_duration)
            if time_limit_reached:
                print("Instance has been running for more than 5 minutes.")
            


    except Exception as e:
        print(str(e))

    return {
       'statusCode': 200,
       'body': json.dumps('It got to the end of the function')
     }
     