terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"

  backend "s3" {
    bucket = "picklepokeyhouse"
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

resource "aws_lambda_function" "airflow_lambda" {
  function_name    = "airflow_launcher"
  role             = "arn:aws:iam::${var.aws_account}:role/SparkFlowLambdaRole"
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.9"
  s3_bucket        = "picklepokeyhouse"
  s3_key           = "spark_flow/lambda/code.zip"
  source_code_hash = filebase64sha256("lambda.zip")
}
