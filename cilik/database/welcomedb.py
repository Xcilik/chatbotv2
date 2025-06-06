from ._mongodb import welcomedb, welcomecekdb, welcometextdb, welcomeclientdb


# user welcome
async def get_user_wlcm(user_id):
    user = await welcomedb.find_one({"user_id": user_id})
    if not user:
        return []
    return user["wlcm"]


async def clear_user_wlcm(user_id):
    user = await welcomedb.find_one({"user_id": user_id})
    if user:
        await welcomedb.update_one(
            {"user_id": user_id}, {"$set": {"wlcm": []}}, upsert=True
        )


async def add_user_wlcm(user_id, chat_id):
    wlcm = await get_user_wlcm(user_id)
    if chat_id not in wlcm:
        wlcm.append(chat_id)
        await welcomedb.update_one(
            {"user_id": user_id}, {"$set": {"wlcm": wlcm}}, upsert=True
        )


async def remove_user_wlcm(user_id, chat_id):
    wlcm = await get_user_wlcm(user_id)
    if chat_id in wlcm:
        wlcm.remove(chat_id)
        await welcomedb.update_one(
            {"user_id": user_id}, {"$set": {"wlcm": wlcm}}, upsert=True
        )


#info welcome
async def info_wlcm(user_id):
    cek = await welcomecekdb.find_one({"user_id": user_id})
    if not cek:
        return "off"
    return cek["cek_wlcm"]



async def set_wlcm(user_id, cek_wlcm):
    await welcomecekdb.update_one(
        {"user_id": user_id}, {"$set": {"cek_wlcm": cek_wlcm}}, upsert=True
    )


# text welcome
async def add_wlcm_text(user_id, wlcm_text):
    await welcometextdb.update_one(
        {"user_id": user_id}, {"$set": {"wlcm_text": wlcm_text}}, upsert=True
    )


async def get_wlcm_text(user_id):
    pmmsg = await welcometextdb.find_one({"user_id": user_id})
    if not pmmsg:
        return None
    return pmmsg["wlcm_text"]


async def rm_wlcm_text(user_id):
    await welcometextdb.delete_one({"user_id": user_id})


#client welcome
async def get_client_wlcm():
    sudoers = await welcomeclientdb.find_one({"sudo": "sudo"})
    if not sudoers:
        return []
    return sudoers["sudoers"]


async def add_client_wlcm(user_id):
    sudoers = await get_client_wlcm()
    if user_id not in sudoers:
        sudoers.append(user_id)
        await welcomeclientdb.update_one(
            {"sudo": "sudo"}, {"$set": {"sudoers": sudoers}}, upsert=True
        )


async def remove_client_wlcm(user_id):
    sudoers = await get_client_wlcm()
    if user_id in sudoers:
        sudoers.remove(user_id)
        await welcomeclientdb.update_one(
            {"sudo": "sudo"}, {"$set": {"sudoers": sudoers}}, upsert=True
        )
