import json
import email
from email import policy
from email.parser import BytesParser
import boto3

def lambda_handler(event, context):
    # 1. Extract the SNS message
    sns_message = event['Records'][0]['Sns']['Message']
    
    # 2. Parse the SNS message JSON string to a dictionary
    message_json = json.loads(sns_message)
    
    # 3. Get the raw email content
    raw_email = message_json.get('content', '')
    
    
    # 4. Parse the raw email content using the email module
    # The raw email content might contain escaped characters, so we need to decode it properly
    raw_email_bytes = raw_email.encode('utf-8')
    email_message = BytesParser(policy=policy.default).parsebytes(raw_email_bytes)
    
    # 5. Extract email headers
    subject = email_message['Subject']
    from_address = email_message['From']
    to_address = email_message['To']
    date = email_message['Date']
    
    # Print email headers
    print(f"Subject: {subject}")
    print(f"From: {from_address}")
    print(f"To: {to_address}")
    print(f"Date: {date}")
    
    # 6. Extract the email body
    if email_message.is_multipart():
        # If multipart, get the payload from the text/plain part
        for part in email_message.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get_content_disposition())
            
            # Ignore attachments
            if content_type == 'text/plain' and 'attachment' not in content_disposition:
                email_body = part.get_content()
                break
    else:
        # Not multipart - get the payload directly
        email_body = email_message.get_content()
    
    # Print the email body
    print("Email body:")
    print(email_body)
    
    # 7. Prepare the message to send to SNS
    sns_message_content = f"""
    Subject: {subject}
    From: {from_address}
    To: {to_address}
    Date: {date}
    
    {email_body}
    """
    
    # 8. Publish the message to SNS
    sns_client = boto3.client('sns')
    topic_arn = 'SET THE TOPIC ARN THERE'
    
    response = sns_client.publish(
        TopicArn=topic_arn,
        Message=sns_message_content,
        Subject=subject  # Note: Subject may not be used in email subscriptions
    )
    
    # Optionally, print the response for debugging
    print("SNS publish response:", response)
    
    # Optionally, return some info
    return {
        'statusCode': 200,
        'body': json.dumps('Email content extracted and sent to SNS!')
    }
