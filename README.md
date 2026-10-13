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

**Setup**
1) **DynamoDB**: create a table named CloudFacts with partition key FactID (String). Use on-demand capacity.
2) **Load the data**:

   aws dynamodb batch-write-item --request-items file://data/data.json
   
3)**Bedrock**: In the Bedrock console (us-east-1), open the model catalog, select Claude Haiku 4.5, and submit the use case details if prompted. Confirm it works in the playground.

4) **Lambda:** Create a Python function, paste `backend/lambda_function.py`, and set the timeout to 15-30 seconds. Attach these managed IAM policies to the function's execution role:
   - `AWSLambdaBasicExecutionRole` (lets Lambda write logs to CloudWatch)
   
   - `AmazonDynamoDBReadOnlyAccess` (lets Lambda read facts from the `CloudFacts` table)
   
   - `AmazonBedrockFullAccess` (lets Lambda invoke Claude Haiku 4.5 on Bedrock)
   
> Note: These managed policies keep the setup simple for learning. In production, replace them with a custom policy that allows only `dynamodb:Scan` 
on the `CloudFacts` table and `bedrock:InvokeModel` on the specific model.

5) **API Gateway:** Create an HTTP API with a GET /funfact route integrated with the Lambda function.

6)**Frontend:** In frontend/index.html, replace YOUR_API_GATEWAY_URL with your API invoke URL (for example https://abc123.execute-api.us-east-1.amazonaws.com). Zip index.html and deploy it to Amplify using "Deploy without Git provider".

7)**CORS:** In API Gateway, add your Amplify URL as an allowed origin, with methods GET and OPTIONS and header content-type.

**Cost control**
-Uses Claude Haiku 4.5, the lowest-cost Claude model, which is enough for rewriting a short fact.

-Output is capped with max_tokens (150), so each response has a limit on its cost.

-Bedrock is billed per token, so each request costs a tiny fraction of a cent.


**What I learned**
-Designing a serverless architecture with Amplify, API Gateway, Lambda, DynamoDB, and Bedrock

-Configuring IAM permissions so Lambda can read DynamoDB and invoke Bedrock

-Enabling CORS in API Gateway for a cross-origin frontend

-Writing prompts and output handling to get clean plain-text responses from a model

-Choosing a low-cost model and setting token limits to keep spending down
