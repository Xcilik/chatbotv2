from cilik.database import get_prem



def checkprem(func):
    async def wrapper(message):
        user_id = message.from_user.id
        check = await get_prem()
        if user_id not in check:
            return await message.reply(
                "¯\_(ツ)_/¯",
                quote=True,
            )
        return await func(message)

    return wrapper