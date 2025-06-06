from motor.motor_asyncio import AsyncIOMotorClient

from config import MONGO_URL

# function database
mongo_client = AsyncIOMotorClient(MONGO_URL)
mongodb = mongo_client.chatbot

#bot
usersdb = mongodb.broadcast
jumlahclient = mongodb.jumlahclient

#plugins
welcomedb = mongodb.welcome
welcomecekdb = mongodb.welcomecek
welcometextdb = mongodb.welcometext
welcomeclientdb = mongodb.welcomeclient

filterdb = mongodb.filter
cekfilterdb = mongodb.cekfilter
textfilterdb = mongodb.textfilter
mediafilterdb = mongodb.mediafilter

notesdb = mongodb.notes
textnotesdb = mongodb.textnotes
medianotesdb = mongodb.medianotes

#client & exp
waktuhabisdb = mongodb.expired
premdb = mongodb.prem
