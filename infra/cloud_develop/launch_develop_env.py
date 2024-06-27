"""
Launch this py file with Run and Debug to quickly launch an EC2 which builds the project and docker containers for remote development.
You can then use VSCode Remote Explorer to connect to the EC2 on your local and develop using a vscode window instead of something like putty
and vim.
"""
import boto3
import json
import logging
import time
import os

log = logging.getLogger()

LAMBDA_FUNCTION_NAME = 'SparkFlowEC2Launcher'

# The PEM file is obviously not stored in git, you will have to grab this from AWS itself and manually put it in your dev env.
CURRENT_FILE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(CURRENT_FILE, '../../'))
PEM_FILE_PATH = os.path.join(REPO_ROOT, 'sparkflow.pem')
VS_CODE_SSH_CONFIG_PATH = os.path.expanduser('~\.ssh\config')

def call_lambda_function():
    """Launches the Lambda we use to instantiate the production environment."""
    lambda_client = boto3.client('lambda')
    response = lambda_client.invoke(
        FunctionName=LAMBDA_FUNCTION_NAME,
        InvocationType='RequestResponse'
    )

    if response['StatusCode'] == 200:
        payload_stream = response['Payload']
        payload = json.loads(payload_stream.read())
        return payload
    else:
        raise Exception(f"Failed to invoke Lambda function. Status code: {response['StatusCode']}")


def get_instance_ip(instance_id):
    ec2 = boto3.client('ec2')
    response = ec2.describe_instances(InstanceIds=[instance_id])
    reservations = response.get('Reservations')
    if reservations:
        instances = reservations[0].get('Instances')
        if instances:
            public_ip = instances[0].get('PublicIpAddress')
            return public_ip
    return None


def configure_ssh(ip, write_type):
    ssh_config_entry = [
        f'Host {ip}',
        f'HostName {ip}',
        f'IdentityFile {PEM_FILE_PATH}',
        'User ec2-user'
    ]

    with open(VS_CODE_SSH_CONFIG_PATH, write_type) as ssh_config:
        ssh_config.write('\n'.join(ssh_config_entry))

    print(f'SSH configuration for {ip} added to {VS_CODE_SSH_CONFIG_PATH}')


if __name__ == '__main__':
    """TODO: Once terraform is figured out, we should launch the terraform file to build the lambda from the current code iny
    the local environment, this will allow someone to test any infra changes.
    """
    ec2_instance_id = call_lambda_function()

    # Sometimes it takes a second for the EC2 to launch and generate the IP.  We want to retry after a few seconds if this is the case
    ip = get_instance_ip(ec2_instance_id)
    retries = 0
    while ip is None and retries < 1:
        time.sleep(5)
        ip = get_instance_ip(ec2_instance_id)
        retries += 1

    # I'm overwriting my SSH config file everytime.  I do this because I'm spinning up and tearing down EC2's relatively often.
    # You can instead use 'a' to append the new machine to your config file if so desired.
    configure_ssh(ip, write_type='w')
