# app/config.py
import os
from dotenv import load_dotenv
import redis

load_dotenv()  # Carga variables del archivo .env

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

REDIS_URL = os.getenv("REDIS_URL")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
API_URL = os.getenv("API_URL")
