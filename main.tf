data "template_file" "iam_assume_role_lambda" {
  template = "${file("policies/iam_assume_role.json")}"

  vars {
    aws_service = "lambda"
  }
}

data "template_file" "daycare_lambda_policy" {
  template = "${file("./policies/daycare_lambda.json")}"
}

resource "aws_cloudwatch_event_rule" "daycare_lambda" {
  name        = "daycare_events"
  description = "Cron for lambda"

  schedule_expression = "rate(15 minutes)" 
}

resource "aws_lambda_permission" "daycare_lambda" {
  statement_id  = "daycare-lambda-trigger"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.daycare_lambda.function_name}"
  principal     = "events.amazonaws.com"
  source_arn    = "${aws_cloudwatch_event_rule.daycare_lambda.arn}"
}

resource "aws_cloudwatch_event_target" "daycare_to_lambda" {
  rule = "${aws_cloudwatch_event_rule.daycare_lambda.name}"
  arn  = "${aws_lambda_function.daycare_lambda.arn}"
}

resource "aws_kms_key" "daycare_lambda_kms_key" {
  description = "Encryption key for daycare slack lambda configuration"

  tags {
    "Name"        = "daycare-slack-lambda-${var.env}"
    "Contact"     = "${var.contact}"
    "Service"     = "${var.service}"
    "Description" = "Managed via Terraform"
    "Environment" = "${var.env}"
  }
}

resource "aws_lambda_function" "daycare_lambda" {
  filename         = "./build/lambda.zip"
  function_name    = "daycare_lambda"
  description      = "Updates the daycares"
  runtime          = "python3.7"
  role             = "${aws_iam_role.daycare_lambda_role.arn}"
  handler          = "daycare.lambda_handler"
  source_code_hash = "${base64sha256(file("./build/lambda.zip"))}"
  memory_size      = 128
  timeout          = 150

  tags {
    "Contact"     = "${var.contact}"
    "Service"     = "${var.service}"
    "Description" = "Managed via Terraform"
    "Environment" = "${var.env}"
  }
}

resource "aws_iam_role_policy_attachment" "daycare_lambda_policy_att" {
  role       = "${aws_iam_role.daycare_lambda_role.name}"
  policy_arn = "${aws_iam_policy.daycare_lambda_policy.arn}"
}

resource "aws_iam_role_policy_attachment" "daycare_lambda_policy_att_basic" {
  role       = "${aws_iam_role.daycare_lambda_role.name}"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_policy" "daycare_lambda_policy" {
  name        = "daycare_lambda_policy"
  description = "Grants access to describe instances"
  policy      = "${data.template_file.daycare_lambda_policy.rendered}"
}

resource "aws_iam_role" "daycare_lambda_role" {
  name               = "daycare_lambda_role"
  assume_role_policy = "${data.template_file.iam_assume_role_lambda.rendered}"
}
