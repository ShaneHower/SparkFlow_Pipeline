terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"

  backend "s3" {
    bucket = var.s3_bucket
    key    = "terraform/spark_flow/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = "us-east-1"
}

variable "aws_account" {
  description = "The AWS account id where we are deploying"
  type        = string
}

variable "s3_bucket" {
  description = "The S3 bucket containing the Lambda deployment package"
  type        = string
}

resource "aws_lambda_function" "airflow_lambda" {
  function_name = "airflow_launcher"
  role = "arn:aws:iam::${var.aws_account}:role/EC2"
  handler = "lambda_function.lambda_handler"
  runtime = "python3.12"
  s3_bucket = var.s3_bucket
  s3_key = "spark_flow/lambda/code.zip"
}
