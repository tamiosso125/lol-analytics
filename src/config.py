"""Configuração central: lê variáveis do .env."""
import os
from dotenv import load_dotenv

load_dotenv()

RIOT_API_KEY = os.environ["RIOT_API_KEY"]
RIOT_PLATFORM = os.getenv("RIOT_PLATFORM", "br1")      # summoner/league endpoints
RIOT_REGION = os.getenv("RIOT_REGION", "americas")     # match-v5 endpoints
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/lol_analytics"
)
