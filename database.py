import psycopg
import os
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if(not DATABASE_URL):
    print("Missing DATABASE_URL")
    exit()

conn = psycopg.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()

def check_db_health():
    try:
        cur.execute("SELECT 1")
        return True
    except psycopg.DatabaseError: 
        return False

def get_player_db(name):
    result = cur.execute(""" SELECT * 
                         FROM players 
                         WHERE LOWER(name) = LOWER(%s)""", (name.strip(), ))
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


def build_search_query(name = None, team = None):
    # Base query used when no filters are provided
    base_query  = "SELECT * FROM players"
    conditions = []
    paramaters = []

    # Add optional name filter
    if(name is not None):
        conditions.append("LOWER(name) LIKE LOWER(%s)")
        paramaters.append(f'%{name.strip()}%')

    # Add optional team filter
    if(team is not None):
        conditions.append("LOWER(team_name) = LOWER(%s)")
        paramaters.append(team.strip())
    
    # Return base query if no filters were given
    if(len(conditions) == 0):
        return (base_query, paramaters)
    else: 
        # Join all conditions into one WHERE clause
        final_conditions = ' AND '.join(conditions)
        final_query = f'{base_query} WHERE {final_conditions}'
        return (final_query, paramaters)
        

def search_players_db(query, params):
    # Execute query with params if filters exist
    if(len(params) > 0):
        result = cur.execute(query, params)
        return result.fetchall()
    else: 
        # Execute base query without params
        result = cur.execute(query)
        return result.fetchall()