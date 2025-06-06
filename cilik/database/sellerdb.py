from ._mongodb import premdb


async def get_prem():
    sudoers = await premdb.find_one({"sudo": "sudo"})
    if not sudoers:
        return []
    return sudoers["sudoers"]


async def add_prem(user_id):
    sudoers = await get_prem()
    if user_id not in sudoers:
        sudoers.append(user_id)
        await premdb.update_one(
            {"sudo": "sudo"}, {"$set": {"sudoers": sudoers}}, upsert=True
        )


async def remove_prem(user_id):
    sudoers = await get_prem()
    if user_id in sudoers:
        sudoers.remove(user_id)
        await premdb.update_one(
            {"sudo": "sudo"}, {"$set": {"sudoers": sudoers}}, upsert=True
        )

    