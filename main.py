import requests
import json
import schedule
import time
import re
from datetime import datetime

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

def send_message():
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
            if sender_id == "432610292342587392":
                match = re.search(r"(\d+) min", last_message['content'])
                if match:
                    time_left = int(match.group(1))
                    print(f"Temps restant avant le prochain message: {time_left} minutes")
                    time.sleep(time_left * 60)
                    send_message()  
            else:
                print("L'envoyeur n'est pas correct. Démarrage de la planification.")
                start_scheduled_messages()

        else:
            print(f"Erreur lors de la récupération du message : {response_get.status_code}")
    else:
        print(f"Erreur lors de l'envoi du message : {response_send.status_code}")
        print(response_send.text)

def heure_impaire():
    current_hour = datetime.now().hour
    return current_hour % 2 != 0

def start_scheduled_messages():
    schedule.every(2).hours.do(send_message)
    schedule.every().hour.at(":00").do(lambda: send_message() if heure_impaire() else None)
    while True:
        schedule.run_pending()
        time.sleep(60)  

send_message()
