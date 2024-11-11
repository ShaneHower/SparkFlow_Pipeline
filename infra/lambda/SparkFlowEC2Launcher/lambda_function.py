import boto3

AMI = "ami-0a699202e5027c10d"
INSTANCE_TYPE = "t2.large"
KEY_NAME = "SparkFlow"
REGION = "us-east-1"

ec2 = boto3.client('ec2', region_name=REGION)

block_device_mappings = [
    {
        'DeviceName': '/dev/xvda',
        'Ebs': {
            'VolumeSize': 20,  # Size in GB
            'VolumeType': 'gp2',  # General Purpose SSD
            'DeleteOnTermination': True
        }
    }
]

def lambda_handler(event, context):
    with open('init_instructions.txt', 'r') as file:
        init_script = file.read()

    print(init_script)

    instance = ec2.run_instances(
        ImageId=AMI,
        InstanceType=INSTANCE_TYPE,
        KeyName=KEY_NAME,
        MaxCount=1,
        MinCount=1,
        InstanceInitiatedShutdownBehavior='terminate',
        BlockDeviceMappings=block_device_mappings,
        UserData=init_script,
        IamInstanceProfile={
            'Name': 'EC2'
        }
    )

    instance_id = instance['Instances'][0]['InstanceId']
    print(f'INSATNCE ID: {instance_id}')

    return instance_id
