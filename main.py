import os
import requests
import psycopg
from dotenv import load_dotenv


load_dotenv()
API_KEY = os.getenv("FOOTBALL_API_KEY")
BASE_URL = "https://api.football-data.org/v4"
headers = {"X-Auth-Token": API_KEY}

if (not os.getenv("DATABASE_URL") or not os.getenv("FOOTBALL_API_KEY")):
    print("Missing DATABASE_URL or FOOTBALL_API_KEY")
    exit()

conn = psycopg.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()


leagues = {
    'FIFA World Cup' : 'WC',
    'UEFA Champions League' : 'CL',
    'Bundesliga' : 'BL1',
    'Eredivisie' : 'DED',
    'Campeonato Brasileiro Série A' : 'BSA',
    'La Liga' : 'PD',
    'Ligue 1' : 'FL1',
    'Championship' : 'ELC',
    'Primeira Liga' : 'PPL',
    'European Championship' : 'EC',
    'Serie A' : 'SA',
    'Premier League' : 'PL'
}

def get_player_db(name):
    result = cur.execute(""" SELECT * 
                         FROM players 
                         WHERE LOWER(name) = %s""", (name.lower(), ))
    return result.fetchone()

def add_player_to_db(player):
    cur.execute ( """ INSERT INTO players (
                  api_player_id, 
                  name, 
                  nationality, 
                  date_of_birth, 
                  shirt_number, 
                  position, 
                  team_name, 
                  team_crest) 
                  
                  VALUES 
                  (%s, 
                  %s, 
                  %s, 
                  %s, 
                  %s,   
                  %s, 
                  %s, 
                  %s)
                  """, (player['api_player_id'], 
                        player['name'], 
                        player['nationality'],
                        player['date_of_birth'],
                        player['shirt_number'],
                        player['position'],
                        player['team_name'],
                        player['team_crest'])
    )
    conn.commit()


def get_league_data(league_name):
    league_code = leagues[league_name]
    response = requests.get(f"{BASE_URL}/competitions/{league_code}/teams", headers=headers)
    if(response.status_code != 200):
        print("Something went wrong")
        return None
    return response.json()

def get_player_api(league, player_name):
    # leauge['teams'] because leauge is a dictionary, we have to look at the 'teams' key
    for team in league['teams']:
        # team['squad'] because the key 'squad' contains the players information
        for player in team['squad']:
            if player['name'].lower() == player_name.lower():
                player_id = player['id']
                # API request to find player
                player_data = requests.get(f'{BASE_URL}/persons/{player_id}', headers=headers)
                if(player_data.status_code != 200):
                    print("Something went wrong")
                    return None
                return player_data.json()

def clean_up_data(player_data):
    # only get the data I want from API request
    player = {
        'api_player_id' : player_data['id'],
        'name' : player_data['name'],
        'nationality' : player_data['nationality'],
        'date_of_birth' : player_data['dateOfBirth'],
        'shirt_number' : player_data['shirtNumber'],
        'position' : player_data['position'],
        'team_name' : player_data['currentTeam']['name'],
        'team_crest' : player_data['currentTeam']['crest']
    }
    return player


while True: 
    league = input("What league is your player in: ")
    if(league not in leagues):
        print("\nLeague not valid. Choose from available leagues\n")
        for key in leagues:
            print(key)
        print('\n')
    else: 
        league_data = get_league_data(league)

        if(league_data is not None):
            break

while True: 
    name = input("Enter Player Name: ")
    # Searches database first
    player_db = get_player_db(name)
    if(player_db is not None):
        print(f'{player_db} From db')
        break
    else: 
        # If player was not in database, fetches them from API
        player_api = get_player_api(league_data, name)
    if(not player_api):
        print("\nPlayer not found. Please try again\n")
    else:
        # Stores player data in database
        player_api = clean_up_data(player_api)
        add_player_to_db(player_api)
        # Gets player from database
        print(f'{get_player_db(name)} From API')
        break 
