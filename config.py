import os

from dotenv import load_dotenv

load_dotenv(".env")

BOT_TOKEN = os.environ.get("BOT_TOKEN", "7401820056:AAHU9cijeViZ1g9-9TXqzlZ7lsbXWf9hDnw")
API_ID = int(os.environ.get("API_ID", "21445722"))
API_HASH = os.environ.get("API_HASH", "710f18f90849255dd85837d00d5fe85f")
OWNER = int(os.environ.get("OWNER", "1784606556"))
MONGO_URL = os.environ.get("MONGO_URL", "mongodb+srv://chat:chat@cluster0.jt616lp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
MUST_JOIN = os.environ.get("MUST_JOIN", "katalogbottelegram")
SELLER_GROUP = int(os.environ.get("SELLER_GROUP", "-1002091170438"))
