import json
import subprocess
import boto3


def lambda_handler(event, context):
    records = event['Records'][0]['s3']
    bucket_name = records['bucket']['name']
    file_name = records['object']['key']
    process_data = 's3://' + bucket_name + '/' + file_name
    ec2 = boto3.client('ec2')
    # Start EC2 instance before running a job
    
    ec2.start_instances(InstanceIds=['i-0e1bec1f1a73319e9'])
    print("Starting EC2 Airflow instance")
    waiter = ec2.get_waiter('instance_running')
    waiter.wait(InstanceIds=['i-0e1bec1f1a73319e9'])
    print("EC2 instance Started")
    # Get Public IP
    response = ec2.describe_instances(InstanceIds=['i-0e1bec1f1a73319e9',],)
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            publicip = instance.get('PublicIpAddress')
            print(publicip)
    # Pinpoint dag directory
    endpoint = f'http://{publicip}:8080/api/experimental/dags/emr_scala_run_dag/dag_runs'
    data = json.dumps({"conf": {'s3_location': process_data}})
    # Trigger Airflow job
    subprocess.run(['curl', '-X', 'POST', endpoint, '--insecure', '-d', data])
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
