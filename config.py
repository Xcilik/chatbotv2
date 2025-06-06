import os

from dotenv import load_dotenv

load_dotenv(".env")

BOT_TOKEN = os.environ.get("BOT_TOKEN", "7521309897:AAEITsse9EQY_BvJteguTl3GDzEroKbsNVQ")
API_ID = int(os.environ.get("API_ID", "21445722"))
API_HASH = os.environ.get("API_HASH", "710f18f90849255dd85837d00d5fe85f")
OWNER = int(os.environ.get("OWNER", "1784606556"))
MONGO_URL = os.environ.get("MONGO_URL", "mongodb+srv://chatbot:chatbot@cluster0.wvgny.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
MUST_JOIN = os.environ.get("MUST_JOIN", "katalogbottelegram")
