import datetime
from datetime import timedelta
from pytz import timezone

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from cilik import bot
from cilik.database import add_prem, get_prem, add_date_end, get_date_end
from config import SELLER_GROUP


@bot.on_message(filters.command("chatbot") & filters.group)
async def akses(client, message):
    if message.chat.id != SELLER_GROUP:
        return

    if len(message.command) < 2:
        return await message.reply_text("Berikan user_id/username.")

    if len(message.command) < 3:
        return await message.reply_text(
            f"Berikan plan 1 - 12 Bulan\n\nContoh: /{message.command[0]} @jono 1 or /{message.command[0]} user_id 1"
        )

    # Validasi plan 1-12 bulan
    try:
        plan_months = int(message.command[2])
        if plan_months < 1 or plan_months > 12:
            return await message.reply_text("Plan harus antara 1 hingga 12 bulan.")
    except ValueError:
        return await message.reply_text(
            "Plan harus berupa angka bulanan antara 1 hingga 12."
        )

    h = plan_months * 30
    time = datetime.datetime.now(timezone("Asia/Jakarta")) + timedelta(days=h)
    user_input = message.text.split()[1]
    seller_id = message.from_user.id

    # Cek apakah input adalah username atau user_id
    if "@" in user_input:
        user_input = user_input.replace("@", "")
        try:
            user = await client.get_users(user_input)
            user_id = user.id
        except Exception:
            return await message.reply_text("Username tidak ditemukan.")
    else:
        user_id = int(user_input)

    # Cek apakah user sudah terdaftar di database
    member = await get_prem()
    existing_expiry = await get_date_end(user_id)
    expiry_date = existing_expiry + timedelta(days=h) if existing_expiry else time

    # Tambahkan atau update plan dan expiry user
    if user_id not in member:
        await add_prem(user_id)

    await add_date_end(user_id, expiry_date)

    buttonsa = [
        [InlineKeyboardButton("User", url=f"tg://user?id={user_id}")]
    ]
    await message.reply_text(
        f"Done **Chat Bot**!\n\nUser id: <code>{user_id}</code>\nPlan: <code>{plan_months} bulan</code>\nExpired: {expiry_date.strftime('%d-%B-%Y')}\n\nBuat di @{bot.me.username}",
        reply_markup=InlineKeyboardMarkup(buttonsa),
        disable_web_page_preview=True,
    )
    try:
        await bot.send_message(user_id, f"✅ Chat bot sudah aktif\n📆 Expired: {expiry_date.strftime('%d-%B-%Y')}")
    except:
        pass