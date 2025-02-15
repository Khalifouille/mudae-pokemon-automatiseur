import requests
import time
import json

CHANNEL_ID = "1084908479745114212"  
GUILD_ID = "979531608459726878"  

headers = {
    "Authorization": USER_TOKEN,
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

SEND_MESSAGE_URL = f"https://discord.com/api/v9/channels/{CHANNEL_ID}/messages"
FETCH_MESSAGES_URL = f"https://discord.com/api/v9/channels/{CHANNEL_ID}/messages?limit=1"
INTERACT_URL = "https://discord.com/api/v9/interactions"

def send_pd():
    """Envoie la commande $pd dans le canal spécifié."""
    payload = {
        "content": "$pd"
    }
    response = requests.post(SEND_MESSAGE_URL, headers=headers, json=payload)
    if response.status_code == 200:
        print("Commande $pd envoyée avec succès.")
    else:
        print(f"Erreur lors de l'envoi de la commande : {response.status_code} - {response.text}")

def fetch_last_message():
    """Récupère le dernier message du canal."""
    response = requests.get(FETCH_MESSAGES_URL, headers=headers)
    if response.status_code == 200:
        messages = response.json()
        if messages:
            print("Message reçu :", json.dumps(messages[0], indent=4))
            return messages[0]  
        else:
            print("Aucun message trouvé dans le canal.")
    else:
        print(f"Erreur lors de la récupération des messages : {response.status_code} - {response.text}")
    return None

def extract_embed_content(message):
    """Extrait le contenu de l'embed du message."""
    if "embeds" in message and len(message["embeds"]) > 0:
        embed = message["embeds"][0]
        print("Contenu de l'embed :")
        print(f"Titre : {embed.get('title', 'Aucun titre')}")
        print(f"Description : {embed.get('description', 'Aucune description')}")
        if "fields" in embed:
            print("Champs :")
            for field in embed["fields"]:
                print(f"{field.get('name', 'Aucun nom')} : {field.get('value', 'Aucune valeur')}")
    else:
        print("Aucun embed trouvé dans le message.")

def click_button(message_id, custom_id):
    """Clique sur un bouton en utilisant son custom_id."""
    payload = {
        "type": 3,  
        "guild_id": GUILD_ID,
        "channel_id": CHANNEL_ID,
        "message_id": message_id,
        "application_id": "432610292342587392", 
        "session_id": "2ee2419846b43881374738c20879e3c4",  
        "data": {
            "component_type": 2,  
            "custom_id": custom_id
        }
    }
    response = requests.post(INTERACT_URL, headers=headers, json=payload)
    if response.status_code == 204:
        print(f"Bouton {custom_id} cliqué avec succès.")
    else:
        print(f"Erreur lors du clic sur le bouton : {response.status_code} - {response.text}")

def is_last_page(embed):
    """Vérifie si l'embed est sur la dernière page."""
    if "footer" in embed:
        footer_text = embed["footer"]["text"]
        if "Page" in footer_text:
            current_page = int(footer_text.split("Page")[1].split("/")[0].strip())  
            total_pages = int(footer_text.split("Page")[1].split("/")[1].strip())
            return current_page >= total_pages
    return False

def fetch_all_pages(message_id):
    """Récupère toutes les pages de l'embed en cliquant sur les boutons."""
    current_message_id = message_id
    while True:
        last_message = fetch_last_message()
        if not last_message or last_message["id"] != current_message_id:
            print("Fin des pages.")
            break

        extract_embed_content(last_message)

        if "embeds" in last_message and len(last_message["embeds"]) > 0:
            embed = last_message["embeds"][0]
            if is_last_page(embed):
                print("Dernière page atteinte.")
                break

        if "components" in last_message and len(last_message["components"]) > 0:
            buttons = last_message["components"][0]["components"]  
            next_button = next((btn for btn in buttons if btn.get("emoji", {}).get("name") == "pright"), None)
            if next_button:
                click_button(current_message_id, next_button["custom_id"])
                time.sleep(2)
                current_message_id = last_message["id"]
            else:
                print("Aucun bouton 'pright' trouvé.")
                break
        else:
            print("Aucun bouton trouvé dans le message.")
            break

def main():
    send_pd()
    print("Attente de la réponse de Mudae...")
    time.sleep(5) 
    last_message = fetch_last_message()
    if last_message:
        if last_message["author"]["id"] == "432610292342587392": 
            print("Message de Mudae détecté.")
            extract_embed_content(last_message)
            fetch_all_pages(last_message["id"])
        else:
            print("Le dernier message ne provient pas de Mudae.")
    else:
        print("Aucun message trouvé.")

if __name__ == "__main__":
    main()