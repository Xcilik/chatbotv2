from ._mongodb import filterdb, cekfilterdb, textfilterdb, mediafilterdb

async def info_filter(user_id):
    cek = await cekfilterdb.find_one({"_id": user_id})
    if not cek:
        return "off"
    return cek["cek_filter"]


async def set_filter(user_id, cek_filter):
    await cekfilterdb.update_one(
        {"_id": user_id}, {"$set": {"cek_filter": cek_filter}}, upsert=True
    )



async def add_filter(user_id, filter_name, filter_id):
    doc = {"user_id": user_id, "filter": {filter_name: filter_id}}
    result = await filterdb.find_one({"user_id": user_id})
    if result:
        await filterdb.update_one(
            {"user_id": user_id},
            {"$set": {f"filter.{filter_name}": filter_id}},
            upsert=True,
        )
    else:
        await filterdb.insert_one(doc)


async def get_filter(user_id, filter_name):
    result = await filterdb.find_one({"user_id": user_id})
    if result is not None:
        try:
            filter_id = result["filter"][filter_name]
            return filter_id
        except KeyError:
            return None
    else:
        return None


async def rm_filter(user_id, filter_name):
    await filterdb.update_one(
        {"user_id": user_id}, {"$unset": {f"filter.{filter_name}": ""}}
    )


async def all_filter(user_id):
    results = await filterdb.find_one({"user_id": user_id})
    try:
        filter_dic = results["filter"]
        key_list = filter_dic.keys()
        return key_list
    except:
        return None


async def rm_all_filter(user_id):
    await filterdb.update_one({"user_id": user_id}, {"$unset": {"filter": ""}})


#text dan media
async def add_text_filter(user_id, filter_name, filter_id):
    doc = {"user_id": user_id, "filter": {filter_name: filter_id}}
    result = await textfilterdb.find_one({"user_id": user_id})
    if result:
        await textfilterdb.update_one(
            {"user_id": user_id},
            {"$set": {f"filter.{filter_name}": filter_id}},
            upsert=True,
        )
    else:
        await textfilterdb.insert_one(doc)


async def get_text_filter(user_id, filter_name):
    result = await textfilterdb.find_one({"user_id": user_id})
    if result is not None:
        try:
            filter_id = result["filter"][filter_name]
            return filter_id
        except KeyError:
            return None
    else:
        return None


async def rm_text_filter(user_id, filter_name):
    await textfilterdb.update_one(
        {"user_id": user_id}, {"$unset": {f"filter.{filter_name}": ""}}
    )


async def add_media_filter(user_id, filter_name, filter_id):
    doc = {"user_id": user_id, "filter": {filter_name: filter_id}}
    result = await mediafilterdb.find_one({"user_id": user_id})
    if result:
        await mediafilterdb.update_one(
            {"user_id": user_id},
            {"$set": {f"filter.{filter_name}": filter_id}},
            upsert=True,
        )
    else:
        await mediafilterdb.insert_one(doc)


async def get_media_filter(user_id, filter_name):
    result = await mediafilterdb.find_one({"user_id": user_id})
    if result is not None:
        try:
            filter_id = result["filter"][filter_name]
            return filter_id
        except KeyError:
            return None
    else:
        return None


async def rm_media_filter(user_id, filter_name):
    await mediafilterdb.update_one(
        {"user_id": user_id}, {"$unset": {f"filter.{filter_name}": ""}}
    )
