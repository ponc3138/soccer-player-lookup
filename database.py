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



