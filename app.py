from fastapi import FastAPI, HTTPException
from api import search_player_all_leagues, clean_up_data
from database import get_player_db, add_player_to_db, check_db_health, search_players_db, build_search_query
from pydantic import BaseModel
from datetime import date


app = FastAPI()

class Player(BaseModel):
    id : int
    api_player_id: int
    name : str 
    nationality : str 
    date_of_birth : date
    shirt_number : int
    position : str
    team_name : str
    team_crest : str

class PlayerSearchResponse(BaseModel):
    players : list[Player]

def row_to_dict(player):
    dict_player = {
        "id" : player[0],
        "api_player_id" : player[1],
        "name" : player[2],
        "nationality" : player[3],
        "date_of_birth" : player[4],
        "shirt_number" : player[5],
        "position" : player[6],
        "team_name" : player[7],
        "team_crest" : player[8]
    }

    return dict_player


@app.get("/players/{player}", response_model=Player)
def get_player(player : str):
    new_player = get_player_db(player)
    if(not new_player):
        api_player = search_player_all_leagues(player)
        if(not api_player):
            raise HTTPException(status_code=404, detail="Player not found")
        else:
            api_player = clean_up_data(api_player)
            add_player_to_db(api_player)
            api_player = get_player_db(player)
            return row_to_dict(api_player)
        
    return row_to_dict(new_player)


@app.get("/players", response_model=PlayerSearchResponse)
def search_player(name: str = None, 
                  team: str = None, 
                  nationality: str = None, 
                  position: str = None):
    
    # Build SQL query based on optional filters
    query_params = build_search_query(name, team, nationality, position)
    result = search_players_db(query_params[0], query_params[1])

    # Convert database rows into JSON-friendly dictionaries
    result_list = []
    for player in result:
        result_list.append(row_to_dict(player))
    return{'players': result_list}


@app.get("/health")
def get_health():
    if(not check_db_health()):
        return {"status" : "unhealthy",
                "database" : "error"}
    else:
        return {"status" : "healthy",
                "database": "connected"}
    