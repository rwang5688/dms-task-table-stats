module "lambda_python" {
  source            = "../terraform-aws-lambda-python/"

  aws_profile       = "default"
  aws_region        = "us-west-2"

  pip_path          = "pip"

  lambda_name       = "get-dms-task-table-stats"
  lambda_iam_name   = "get-dms-task-table-stats-iam"

#  lambda_api_name   = "get-dms-task-table-stats-api"
#  api_stage_name    = "dev"
#  api_resource_path = "demo"
#  api_http_method   = "POST"
}
