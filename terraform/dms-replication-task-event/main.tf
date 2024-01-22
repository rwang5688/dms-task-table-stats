module "lambda_python" {
  source            = "../terraform-aws-lambda-python/"

  aws_profile       = "default"
  aws_region        = "us-west-2"

  pip_path          = "pip"

  lambda_name       = "dms-replication-task-event"
  lambda_iam_name   = "dms-replication-task-event-iam"

#  lambda_api_name   = "dms-replication-task-event-api"
#  api_stage_name    = "dev"
#  api_resource_path = "demo"
#  api_http_method   = "POST"
}
