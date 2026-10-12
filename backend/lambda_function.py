import boto3
import random
import json
import re

# DynamoDB connection
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("CloudFacts")

# Bedrock client
bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

# CORS is configured in API Gateway; these headers are a fallback
HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type"
}


def clean_text(text):
    # Remove markdown headings, bold/italic markers, and backticks
    text = re.sub(r"^#+\s*", "", text)
    text = text.replace("*", "").replace("`", "").replace("_", " ")
    # Replace fancy punctuation with plain equivalents
    text = (text.replace("\u2014", " - ")
                .replace("\u2013", "-")
                .replace("\u2018", "'").replace("\u2019", "'")
                .replace("\u201c", '"').replace("\u201d", '"'))
    # Remove emojis and any other non-ASCII characters
    text = text.encode("ascii", "ignore").decode("ascii")
    # Tidy up extra spaces and line breaks
    return re.sub(r"\s+", " ", text).strip()


def lambda_handler(event, context):
    response = table.scan()
    items = response.get("Items", [])
    if not items:
        return {
            "statusCode": 404,
            "headers": HEADERS,
            "body": json.dumps({"fact": "No facts available in DynamoDB."})
        }

    fact = random.choice(items)["FactText"]

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 150,
        "system": (
            "You rewrite cloud computing facts as short, witty sentences. "
            "Reply with plain text only. Never use markdown, headings, asterisks, "
            "emojis, or special symbols. Return only the rewritten fact."
        ),
        "messages": [
            {
                "role": "user",
                "content": f"Make this fact fun and engaging in 1-2 sentences maximum: {fact}"
            }
        ],
        "temperature": 0.7
    }

    try:
        resp = bedrock.invoke_model(
            modelId="us.anthropic.claude-haiku-4-5-20251001-v1:0",
            body=json.dumps(body),
            accept="application/json",
            contentType="application/json"
        )

        result = json.loads(resp["body"].read())
        witty_fact = ""

        for block in result.get("content", []):
            if block.get("type") == "text":
                witty_fact = clean_text(block["text"])
                break

        if not witty_fact or len(witty_fact) > 300:
            witty_fact = fact

    except Exception as e:
        print(f"Bedrock error: {e}")
        witty_fact = fact

    return {
        "statusCode": 200,
        "headers": HEADERS,
        "body": json.dumps({"fact": witty_fact})
    }