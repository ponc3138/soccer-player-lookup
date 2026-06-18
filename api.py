import time
import requests
from dotenv import load_dotenv
import os



load_dotenv()
API_KEY = os.getenv("FOOTBALL_API_KEY")
if(not API_KEY):
    print("MIssing FOOTBALL_API_KEY")
    exit()
    
BASE_URL = "https://api.football-data.org/v4"
headers = {"X-Auth-Token": API_KEY}

leagues = {
    'FIFA World Cup' : 'WC',
    'UEFA Champions League' : 'CL',
    'Bundesliga' : 'BL1',
    'La Liga' : 'PD',
    'Premier League' : 'PL',
    'Ligue 1' : 'FL1',
    'Primeira Liga' : 'PPL',
    'European Championship' : 'EC',
    'Serie A' : 'SA',
    'Campeonato Brasileiro Série A' : 'BSA',
    'Championship' : 'ELC',
    'Eredivisie' : 'DED'
}



def get_league_data(league_name):
    league_code = leagues[league_name]
    response = requests.get(f"{BASE_URL}/competitions/{league_code}/teams", headers=headers)
    if(response.status_code == 200):
        return response.json()
    else: 
        print(f"Something went wrong. Error Code: {response.status_code}")
        if(response.status_code == 429):
            print('Retrying in 60 seconds')
            time.sleep(60)
        response = requests.get(f"{BASE_URL}/competitions/{league_code}/teams", headers=headers)
        if(response.status_code == 200):
            return response.json()
        else: 
            print(response.text)
            return None


def search_player_all_leagues(name):
    for league in leagues:
        print(f'Checking {league}...')
        league_data = get_league_data(league)
        if(not league_data):
            continue
        player_data = get_player_api(league_data, name)
        if(player_data is not None):
            return player_data
        
    return None


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
