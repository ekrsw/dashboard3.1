import pymsteams

import settings

def send_message() -> None:
    incoming_webhook_url = settings.WEBHOOK_URL
    title = settings.TITLE
    message = settings.MESSAGE

    teams_obj = pymsteams.connectorcard(incoming_webhook_url)
    teams_obj.title(title)
    teams_obj.text(message)
    teams_obj.send()
    print("Done")

def send_message_test() -> None:
    import requests
    import json

    webhook_url = settings.WEBHOOK_URL
    user_id = settings.USER_ID
    user_name = settings.USER_NAME

    message = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "text": f"{settings.MESSAGE} <at>{user_name}</at>",
        "entities": [{
            "type": "mention",
            "text": f"<at>{user_name}</at>",
            "mentioned": {
                "id": user_id,
                "name": user_name
            }
        }]
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(webhook_url, headers=headers, data=json.dumps(message))
    print(response.status_code)
