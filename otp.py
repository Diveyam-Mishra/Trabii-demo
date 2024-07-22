from azure.communication.email import EmailClient
import random
import asyncio
from config import *
email_client = EmailClient.from_connection_string(connstring)

def send_otp_email(recipient_email, otp_code):
    message = {
        "senderAddress": senderMailAddress,
        "recipients": {
            "to": [{"address": recipient_email}],
        },
        "content": {
            "subject": "Your OTP Code",
            "plainText": f"Your OTP code is {otp_code}.",
        }
    }

    poller = email_client.begin_send(message)
    result = poller.result()
    return result
