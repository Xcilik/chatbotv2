from pyrogram import filters
from datetime import datetime
from pytz import timezone

from cilik import bot

from cilik.database import info_wlcm, add_user_wlcm, get_user_wlcm, get_wlcm_text, get_prem

DEFAULT_TEXT = """
Welcome {mention} 👋🏻

How are you today? Hope everything will be fine.
"""

def get_datetime():
    now = datetime.now(timezone("Asia/Jakarta"))
    return now.strftime('%A, %d-%B-%Y'), now.strftime('%H:%M:%S %Z')

def format_text(template, user, sender):
    date, time = get_datetime()
    return template.format(
        mename=f"{user.first_name} {user.last_name or ''}".strip(),
        memention=user.mention,
        name=f"{sender.first_name} {sender.last_name or ''}".strip(),
        username=f"@{sender.username}" if sender.username else sender.mention,
        mention=sender.mention,
        id=sender.id,
        date=date,
        time=time
    )

@bot.on_message(filters.business & filters.private & filters.incoming, group=2)
async def wlcm(client, message):
    if not message.business_connection_id or not message.from_user:
        return

    connection = await client.get_business_connection(message.business_connection_id)
    user_id = connection.user.id
    if user_id not in await get_prem():
        return
    from_id = message.from_user.id

    # Filter pesan dari diri sendiri, dari 777000, atau yang sudah pernah disambut
    if from_id == user_id or message.chat.id == 777000:
        return
    if int(message.chat.id) in await get_user_wlcm(user_id):
        return

    if await info_wlcm(user_id) != "on":
        return

    text_template = await get_wlcm_text(user_id) or DEFAULT_TEXT
    formatted_text = format_text(text_template, connection.user, message.from_user)

    await message.reply(text=formatted_text)
    await add_user_wlcm(user_id, message.chat.id)
