import requests
import json

channel_id = "1084908479745114212"
url_send_message = f"https://discord.com/api/v9/channels/{channel_id}/messages"
url_get_message = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=1"

headers = {
    "accept": "*/*",
    "accept-language": "fr,fr-CH;q=0.9",
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9181 Chrome/128.0.6613.186 Electron/32.2.7 Safari/537.36"
}

data = {
    "content": "$p",  
    "tts": False
}


response_send = requests.post(url_send_message, headers=headers, data=json.dumps(data))

if response_send.status_code == 200:
    print("Message envoyé avec succès !")

    response_get = requests.get(url_get_message, headers=headers)
    
    if response_get.status_code == 200:
        last_message = response_get.json()[0]  
        print("--------------------")
        print(f"Content: {last_message['content']}")
        sender_id = last_message['author']['id']
        print(f"Envoyeur : {sender_id}")
    else:
        print(f"Erreur lors de la récupération du message : {response_get.status_code}")
else:
    print(f"Erreur lors de l'envoi du message : {response_send.status_code}")
    print(response_send.text)
