from dotenv import load_dotenv
import os

dot = load_dotenv()

# Database
DB_LOGIN = os.getenv("DB_LOGIN")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql://{DB_LOGIN}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

TOKEN = os.getenv("TOKEN")
YOUKASSA_ACCOUNT_ID = os.getenv("YOUKASSA_ACCOUNT_ID")
YOUKASSA_SECRET_KEY = os.getenv("YOUKASSA_SECRET_KEY")
ADMIN_IDS = os.getenv("ADMIN_IDS")
MAX_ADMIN = os.getenv("MAX_ADMIN")
ALEX_ADMIN = os.getenv("ALEX_ADMIN")

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")
PRODUCTION = os.getenv("PRODUCTION")

PROXY = os.getenv("PROXY")