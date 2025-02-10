import requests
import json
import re
import time
from datetime import datetime

id_canal = "1084908479745114212"
url_envoi_message = f"https://discord.com/api/v9/channels/{id_canal}/messages"
url_recup_message = f"https://discord.com/api/v9/channels/{id_canal}/messages?limit=1"

entetes = {
    "accept": "*/*",
    "accept-language": "fr,fr-CH;q=0.9",
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9181 Chrome/128.0.6613.186 Electron/32.2.7 Safari/537.36"
}

donnees = {
    "content": "$p",  
    "tts": False
}

def extraire_temps(texte):
    heures = 0
    minutes = 0

    match_heures = re.search(r"(\d+)h", texte.replace("**", ""))
    match_minutes = re.search(r"(\d+) min", texte.replace("**", ""))

    if match_heures:
        heures = int(match_heures.group(1))
    if match_minutes:
        minutes = int(match_minutes.group(1))

    return (heures * 60) + minutes  

def envoyer_message():
    reponse_envoi = requests.post(url_envoi_message, headers=entetes, data=json.dumps(donnees))

    if reponse_envoi.status_code == 200:
        print("\033[92m[SUCCESS] Message envoyé avec succès !\033[0m")

        reponse_recup = requests.get(url_recup_message, headers=entetes)
        
        if reponse_recup.status_code == 200:
            dernier_message = reponse_recup.json()[0]
            print("--------------------")
            print(f"Contenu: {dernier_message['content']}")
            id_envoyeur = dernier_message['author']['id']
            print(f"Envoyeur : {id_envoyeur}")
            
            if id_envoyeur == "432610292342587392":
                temps_restant = extraire_temps(dernier_message['content'])
                if temps_restant > 0:
                    print(f"Temps restant avant le prochain message: {temps_restant} minutes")
                    attendre_temps_restant(temps_restant)
                else:
                    print("\033[91m[ERROR] Temps restant incorrect ou non trouvé.\033[0m")
            else:
                print(f"L'envoyeur n'est pas correct (ID: {id_envoyeur}).")
        else:
            print(f"\033[91m[ERROR] Erreur lors de la récupération du message : {reponse_recup.status_code}\033[0m")
    else:
        print(f"\033[91m[ERROR] Erreur lors de l'envoi du message : {reponse_envoi.status_code}\033[0m")
        print(reponse_envoi.text)

def attendre_temps_restant(temps_restant):
    print(f"Attente pendant {temps_restant} minutes...")
    time.sleep(temps_restant * 60)
    print("Temps écoulé, envoi du message.")
    envoyer_message()

def envoyer_messages_reguliers():
    while True:
        heure_actuelle = datetime.now()

        if heure_actuelle.hour % 2 == 1 or heure_actuelle.minute == 0:
            envoyer_message()
        
        temps_attente = (60 - heure_actuelle.minute) * 60
        print(f"Attente jusqu'à la prochaine heure ({temps_attente} secondes)...")
        time.sleep(temps_attente)

envoyer_message()
envoyer_messages_reguliers()
