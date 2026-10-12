AWS Cloud Fun Facts Generator:

A serverless web app that serves witty cloud computing facts. A static frontend hosted on AWS Amplify calls an API Gateway endpoint, which triggers a Python Lambda function. The function reads a random fact from DynamoDB and uses Claude Haiku 4.5 on Amazon Bedrock to rewrite it as a short, fun and witty sentence.

## Services used

| Service | Purpose |
| --- | --- |
| AWS Amplify | Hosts the static frontend |
| Amazon API Gateway (HTTP API) | Exposes the `/funfact` endpoint, with CORS enabled |
| AWS Lambda (Python) | Backend logic |
| Amazon DynamoDB | Stores the cloud facts |
| Amazon Bedrock (Claude Haiku 4.5) | Rewrites each fact to be witty |
| AWS IAM | Gives Lambda permission to read DynamoDB and invoke Bedrock |

Request flow:

-The user opens the Amplify-hosted page and clicks Generate Fun Fact.
-The page calls GET /funfact on API Gateway.
-API Gateway triggers the Lambda function.
-Lambda scans the CloudFacts table and picks a random fact.
-Lambda sends the fact to Claude Haiku 4.5 on Bedrock and asks for a short, witty rewrite in plain text.
-The rewritten fact is returned to the browser. If Bedrock fails, the original fact is returned instead.

