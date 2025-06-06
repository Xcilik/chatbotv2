from ._mongodb import waktuhabisdb

async def get_date_end(user_id):
    user = await waktuhabisdb.users.find_one({"_id": user_id})
    if user:
        return user.get("date_id")
    else:
        return None


async def add_date_end(user_id, date_id):
    await waktuhabisdb.users.update_one(
        {"_id": user_id}, {"$set": {"date_id": date_id}}, upsert=True
    )


async def remove_date_end(user_id):
    await waktuhabisdb.users.update_one(
        {"_id": user_id}, {"$unset": {"date_id": ""}}, upsert=True
    )
