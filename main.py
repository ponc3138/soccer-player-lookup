from database import get_player_db, add_player_to_db
from api import search_player_all_leagues, clean_up_data

while True: 
    name = input("Enter Player Name: ")
    # Searches database first
    player_db = get_player_db(name)
    if(player_db is not None):
        print('From db')
        for value in player_db:
            print(f'{value} \n') 
        break
    else:
        player_api = search_player_all_leagues(name)
        if(not player_api):
            print("\nPlayer not found. Please try again\n")
        else: 
            # Stores player data in database
            player_api = clean_up_data(player_api)
            add_player_to_db(player_api)
            # Gets player from database
            print('From API')
            player_api_db = get_player_db(name)
            for value in player_api_db:
                print(f'{value}\n')
            break 
