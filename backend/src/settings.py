from dotenv import load_dotenv
import os
load_dotenv()

database_filename = os.environ.get("database_filename")
AUTH0_DOMAIN= os.environ.get("AUTH0_DOMAIN")
ALGORITHMS = os.environ.get("ALGORITHMS")
API_AUDIENCE = os.environ.get("API_AUDIENCE")