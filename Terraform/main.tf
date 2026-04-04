# terraform settings
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.39.0"
    }
  }
}

# provider
provider "aws" {
  region = "ap-south-1"
}

# resources
resource "aws_s3_bucket" "f1ow_bucket" {
  bucket = "f1ow-data-417521971713"

  tags = {
    Name        = "f1ow-data"
    Environment = "Dev"
  }
}