from email.message import EmailMessage
import json
import os
import smtplib

def execute(event, context):
    name = event["queryStringParameters"]["name"]
    email = event["queryStringParameters"]["email"]
    comments = event["queryStringParameters"]["comments"]
    
    from_address = os.environ["FROM_ADDRESS"]
    to_address = os.environ["TO_ADDRESS"]
    
    message = EmailMessage()
    message["From"] = from_address
    message["To"] = to_address
    message["Subject"] = "Feedback from alanbuttars.com"
    
    body = """
    Name: {}
    Email: {}
    Comments: {}
    """.format(name, email, comments)
    
    message.set_content(body)
    
    with smtplib.SMTP("email-smtp.us-west-2.amazonaws.com", port=587) as smtp_server:
        smtp_server.ehlo()
        smtp_server.starttls()
        smtp_server.ehlo()
        smtp_server.login(os.environ["SMTP_USERNAME"], os.environ["SMTP_PASSWORD"])
        smtp_server.send_message(message)
    
    # return { 
    #     "isBase64Encoded": False,
    #     "statusCode": 200,
    #     "headers": {
    #         "content-type": "application/json",
    #         "Access-Control-Allow-Origin": "*"
    #     },
    #     "body": {"status" : "OK" }
    # }

    
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body)
    }

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """
