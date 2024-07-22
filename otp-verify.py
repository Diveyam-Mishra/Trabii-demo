from azure.communication.email import EmailClient
def main():
    try:
        connection_string =""
        client = EmailClient.from_connection_string(connection_string)

        message = {
            "senderAddress": "",
            "recipients":  {
                "to": [{"address": "mishradiveyam@gmail.com" }],
            },
            "content": {
                "subject": "Test Email",
                "plainText": "Hello world via email.",
            }
        }

        poller = client.begin_send(message)
        result = poller.result()

    except Exception as ex:
        print(ex)
main()
