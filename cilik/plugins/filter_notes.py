import re
from pyrogram import filters
from datetime import datetime
from pytz import timezone

from cilik import bot
from cilik.utils.cekprem import checkprem
from cilik.database import (
    all_notes, get_notes, get_media_notes, get_text_notes,
    all_filter, get_text_filter, get_media_filter, get_prem
)

def get_datetime():
    dt = datetime.now(timezone("Asia/Jakarta"))
    return dt.strftime('%A, %d-%B-%Y'), dt.strftime('%H:%M:%S %Z')

def format_text(template, user, target):
    date, time = get_datetime()
    return template.format(
        mename=f"{user.first_name} {user.last_name or ''}".strip(),
        memention=user.mention,
        name=f"{target.first_name} {target.last_name or ''}".strip(),
        username=f"@{target.username}" if target.username else target.mention,
        mention=target.mention,
        id=target.id,
        date=date,
        time=time
    )

@bot.on_message(
    filters.business & filters.private & ~filters.forwarded,
    group=1
)
async def filters_re(client, message):
    if not message.business_connection_id:
        return
    
    connection = await client.get_business_connection(message.business_connection_id)
    if not connection:
        return

    user_id = connection.user.id
    if user_id not in await get_prem():
        return
    user = connection.user
    text = message.text.strip() if message.text else ""

    if text.startswith("/get"):
        if message.from_user.id != user_id:
            return

        args = text.split(maxsplit=1)
        if len(args) == 1:
            await message.reply("`/get nama_catatan`", reply_to_message_id=message.id)
            return

        note_name = args[1].lower()
        if await get_notes(user_id, note_name):
            note_text = await get_text_notes(user_id, note_name)
            note_media = await get_media_notes(user_id, note_name)

            if note_text and not note_media:
                await message.reply(
                    text=format_text(note_text, user, message.chat),
                    reply_to_message_id=message.id
                )
            elif note_text and note_media:
                await message.reply_cached_media(
                    note_media,
                    caption=format_text(note_text, user, message.chat),
                    reply_to_message_id=message.id
                )
            elif note_media:
                await message.reply_cached_media(note_media, reply_to_message_id=message.id)
            else:
                await message.reply(f"Catatan `{note_name}` tidak ada data.", reply_to_message_id=message.id)
        else:
            await message.reply(f"Catatan `{note_name}` tidak ditemukan.", reply_to_message_id=message.id)
        return

    if text.startswith("/listnote"):
        if message.from_user.id != user_id:
            return
        try:
            notes = await all_notes(user_id)
            msg = "<b>Saved Notes</b>\n\n" + "\n".join(f"• <code>{note}</code>" for note in notes)
            await message.reply(msg, reply_to_message_id=message.id)
        except Exception:
            await message.reply("Tidak ada catatan yang tersimpan.", reply_to_message_id=message.id)
        return

    # Jangan teruskan kalau pengirim adalah pemilik bisnis
    if message.from_user.id == user_id or not text:
        return

    filters_list = await all_filter(user_id)
    if not filters_list:
        return

    for keyword in filters_list:
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, text, flags=re.IGNORECASE):
            filter_text = await get_text_filter(user_id, keyword)
            filter_media = await get_media_filter(user_id, keyword)

            if filter_text and not filter_media:
                await message.reply(
                    text=format_text(filter_text, user, message.from_user),
                )
            elif filter_text and filter_media:
                await message.reply_cached_media(
                    filter_media,
                    caption=format_text(filter_text, user, message.from_user),
                )
            elif filter_media:
                await message.reply_cached_media(filter_media)
            break
