import requests
import time
import json
from collections import defaultdict

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

def envoyer_pd():
    payload = {
        "content": "$pd"
    }
    response = requests.post(SEND_MESSAGE_URL, headers=headers, json=payload)
    if response.status_code == 200:
        print("Commande $pd envoyée avec succès.")
    else:
        print(f"Erreur lors de l'envoi de la commande : {response.status_code} - {response.text}")

def envoyer_arl():
    payload = {
        "content": "$arl"
    }
    response = requests.post(SEND_MESSAGE_URL, headers=headers, json=payload)
    if response.status_code == 200:
        print("Commande $arl envoyée avec succès.")
    else:
        print(f"Erreur lors de l'envoi de la commande : {response.status_code} - {response.text}")

def recuperer_dernier_message():
    response = requests.get(FETCH_MESSAGES_URL, headers=headers)
    if response.status_code == 200:
        messages = response.json()
        if messages:
            return messages[0]
        else:
            print("Aucun message trouvé dans le canal.")
    else:
        print(f"Erreur lors de la récupération des messages : {response.status_code} - {response.text}")
    return None

def extraire_pokemon_de_lembed(embed):
    pokemon_liste = []
    if "description" in embed:
        description = embed["description"]
        pokemon_liste = [line.split(">")[1].strip() for line in description.split("\n") if ">" in line]
    return pokemon_liste

def cliquer_bouton(message_id, custom_id):
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

def est_derniere_page(embed):
    if "footer" in embed:
        footer_text = embed["footer"]["text"]
        if "Page" in footer_text:
            page_actuelle = int(footer_text.split("Page")[1].split("/")[0].strip())
            pages_totales = int(footer_text.split("Page")[1].split("/")[1].strip())
            return page_actuelle >= pages_totales
    return False

def recuperer_toutes_les_pages(message_id):
    message_actuel_id = message_id
    tous_les_pokemon = []
    while True:
        dernier_message = recuperer_dernier_message()
        if not dernier_message or dernier_message["id"] != message_actuel_id:
            print("Fin des pages.")
            break

        if "embeds" in dernier_message and len(dernier_message["embeds"]) > 0:
            embed = dernier_message["embeds"][0]
            pokemon_liste = extraire_pokemon_de_lembed(embed)
            tous_les_pokemon.extend(pokemon_liste)

            if est_derniere_page(embed):
                print("Dernière page atteinte.")
                break

        if "components" in dernier_message and len(dernier_message["components"]) > 0:
            boutons = dernier_message["components"][0]["components"]
            bouton_suivant = next((btn for btn in boutons if btn.get("emoji", {}).get("name") == "pright"), None)
            if bouton_suivant:
                cliquer_bouton(message_actuel_id, bouton_suivant["custom_id"])
                time.sleep(2)
                message_actuel_id = dernier_message["id"]
            else:
                print("Aucun bouton 'pright' trouvé.")
                break
        else:
            print("Aucun bouton trouvé dans le message.")
            break

    return tous_les_pokemon

def trouver_doublons(pokemon_liste):
    compteur_pokemon = defaultdict(int)
    for pokemon in pokemon_liste:
        compteur_pokemon[pokemon] += 1

    doublons = {pokemon: count for pokemon, count in compteur_pokemon.items() if count > 1}
    return doublons

def main():
    envoyer_pd()
    print("Attente de la réponse de Mudae...")
    time.sleep(5)
    dernier_message = recuperer_dernier_message()
    if dernier_message:
        if dernier_message["author"]["id"] == "432610292342587392":
            print("Message de Mudae détecté.")
            tous_les_pokemon = recuperer_toutes_les_pages(dernier_message["id"])
            doublons = trouver_doublons(tous_les_pokemon)

            if doublons:
                print("\nPokémon en double :")
                for pokemon, count in doublons.items():
                    print(f"{pokemon} : {count} exemplaires")
                envoyer_arl()
            else:
                print("Aucun Pokémon en double trouvé.")
        else:
            print("Le dernier message ne provient pas de Mudae.")
    else:
        print("Aucun message trouvé.")

if __name__ == "__main__":
    main()