from pyrogram import filters

from cilik import bot
from cilik.database import add_served_user, get_prem, get_date_end
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .mustjoin import subcribe

@bot.on_message(filters.command("start") & filters.private)
@subcribe
async def start(client, message):
    await add_served_user(message.from_user.id)
    checkprem = await get_prem()
    if message.from_user.id not in checkprem:
        msg = f"""
👋🏻 Halo {message.from_user.mention}
__Dengan @{bot.me.username} anda dapat membuat bot kustom keperluan business anda:__

• Memberi kata sambutan kepada pengguna
• Menerima dan membalas pesan pengguna dengan menambahkan filter atau balasan otomatis
• Menyimpan notes / catatan
• Supported Text dan Media

__...Dan masih banyak lagi!__
"""        
        buttons = [
            [
                InlineKeyboardButton("💰 Langganan", url="t.me/iaamat"),
            ],
        ]  
        return await message.reply(msg, reply_markup=InlineKeyboardMarkup(buttons))
    
    text = f"""
👋🏻 Halo {message.from_user.mention}
__Dengan @{bot.me.username} anda dapat membuat bot kustom keperluan business anda:__

• Memberi kata sambutan kepada pengguna
• Menerima dan membalas pesan pengguna dengan menambahkan filter atau balasan otomatis
• Menyimpan notes / catatan
• Supported Text dan Media

__...Dan masih banyak lagi!__
"""
    buttons = [
        [
            InlineKeyboardButton("⚙️ Setting", callback_data="setting"),
            InlineKeyboardButton("💡 Tutorial", callback_data="tutorial"),
        ],
        [
            InlineKeyboardButton("👤 Saya", callback_data="saya"),
        ],
    ]  
    await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons))


@bot.on_callback_query(filters.regex("start_back"))
async def start_back(client, callback_query):
    text = f"""
👋🏻 Halo {callback_query.from_user.mention}
__Dengan @{bot.me.username}  anda dapat membuat bot kustom keperluan business anda:__

• Memberi kata sambutan kepada pengguna
• Menerima dan membalas pesan pengguna dengan menambahkan filter atau balasan otomatis
• Menyimpan notes / catatan
• Supported Text dan Media

__...Dan masih banyak lagi!__
"""
    buttons = [
        [
            InlineKeyboardButton("⚙️ Setting", callback_data="setting"),
            InlineKeyboardButton("💡 Tutorial", callback_data="tutorial"),
        ],
        [
            InlineKeyboardButton("👤 Saya", callback_data="saya"),
        ],
    ]   
    await callback_query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True
    ) 


@bot.on_callback_query(filters.regex("tutorial"))
async def tutorial(client, callback_query):
    text = f"""
💡 **Tutorial:**

• Buka Pengaturan Telegram
• Pilih opsi "Telegram Business"
• Klik pada menu "Chatbot"
• Masukkan @{bot.me.username} pada kolom Username atau URL Bot
• Pastikan untuk mengaktifkan atau mencentang opsi perizinan bot untuk membalas pesan
• ✅ **Selesai!**
"""
    buttons = [
        [
            InlineKeyboardButton("🔙 Kembali", callback_data="start_back"),            
            InlineKeyboardButton("⚙️ Setting", callback_data="setting"),
        ],
    ]
    await callback_query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True
    )    

@bot.on_callback_query(filters.regex("saya"))
async def saya(client, callback_query):
    exp = await get_date_end(callback_query.from_user.id)
    text = f"""

• Name : {callback_query.from_user.mention}
• Id : {callback_query.from_user.id}
• Expired : {exp.strftime('%d-%B-%Y')}
"""
    buttons = [
        [
            InlineKeyboardButton("🔙 Kembali", callback_data="start_back"),            
            InlineKeyboardButton("⚙️ Setting", callback_data="setting"),
        ],
    ]
    await callback_query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True
    )    


