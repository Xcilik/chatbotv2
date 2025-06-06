from ._mongodb import notesdb, textnotesdb, medianotesdb

async def add_notes(user_id, note_name, note_id):
    doc = {"user_id": user_id, "notes": {note_name: note_id}}
    result = await notesdb.find_one({"user_id": user_id})
    if result:
        await notesdb.update_one(
            {"user_id": user_id},
            {"$set": {f"notes.{note_name}": note_id}},
            upsert=True,
        )
    else:
        await notesdb.insert_one(doc)


async def get_notes(user_id, note_name):
    result = await notesdb.find_one({"user_id": user_id})
    if result is not None:
        try:
            note_id = result["notes"][note_name]
            return note_id
        except KeyError:
            return None
    else:
        return None


async def rm_notes(user_id, note_name):
    await notesdb.update_one(
        {"user_id": user_id}, {"$unset": {f"notes.{note_name}": ""}}
    )


async def all_notes(user_id):
    results = await notesdb.find_one({"user_id": user_id})
    try:
        notes_dic = results["notes"]
        key_list = notes_dic.keys()
        return key_list
    except:
        return None


async def rm_all_notes(user_id):
    await notesdb.update_one({"user_id": user_id}, {"$unset": {"notes": ""}})



#text dan media
async def add_text_notes(user_id, filter_name, filter_id):
    doc = {"user_id": user_id, "filter": {filter_name: filter_id}}
    result = await textnotesdb.find_one({"user_id": user_id})
    if result:
        await textnotesdb.update_one(
            {"user_id": user_id},
            {"$set": {f"filter.{filter_name}": filter_id}},
            upsert=True,
        )
    else:
        await textnotesdb.insert_one(doc)


async def get_text_notes(user_id, filter_name):
    result = await textnotesdb.find_one({"user_id": user_id})
    if result is not None:
        try:
            filter_id = result["filter"][filter_name]
            return filter_id
        except KeyError:
            return None
    else:
        return None


async def rm_text_notes(user_id, filter_name):
    await textnotesdb.update_one(
        {"user_id": user_id}, {"$unset": {f"filter.{filter_name}": ""}}
    )


async def add_media_notes(user_id, filter_name, filter_id):
    doc = {"user_id": user_id, "filter": {filter_name: filter_id}}
    result = await medianotesdb.find_one({"user_id": user_id})
    if result:
        await medianotesdb.update_one(
            {"user_id": user_id},
            {"$set": {f"filter.{filter_name}": filter_id}},
            upsert=True,
        )
    else:
        await medianotesdb.insert_one(doc)


async def get_media_notes(user_id, filter_name):
    result = await medianotesdb.find_one({"user_id": user_id})
    if result is not None:
        try:
            filter_id = result["filter"][filter_name]
            return filter_id
        except KeyError:
            return None
    else:
        return None


async def rm_media_notes(user_id, filter_name):
    await medianotesdb.update_one(
        {"user_id": user_id}, {"$unset": {f"filter.{filter_name}": ""}}
    )
