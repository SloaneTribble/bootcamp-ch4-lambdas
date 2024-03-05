import json
import boto3
import csv
from datetime import datetime, timezone, timedelta


# max minutes we would like our instances to run
MAX_RUNNING_MINUTES = 1

def put_item(ddb_table, item):
    try:
        response = ddb_table.put_item(Item=item)
        print("Item inserted successfully:", response)
        return True, response
    except Exception as e:
        print("Error inserting item:", e)
        return False, e
    

# given an elapsed time (in timedelta format), use a timedelta to determine whether 5 minutes have elapsed
# if so, returns True; else False
def check_duration(elapsed_time):
    # convert our desired amount of time into a timedelta representing an amount of elapsed time
    threshold = timedelta(minutes=MAX_RUNNING_MINUTES)
    return elapsed_time > threshold

# given an instance json object, check whether the instance has been running past a certain threshold 
# if so, returns True, running_duration; else False, None
def check_if_running_past_threshold(instance):
    instance_state = (instance['State']['Name'])
    print("State of instance: ", instance_state)
    # first check if instance is running
    # if it is, check how long since launch time to determine how long it's been running
    # else launch time is irrelevant, and skip this instance 
    if not instance_state == "running":
        return False, None
            
    # eventbridge uses utc timezone so we base our calculations on that
    launch_time = instance['LaunchTime']
    current_time = datetime.now(timezone.utc)
            
    # running_duration is of type datetime.timedelta
    running_duration = current_time - launch_time
    print("Launch time: ", instance['LaunchTime'])
    print("Current time: ", current_time)
    print("Running duration: ", running_duration)
    time_limit_reached = check_duration(running_duration)
    # return Bool representing whether instance has been running past threhold
    return time_limit_reached, running_duration
    

def lambda_handler(event, context):
    region = 'us-east-1'
    table_name = "stribble-dob-lambda-ex-2"
    
    print(event)

    try:
        # create objects representing the ddb and ec2 services to allow us to interact with them more easily
        dynamodb = boto3.resource('dynamodb')
        ddb_table = dynamodb.Table(table_name)
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
            running_past_time_limit, running_duration = check_if_running_past_threshold(instance)
            if running_past_time_limit:
                print("Instance has been running past max allowed minutes.", running_duration)
                # retrieve instance id
                instance_id = instance['InstanceId']
                # convert running_duration timedelta to total seconds
                running_duration_seconds = running_duration.total_seconds()

                running_duration_seconds = int(running_duration_seconds)
                
                # stop instance
                try:
                    response = ec2.stop_instances(InstanceIds=[instance_id])
                    stopped_time = datetime.now().isoformat()
                    status_message = "Instance successfully stopped."
                    print("Attempted to stop instance. Response: ", response)
                
                    # save some information about this instance to a ddb table
                    # Prepare the item you want to put in the table
                    item = {
                        'instance': instance_id,  # instance is partition key of our ddb table
                        'stoppedTime': stopped_time,
                        'running_duration(s)': running_duration_seconds,
                        'statusMessage': status_message
                    }
                    response, success = put_item(ddb_table, item)
                    if success:
                        print("Successfully put item to table with response: ", response)
                    else:
                        print("Failed to put item.  Response: ", response)
                    
                except Exception as e:
                    print(str(e))
            


    except Exception as e:
        print(str(e))

    return {
       'statusCode': 200,
       'body': json.dumps('It got to the end of the function')
     }
     