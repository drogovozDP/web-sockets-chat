from dotenv import load_dotenv
import os

load_dotenv()

SECRET_AUTH = os.environ.get("SECRET_AUTH")
SECRET_MANAGER = os.environ.get("SECRET_MANAGER")
LIFETIME_SECONDS = int(os.environ.get("LIFETIME_SECONDS"))

DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_NAME = os.environ.get("DB_NAME")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
