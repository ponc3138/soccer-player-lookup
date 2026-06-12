# Soccer Player Lookup

A Python CLI app that lets users search for soccer players by league and name.  
The app checks a local PostgreSQL database first. If the player is not found, it fetches player data from the football-data.org API and stores the result in PostgreSQL.

## Status

This project is currently in progress.

## Features

- Search for players by name
- Choose from supported leagues
- Fetch player data from an external API
- Store player data in PostgreSQL
- Check the database before calling the API

## Tech Stack

- Python
- PostgreSQL
- psycopg
- requests
- python-dotenv
- football-data.org API

## Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=your_database_url
FOOTBALL_API_KEY=your_api_key