from fastapi import FastAPI, HTTPException, Depends
from api import search_player_all_leagues, clean_up_data
from database import get_player_db, add_player_to_db, check_db_health, search_players_db, build_search_query, create_user_db, get_user
from pydantic import BaseModel, EmailStr
from datetime import timedelta, timezone
import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pwdlib import PasswordHash
import psycopg
from datetime import datetime, date
import os
from dotenv import load_dotenv


app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_hash = PasswordHash.recommended()

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

class User(BaseModel):
    email : EmailStr 
    password: str


def create_token(email):
    # token expects a 'sub' wich is the subject, or the user (can be email, username, user id...), 
    # and 'exp' which is the expiration of the token
    payload = {
        "sub" : email,
        "exp" : datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    # creates the token using the payload, key, and algorithm
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def decode_token(token):
    # decodes the token to make sure its valid
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # if token is valid, it returns the payload
        return payload
    # Expired token
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Expired token")
    # Token is not valid
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid Token")

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
    
@app.post("/users", status_code=201)
def create_user(user : User):
    # hash password before storing
    hashed_password = password_hash.hash(user.password)
    try: 
        # Attempts to create a new user
        create_user_db(user.email, hashed_password)
        return {"Success" : "User Created"}
    
    # Prevents duplicate accounts using the same email
    except psycopg.errors.UniqueViolation:
        raise HTTPException(status_code=409, detail="Email already in use")
    
@app.post("/login")
def login(form_data : OAuth2PasswordRequestForm = Depends()):
    # Fetch user by email. says '.username' because that's the field in the request form
    logged_user = get_user(form_data.username)
    if(logged_user is None):
        # Returns unauthorized if the email does not exist
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verifies the plain password against the stored hash
    if(password_hash.verify(form_data.password, logged_user[1])):

        # creates token for user, and returns it
        token = create_token(logged_user[0])
        return {"access_token" : token, "token_type": "bearer"}
    else: 
        # Returns unauthorized if the password is incorrect
        raise HTTPException(status_code=401, detail="Invalid email or password")

@app.get("/me")
def get_current_user(token : str = Depends(oauth2_scheme)):
    # if the token is invalid, it raises error
    payload = decode_token(token)
    # token is valid, and returns the 'subject' which is the email in the payload
    return{"email" : payload['sub']}