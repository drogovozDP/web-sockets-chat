from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

SECRET_AUTH = os.environ.get("SECRET_AUTH")
ALGORITHM = os.environ.get("ALGORITHM")
LIFETIME_SECONDS = int(os.environ.get("LIFETIME_SECONDS"))

MEDIA_FILES_PATH = Path("src/media")

DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_NAME = os.environ.get("DB_NAME")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
