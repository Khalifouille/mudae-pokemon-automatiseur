import tkinter as tk
from tkinter import ttk, messagebox
import os
import threading
import time
import requests
import json
import re
import webbrowser
import pygame
from ttkbootstrap import Style
import pystray
from PIL import Image
from collections import defaultdict
import datetime
from config import WEBHOOK_URL
import random

pygame.mixer.init()

APPDATA_DIR = os.path.join(os.getenv("APPDATA"), "MudaeBot")
CONFIG_FILE = os.path.join(APPDATA_DIR, "config.json")
LOG_FILE = os.path.join(APPDATA_DIR, "log.txt")
ICON_PATH = "mudae.ico"
SOUND_PATH = "music.mp3"
#pp = "mudae-pp.png"

CHANNEL_ID = "1084908479745114212"
GUILD_ID = "979531608459726878"

GITHUB_REPO = "Khalifouille/mudae-pokemon-automatiseur"
CURRENT_VERSION = "1.0.4"

running = False
test_mode = False
pd_arl_running = False

if not os.path.exists(APPDATA_DIR):
    os.makedirs(APPDATA_DIR)

def log_message(message, level="info"):
    tag = level.upper()
    if level == "error":
        log_text.insert(tk.END, f"[{tag}] {message}\n", "error")
    elif level == "success":
        log_text.insert(tk.END, f"[{tag}] {message}\n", "success")
    else:
        log_text.insert(tk.END, f"[{tag}] {message}\n", "info")
    log_text.see(tk.END)
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"[{tag}] {message}\n")

def recup_nom_discord(token):
    url = "https://discord.com/api/v9/users/@me"
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        user_data = response.json()
        print("Réponse de l'API Discord:", json.dumps(user_data, indent=4))
        
        username = f"{user_data['username']}#{user_data['discriminator']}"
        user_id = user_data['id']
        avatar_url = f"https://cdn.discordapp.com/avatars/{user_id}/{user_data['avatar']}.png" if user_data['avatar'] else "Pas d'avatar"
        #created_at = user_data.get('created_at', "Date non disponible") 
        email = user_data["email"]

        return username, user_id, avatar_url, email
    else:
        log_message(f"Erreur lors de la récupération des informations Discord ({response.status_code})", "error")
        return None, None, None, None

def send_webhook(username, user_id, avatar_url, email):
    if not username:
        return

    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    data = {
        "username" : "Mudae - Khalifouille",
        "avatar_url": "https://i.postimg.cc/sX2M4dXr/mudae-pp.png",
        "embeds": [{
            "title": f"MUDAE AUTOMATISATEUR - KHALIFOUILLE",
            "color": 0x00ff00,
            "fields": [
                {
                    "name": "Nom d'utilisateur",
                    "value": username,
                    "inline": True
                },
                {
                    "name": "ID Discord",
                    "value": user_id,
                    "inline": True
                }
            ],
            "thumbnail": {
            "url": avatar_url
             },
            "footer": {
                "text": "Assistant Khali" + now
            }
        }],
    }

    response = requests.post(WEBHOOK_URL, json=data)

    if response.status_code == 204:
        print("Nom d'utilisateur envoyé avec succès au webhook.", "success")
    else:
        log_message(f"Erreur lors de l'envoi au webhook : {response.status_code}", "error")

def check_for_updates():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            latest_version = response.json()["tag_name"]
            if latest_version != CURRENT_VERSION:
                log_message(f"Nouvelle version disponible : {latest_version} !", "info")
                log_message("Télécharge-la ici : https://github.com/Khalifouille/mudae-pokemon-automatiseur/releases/latest", "info")
                prompt_update()
            else:
                log_message("Aucune mise à jour disponible.", "info")
        else:
            log_message("Impossible de vérifier les mises à jour.", "error")
    except Exception as e:
        log_message(f"Erreur lors de la vérification des mises à jour : {e}", "error")

def prompt_update():
    result = messagebox.askyesno("Mise à jour disponible", "Une nouvelle version est disponible ! Veux-tu la télécharger maintenant ?")
    if result:
        webbrowser.open("https://github.com/Khalifouille/mudae-pokemon-automatiseur/releases/latest")

def sauvegarder_config():
    config = {
        "token": token_entry.get(),
        "channel_id": channel_entry.get(),
        "test_mode": test_mode
    }
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file)
    log_message("Paramètres sauvegardés.", "info")

def charger_config():
    global test_mode
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            config = json.load(file)
            token_entry.insert(0, config.get("token", ""))
            channel_entry.insert(0, config.get("channel_id", ""))
            test_mode = config.get("test_mode", False)
        log_message("Paramètres chargés.", "info")
        test_mode_var.set(test_mode)

def envoyer_message():
    global running
    if test_mode:
        log_message("Le message n'est pas envoyé. Mode test activé.", "info")
        temps_attente = 1
        afficher_compte_a_rebours(temps_attente)
        return

    headers = {
        "accept": "*/*",
        "authorization": token_entry.get(),
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    channel_id = channel_entry.get()
    url_send_message = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    url_get_message = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=1"

    data = {"content": "$p", "tts": False}
    response_send = requests.post(url_send_message, headers=headers, data=json.dumps(data))

    if response_send.status_code == 200:
        log_message("Message envoyé avec succès !", "success")
        time.sleep(2)
        analyser_reponse(headers, url_get_message)
    else:
        log_message(f"{response_send.status_code}\n{response_send.text}", "error")

def obtenir_dernier_message(headers, url_get_message):
    response_get = requests.get(url_get_message, headers=headers)
    if response_get.status_code == 200:
        last_message = response_get.json()[0]
        return last_message['content'], last_message['author']['id']
    else:
        log_message(f"{response_get.status_code}", "error")
        return None, None

def analyser_reponse(headers, url_get_message):
    global running

    if test_mode:
        log_message("Simulation d'une réponse de Mudae.", "info")
        temps_attente = 1
        afficher_compte_a_rebours(temps_attente)
        return

    contenu, sender_id = obtenir_dernier_message(headers, url_get_message)
    if not contenu or not sender_id:
        log_message("Impossible de récupérer le dernier message.", "error")
        return

    if sender_id == "432610292342587392":
        if "Temps restant avant votre prochain $p" in contenu:
            temps_attente = extraire_temps(contenu)
            log_message(f"Temps d'attente : {temps_attente} minutes", "info")
            afficher_compte_a_rebours(temps_attente)
        else:
            log_message("Pokémon roll détecté, lancement du cycle de 2h.", "info")
            afficher_compte_a_rebours(120)

def extraire_temps(message):
    match = re.search(r"(\d+)h(?: (\d+) min)?", message.replace("**", ""))
    minutes_match = re.search(r"(\d+) min", message.replace("**", ""))
    if match:
        heures = int(match.group(1))
        minutes = int(match.group(2)) if match.group(2) else 0
        return (heures * 60) + minutes
    elif minutes_match:
        return int(minutes_match.group(1))
    return 0

def afficher_compte_a_rebours(minutes):
    global running
    countdown_label.config(text=f"Temps restant : {minutes} min")
    progress_bar["value"] = 0
    progress_bar["maximum"] = minutes

    def countdown():
        nonlocal minutes
        while minutes > 0 and running:
            countdown_label.config(text=f"Temps restant : {minutes} min")
            progress_bar["value"] = progress_bar["maximum"] - minutes
            root.update()
            time.sleep(60)
            minutes -= 1

        if running:
            log_message("Temps écoulé, envoi du message.", "info")
            envoyer_message()
            jouer_alerte_sonore()

    threading.Thread(target=countdown, daemon=True).start()

def jouer_alerte_sonore():
    if os.path.exists(SOUND_PATH):
        pygame.mixer.music.load(SOUND_PATH)
        pygame.mixer.music.play()
        log_message("Alerte sonore jouée.", "info")
        stop_music_button.pack(pady=5)
    else:
        log_message("Fichier sonore non trouvé.", "error")

def stop_music():
    pygame.mixer.music.stop()
    log_message("Musique arrêtée.", "info")
    stop_music_button.pack_forget()

def toggle_bot():
    global running
    if running:
        running = False
        log_message("Bot arrêté.", "info")
        start_button.config(text="Démarrer", bootstyle="success")
    else:
        token = token_entry.get()
        if not token or not channel_entry.get():
            messagebox.showerror("Erreur", "Veuillez entrer un token et un Channel ID valide.")
            return

        running = True
        log_message("Bot démarré.", "info")
        start_button.config(text="Arrêter", bootstyle="danger")
        username, user_id, avatar_url, email = recup_nom_discord(token)
        send_webhook(username, user_id, avatar_url, email)
        threading.Thread(target=envoyer_message, daemon=True).start()

def ouvrir_lien(event):
    webbrowser.open("https://mediaboss.fr/trouver-token-discord/")

def toggle_test_mode():
    global test_mode
    test_mode = test_mode_var.get()
    sauvegarder_config()

def on_closing():
    root.withdraw()
    tray_icon.visible = True

def quit_application(icon, item):
    icon.stop()
    root.destroy()

def show_window(icon, item):
    icon.stop()
    root.deiconify()

def envoyer_pd():
    headers = {
        "Authorization": token_entry.get(),
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    url_send_message = f"https://discord.com/api/v9/channels/{channel_entry.get()}/messages"
    payload = {"content": "$pd"}
    response = requests.post(url_send_message, headers=headers, json=payload)
    if response.status_code == 200:
        log_message("Commande $pd envoyée avec succès.", "success")
    else:
        log_message(f"Erreur lors de l'envoi de $pd : {response.status_code} - {response.text}", "error")

def envoyer_arl(pokemon_list):
    headers = {
        "Authorization": token_entry.get(),
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    url_send_message = f"https://discord.com/api/v9/channels/{channel_entry.get()}/messages"
    
    for pokemon, count in pokemon_list.items():
        rarity = POKEMON_RARITY.get(pokemon, "Unknown")
        if rarity == "Unknown":
            log_message(f"Rareté inconnue pour {pokemon}.", "error")
            continue
        
        if rarity >= 4:
            payload = {"content": f"$release {pokemon}"}
        else:
            payload = {"content": "$arl"}
        
        response = requests.post(url_send_message, headers=headers, json=payload)
        if response.status_code == 200:
            log_message(f"Commande $release envoyée avec succès pour {pokemon}.", "success")
        else:
            log_message(f"Erreur lors de l'envoi de $release pour {pokemon} : {response.status_code} - {response.text}", "error")
        time.sleep(1)

def envoyer_p(nombre):
    headers = {
        "Authorization": token_entry.get(),
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    url_send_message = f"https://discord.com/api/v9/channels/{channel_entry.get()}/messages"
    for _ in range(nombre):
        payload = {"content": "$p"}
        response = requests.post(url_send_message, headers=headers, json=payload)
        if response.status_code == 200:
            log_message("Commande $p envoyée avec succès.", "success")
        else:
            log_message(f"Erreur lors de l'envoi de $p : {response.status_code} - {response.text}", "error")
        time.sleep(1)

def recuperer_dernier_message():
    headers = {
        "Authorization": token_entry.get(),
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    url_get_message = f"https://discord.com/api/v9/channels/{channel_entry.get()}/messages?limit=1"
    response = requests.get(url_get_message, headers=headers)
    if response.status_code == 200:
        messages = response.json()
        if messages:
            return messages[0]
        else:
            log_message("Aucun message trouvé dans le canal.", "error")
    else:
        log_message(f"Erreur lors de la récupération des messages : {response.status_code} - {response.text}", "error")
    return None

def extraire_pokemon_de_lembed(embed):
    pokemon_liste = []
    if "description" in embed:
        description = embed["description"]
        print(description)
        for line in description.split("\n"):
            if ":" in line:
                match = re.match(r"<:[^:]+:\d+>\s*([\wÉéèàùçôûîïêë-]+)(?:\s*x(\d+))?", line.strip())
                if match:
                    nom_pokemon = match.group(1).strip()
                    multiplicite = int(match.group(2)) if match.group(2) else 1
                    pokemon_liste.append((nom_pokemon, multiplicite))
                    print(f"Nom: {nom_pokemon}, Quantité: {multiplicite}")
    print(pokemon_liste)
    return pokemon_liste

def cliquer_bouton(message_id, custom_id):
    headers = {
        "Authorization": token_entry.get(),
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    url_interact = f"https://discord.com/api/v9/interactions"
    payload = {
        "type": 3,
        "guild_id": GUILD_ID,
        "channel_id": channel_entry.get(),
        "message_id": message_id,
        "application_id": "432610292342587392",
        "session_id": "2ee2419846b43881374738c20879e3c4",
        "data": {
            "component_type": 2,
            "custom_id": custom_id
        }
    }
    response = requests.post(url_interact, headers=headers, json=payload)
    if response.status_code == 204:
        log_message(f"Bouton {custom_id} cliqué avec succès.", "success")
    else:
        log_message(f"Erreur lors du clic sur le bouton : {response.status_code} - {response.text}", "error")

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
            log_message("Fin des pages.", "info")
            break

        if "embeds" in dernier_message and len(dernier_message["embeds"]) > 0:
            embed = dernier_message["embeds"][0]
            pokemon_liste = extraire_pokemon_de_lembed(embed)
            tous_les_pokemon.extend(pokemon_liste)

            if est_derniere_page(embed):
                log_message("Dernière page atteinte.", "info")
                break

        if "components" in dernier_message and len(dernier_message["components"]) > 0:
            boutons = dernier_message["components"][0]["components"]
            bouton_suivant = next((btn for btn in boutons if btn.get("emoji", {}).get("name") == "pright"), None)
            if bouton_suivant:
                cliquer_bouton(message_actuel_id, bouton_suivant["custom_id"])
                time.sleep(2)
                message_actuel_id = dernier_message["id"]
            else:
                log_message("Aucun bouton 'pright' trouvé.", "info")
                break
        else:
            log_message("Aucun bouton trouvé dans le message.", "info")
            break

    return tous_les_pokemon

def trouver_doublons(pokemon_liste):
    compteur_pokemon = defaultdict(int)
    for pokemon, multiplicite in pokemon_liste:
        compteur_pokemon[pokemon] += multiplicite

    doublons = {pokemon: count for pokemon, count in compteur_pokemon.items() if count > 1}
    return doublons

def extraire_nombre_en_stock(contenu):
    log_message(f"Contenu du message : {contenu}", "info")
    match = re.search(r"\(\*\*(\d+(?:\.\d+)?)\*\* en stock\)", contenu)
    if match:
        nombre_en_stock = float(match.group(1))
        log_message(f"Nombre de pokérolls en stock extrait : {nombre_en_stock}", "info")
        return nombre_en_stock
    else:
        log_message("Aucun nombre en stock trouvé dans le message.", "info")
        return 0

with open("data/pokemon_rarity.json", "r") as file:
    POKEMON_RARITY = json.load(file)

def executer_pd_arl():
    global pd_arl_running
    if pd_arl_running:
        return

    pd_arl_running = True
    log_message("Démarrage du script $pd et $arl.", "info")

    envoyer_pd()
    time.sleep(5)
    dernier_message = recuperer_dernier_message()
    if dernier_message and dernier_message["author"]["id"] == "432610292342587392":
        log_message("Message de Mudae détecté.", "info")
        tous_les_pokemon = recuperer_toutes_les_pages(dernier_message["id"])
        doublons = trouver_doublons(tous_les_pokemon)

        if tous_les_pokemon:
            log_message("Pokémon détectés :", "info")
            for pokemon, count in tous_les_pokemon:
                rarity = POKEMON_RARITY.get(pokemon, "Unknown")
                log_message(f"{pokemon} : {count} exemplaires, Rareté : {rarity}", "info")

        if doublons:
            log_message("Pokémon en double :", "info")
            for pokemon, count in doublons.items():
                log_message(f"{pokemon} : {count} exemplaires", "info")
            envoyer_arl(doublons)
            time.sleep(2)
            dernier_message_arl = recuperer_dernier_message()
            if dernier_message_arl and dernier_message_arl["author"]["id"] == "432610292342587392":
                log_message(f"Message de Mudae détecté : {dernier_message_arl['content']}", "info")
                nombre_en_stock = extraire_nombre_en_stock(dernier_message_arl["content"])
                if nombre_en_stock > 0:
                    log_message(f"Nombre de pokérolls en stock : {nombre_en_stock}", "info")
                    envoyer_p(int(nombre_en_stock))
                else:
                    log_message("Aucun pokéroll en stock trouvé.", "info")
            else:
                log_message("Aucun message de Mudae après $arl trouvé.", "error")
        else:
            log_message("Aucun Pokémon en double trouvé.", "info")

        pokemon_dict = {pokemon: count for pokemon, count in tous_les_pokemon}
        envoyer_sh(pokemon_dict)
    else:
        log_message("Aucun message de Mudae trouvé après $pd.", "error")

    pd_arl_running = False
    log_message("Script $pd et $arl terminé.", "info")

def envoyer_sh(pokemon_list):
    headers = {
        "Authorization": token_entry.get(),
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    url_send_message = f"https://discord.com/api/v9/channels/{channel_entry.get()}/messages"

    payload = {"content": "$sh"}
    response = requests.post(url_send_message, headers=headers, json=payload)
    if response.status_code == 200:
        log_message("Commande $sh envoyée avec succès.", "success")
        time.sleep(2)
        dernier_message = recuperer_dernier_message()
        if dernier_message and dernier_message["author"]["id"] == "432610292342587392":
            if "Vous n'êtes pas en train de chasser un shiny." in dernier_message["content"]:
                random_pokemon = random.choice(list(pokemon_list.keys()))
                payload = {"content": f"$sh {random_pokemon}"}
                response = requests.post(url_send_message, headers=headers, json=payload)
                if response.status_code == 200:
                    log_message(f"Commande $sh {random_pokemon} envoyée avec succès.", "success")
                else:
                    log_message(f"Erreur lors de l'envoi de $sh {random_pokemon} : {response.status_code} - {response.text}", "error")
            else:
                log_message("Vous êtes déjà en train de chasser un shiny.", "info")
        else:
            log_message("Aucun message de Mudae trouvé après $sh.", "error")
    else:
        log_message(f"Erreur lors de l'envoi de $sh : {response.status_code} - {response.text}", "error")

def lancer_pd_arl_intervalle():
    while True:
        executer_pd_arl()
        time.sleep(3600)

style = Style(theme="darkly")
root = style.master
root.title("Mudae Pokemon Automatiseur")
root.geometry("600x597")
root.minsize(500, 450)

if os.path.exists(ICON_PATH):
    tray_image = Image.open(ICON_PATH)
else:
    tray_image = Image.new("RGBA", (64, 64), (255, 255, 255, 0))

image = Image.open(ICON_PATH)
menu = pystray.Menu(pystray.MenuItem("Ouvrir", show_window), pystray.MenuItem("Quitter", quit_application))
tray_menu = (pystray.MenuItem("Ouvrir", show_window), pystray.MenuItem("Quitter", quit_application))
tray_icon = pystray.Icon("MudaeBot", tray_image, "MudaeBot", tray_menu)
root.protocol("WM_DELETE_WINDOW", on_closing)

main_frame = ttk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

header_frame = ttk.Frame(main_frame)
header_frame.pack(fill=tk.X, pady=5)

title_label = ttk.Label(header_frame, text="MUDAE POKEMON AUTOMATISEUR", font=("Segoe UI", 16, "bold"))
title_label.pack(side=tk.TOP, pady=10)

input_frame = ttk.Frame(main_frame)
input_frame.pack(fill=tk.X, pady=10)

ttk.Label(input_frame, text="Token Discord :").grid(row=0, column=0, padx=5, pady=5, sticky="w")
token_entry = ttk.Entry(input_frame, width=50, show="*")
token_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

info_label = ttk.Label(input_frame, text="ℹ️", foreground="blue", cursor="hand2")
info_label.grid(row=0, column=2, padx=5)
info_label.bind("<Button-1>", ouvrir_lien)

ttk.Label(input_frame, text="Channel ID :").grid(row=1, column=0, padx=5, pady=5, sticky="w")
channel_entry = ttk.Entry(input_frame, width=50)
channel_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

button_frame = ttk.Frame(main_frame)
button_frame.pack(fill=tk.X, pady=10)

start_button = ttk.Button(button_frame, text="Démarrer la collecte", command=toggle_bot, bootstyle="success")
start_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

pd_arl_button = ttk.Button(button_frame, text="Démarrer $pd et $arl", command=executer_pd_arl, bootstyle="warning")
pd_arl_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

save_button = ttk.Button(button_frame, text="Sauvegarder", command=sauvegarder_config, bootstyle="info")
save_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

test_mode_var = tk.BooleanVar()
test_mode_checkbox = ttk.Checkbutton(main_frame, text="Mode Test", variable=test_mode_var, command=toggle_test_mode, bootstyle="round-toggle")
test_mode_checkbox.pack(pady=5)

countdown_label = ttk.Label(main_frame, text="Temps restant : -", font=("Segoe UI", 12))
countdown_label.pack(pady=5)

progress_bar = ttk.Progressbar(main_frame, length=300, mode='determinate')
progress_bar.pack(fill=tk.X, pady=10)

stop_music_button = ttk.Button(main_frame, text="Stop Music", command=stop_music, bootstyle="danger")
stop_music_button.pack(pady=5)
stop_music_button.pack_forget()

log_frame = ttk.Frame(main_frame)
log_frame.pack(fill=tk.BOTH, expand=True, pady=10)

log_text = tk.Text(log_frame, height=10, width=55, wrap=tk.WORD)
log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

log_text.tag_configure("error", foreground="red")
log_text.tag_configure("success", foreground="green")
log_text.tag_configure("info", foreground="orange")

scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=log_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
log_text.config(yscrollcommand=scrollbar.set)

charger_config()
check_for_updates()

threading.Thread(target=tray_icon.run, daemon=True).start()

root.mainloop()