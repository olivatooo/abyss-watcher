### Step 1: Enable CloudTrail

First, you need to create a CloudTrail if it doesn't exist already.

```bash
aws cloudtrail create-trail \
    --name my-cloudtrail \
    --s3-bucket-name my-cloudtrail-bucket \
    --is-multi-region-trail
```

To start logging events with the trail:

```bash
aws cloudtrail start-logging --name my-cloudtrail
```

### Step 2: Create an EventBridge Rule

Now, you'll create an EventBridge rule that triggers the Lambda function when specific API calls are detected.

First, create a file named `event_pattern.json` with the following content:

```json
{
  "source": ["aws.ec2", "aws.s3", "aws.rds", "aws.lambda"],
  "detail-type": ["AWS API Call via CloudTrail"],
  "detail": {
    "eventName": [
      "CreateBucket",
      "RunInstances",
      "CreateFunction",
      "CreateDBInstance"
    ]
  }
}
```

Then, use the following command to create the EventBridge rule:

```bash
aws events put-rule \
    --name my-resource-creation-rule \
    --event-pattern file://event_pattern.json \
    --description "Triggers Lambda when a new resource is created"
```

### Step 3: Create the Lambda Function

You need to create an IAM role for the Lambda function with the necessary permissions.

Create a role trust policy file named `trust-policy.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

Create the IAM role:

```bash
aws iam create-role \
    --role-name my-lambda-role \
    --assume-role-policy-document file://trust-policy.json
```

Attach the AWS managed policy `AWSLambdaBasicExecutionRole` to the role:

```bash
aws iam attach-role-policy \
    --role-name my-lambda-role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

Next, create the Lambda function. First, write your Lambda function code in a file named `lambda_function.py`:

```python
def lambda_handler(event, context):
    print("Event received: ", event)
    # Add your processing logic here
```

Zip the function code:

```bash
zip function.zip lambda_function.py
```

Now create the Lambda function:

```bash
aws lambda create-function \
    --function-name my-resource-lambda \
    --runtime python3.9 \
    --role arn:aws:iam::<YOUR_ACCOUNT_ID>:role/my-lambda-role \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://function.zip
```

### Step 4: Add the EventBridge Rule as a Trigger to the Lambda Function

Finally, add the EventBridge rule as a trigger to the Lambda function:

```bash
aws lambda add-permission \
    --function-name my-resource-lambda \
    --statement-id my-eventbridge-trigger \
    --action 'lambda:InvokeFunction' \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:<YOUR_REGION>:<YOUR_ACCOUNT_ID>:rule/my-resource-creation-rule
```

Now, attach the rule to the Lambda function:

```bash
aws events put-targets \
    --rule my-resource-creation-rule \
    --targets "Id"="1","Arn"="arn:aws:lambda:<YOUR_REGION>:<YOUR_ACCOUNT_ID>:function:my-resource-lambda"
```

### Step 5: Verify the Setup

To verify that everything is set up correctly:

1. **Create a test resource** (e.g., an S3 bucket):

   ```bash
   aws s3 mb s3://my-test-bucket
   ```

2. **Check CloudWatch Logs** for the Lambda function to see if it was triggered:

   ```bash
   aws logs describe-log-streams --log-group-name /aws/lambda/my-resource-lambda
   ```

   ```bash
   aws logs get-log-events --log-group-name /aws/lambda/my-resource-lambda --log-stream-name <LOG_STREAM_NAME>
   ```

Replace `<YOUR_ACCOUNT_ID>` and `<YOUR_REGION>` with your actual AWS Account ID and region. With these commands, you should be able to set up the entire process using AWS CLI v2.
