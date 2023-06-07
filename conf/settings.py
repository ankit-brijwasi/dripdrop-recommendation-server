from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# appwrite settings
APPWRITE_ENDPOINT = os.environ.get("APPWRITE_ENDPOINT")
APPWRITE_PROJECT_ID = os.environ.get("APPWRITE_PROJECT_ID")
APPWRITE_SECRET_KEY = os.environ.get("APPWRITE_SECRET_KEY")

# appwrite storages
APPWRITE_USER_DATA_STORAGE_ID = os.environ.get("APPWRITE_USER_DATA_STORAGE_ID")

# appwrite databases
APPWRITE_DATABASE_ID = os.environ.get("APPWRITE_DATABASE_ID")

# appwrite collections
APPWRITE_PROFILE_COLLECTION = os.environ.get("APPWRITE_PROFILE_COLLECTION")
APPWRITE_POST_COLLECTION = os.environ.get("APPWRITE_POST_COLLECTION")
