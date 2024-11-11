import argparse
import boto3
import os
import zipfile
from pathlib import Path
from botocore.exceptions import NoCredentialsError


BUCKET = 'picklepokeyhouse'

def zip_folder(location: Path):
    # Grab the zip name.  We are just saving to the location we are running in since it is temporary a VM
    zip_name = str(location).split(os.sep)[-1]

    # We want to write the zips to the terraform directory.  This allows us to track the lambda code changes with terraform
    # so that it can refresh the lambda code when needed.
    repo_path = Path(__file__).resolve().parents[1]
    terraform_path = repo_path / 'terraform'
    output_zip = str(terraform_path / f'{zip_name}.zip')

    # Execute the zip
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(location):
            for file in files:
                file_path = os.path.join(root, file)
                # Preserve the folder structure by adding relative paths
                arcname = os.path.relpath(file_path, start=location)
                zipf.write(file_path, arcname)

    return output_zip


def send_file_to_s3(file_loc: Path, bucket: str, key: str):

    s3_client = boto3.client('s3')

    try:
        s3_client.upload_file(str(file_loc), bucket, key)
        print(f"File '{file_loc}' uploaded to '{bucket}/{key}'")
    except FileNotFoundError as e:
        print(f"The file '{file_loc}' was not found")
        raise e
    except NoCredentialsError as e:
        print("Credentials not available")
        raise e
    except Exception as e:
        raise e


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process either --lambda or --spark_flow argument.")

    # Adding mutually exclusive arguments
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--lambda', action='store_true', help="Run Lambda Deploy.")
    group.add_argument('--sparkflow', action='store_true', help="Run Spark Flow Deploy.")

    args = parser.parse_args()
    args_dict = vars(args)

    if args_dict.get('lambda'):
        # Running inside of infra so we can simply call the lambda folder
        folder = 'lambda'
        key = 'spark_flow/lambda/code.zip'
    elif args_dict.get('sparkflow'):
        # Running inside of infra so we have to navigate out of it.
        repo_path = Path(__file__).resolve().parents[1]
        folder = repo_path / 'sparkflow'
        key = 'spark_flow/core/code.zip'

    # Send to S3
    output_zip = zip_folder(location=Path(folder))
    send_file_to_s3(file_loc=output_zip, bucket=BUCKET, key=key)
