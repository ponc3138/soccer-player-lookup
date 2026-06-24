import psycopg
from psycopg_pool import ConnectionPool
import os
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if(not DATABASE_URL):
    print("Missing DATABASE_URL")
    exit()

pool = ConnectionPool(DATABASE_URL)

def check_db_health():
    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                return True
    except psycopg.DatabaseError: 
        return False

def get_player_db(name):
    with pool.connection() as conn: 
        with conn.cursor() as cur:    
            result = cur.execute(""" SELECT * 
                                 FROM players 
                                 WHERE LOWER(name) = LOWER(%s)""", (name.strip(), ))
            return result.fetchone()


def add_player_to_db(player):

    # Automatically commits on success, rolls back on failure
    with pool.connection() as conn:
        with conn.cursor() as cur:
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


def build_search_query(name = None, team = None, nationality = None, position = None):
    # Base query used when no filters are provided
    base_query  = "SELECT * FROM players"
    conditions = []
    parameters = []

    # Add optional name filter
    if(name is not None and name.strip()):
        conditions.append("LOWER(name) LIKE LOWER(%s)")
        parameters.append(f'%{name.strip()}%')

    # Add optional team filter
    if(team is not None and team.strip()):
        conditions.append("LOWER(team_name) = LOWER(%s)")
        parameters.append(team.strip())

    # Add optional nationality filter
    if(nationality is not None and nationality.strip()):
        conditions.append("LOWER(nationality) = LOWER(%s)")
        parameters.append(nationality.strip())

    # Add optional position filter
    if(position is not None and position.strip()):
        conditions.append("LOWER(position) = LOWER(%s)")
        parameters.append(position.strip())
    
    # Return base query if no filters were given
    if(len(conditions) == 0):
        return (base_query, parameters)
    else: 
        # Join all conditions into one WHERE clause
        final_conditions = ' AND '.join(conditions)
        final_query = f'{base_query} WHERE {final_conditions}'
        return (final_query, parameters)
        

def search_players_db(query, params):
    with pool.connection() as conn:
        with conn.cursor() as cur:
            # Execute query with params. Pyscopg3 handles empty params, if there is no filters
            result = cur.execute(query, params)
            return result.fetchall()