# calcul.py
import requests
import time
from collections import deque
import os

#API Key from environment variable
API_KEY = os.environ.get('API_KEY') # Assurez-vous de le garder secret dans un environnement de production

# Gérer la limite de fréquence des requêtes
last_requests = deque(maxlen=100)

def rate_limit():
    now = time.time()
    while last_requests and now - last_requests[0] < 120:
        if len(last_requests) >= 100:
            time.sleep(max(0, 120 - (now - last_requests[0])))
        break
    while last_requests and now - last_requests[-1] < 1:
        time.sleep(max(0, 1 - (now - last_requests[-1])))
    last_requests.append(time.time())

def safe_request(url):
    rate_limit()
    response = requests.get(url)
    if response.status_code == 429:
        retry_after = int(response.headers.get('Retry-After', 1))
        time.sleep(retry_after)
        return safe_request(url)
    return response

def get_puuid(region, user_name):
    name, tag = user_name.split('#')
    url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={API_KEY}"
    response = safe_request(url)
    if response.status_code == 200:
        return response.json().get('puuid')
    return None

def get_match_history(region, puuid):
    matches = []
    start = 0
    while True:
        url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start={start}&count=100&api_key={API_KEY}"
        response = safe_request(url)
        match_list = response.json()
        if not match_list:
            break
        matches.extend(match_list)
        start += 100
    return matches

def calculate_total_time(region, match_ids):
    total_time = 0
    for match_id in match_ids:
        url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={API_KEY}"
        response = safe_request(url)
        if response.status_code == 200:
            match_details = response.json()
            duration = match_details['info']['gameDuration']
            total_time += duration
    return total_time

# Vous pouvez supprimer la section 'Programme principal' car nous allons utiliser ces fonctions dans app.py
