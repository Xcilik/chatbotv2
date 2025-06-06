from asyncio import sleep

from pyrogram.enums import ChatType, ParseMode
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pykeyboard import InlineKeyboard

from pyromod.exceptions import ListenerStopped as meki
from cilik import bot
from cilik.database import *




@bot.on_callback_query(filters.regex("setting"))
async def setting(client, callback_query):
    text = """
📝 **Menu yang tersedia:**

• **Filter** - Balasan otomatis sesuai kata kunci
• **Notes** - Mengirim catatan sesuai nama catatan
• **Welcome** - Pesan sambutan kepada pengguna, __(pesan akan terkirim setiap 24 jam sekali)__

Silahkan pilih apa yang anda mau atur/setting!
"""
    button_setting = [
        [
            InlineKeyboardButton("Filter", callback_data="cb_set_filter"),
            InlineKeyboardButton("Notes", callback_data="cb_set_notes"),                
        ],          
        [
            InlineKeyboardButton("Welcome", callback_data="cb_set_welcome"),                 
        ],                           
        [
            InlineKeyboardButton("🔙 Kembali", callback_data="start_back"),          
              
        ],                  
    ]
    await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(button_setting))  


# Fungsi untuk membuat tata letak tombol berdasarkan jumlah kata kunci


@bot.on_callback_query(filters.regex("cb_set_filter"))
async def cb_set_filter(client, callback_query):
    user_id = callback_query.from_user.id    
    await client.stop_listening(chat_id=user_id, user_id=user_id)
    datakunci = await all_filter(user_id)
    
    if not datakunci:
        text = "🤷 Kamu belum memiliki kata kunci silahkan buat!"
        buttons = [
            [InlineKeyboardButton("➕ Buat kata kunci", callback_data="cb_tambah_filter")],
            [InlineKeyboardButton("🔙 Kembali", callback_data="setting")]
        ]
        return await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))
    
    text = "**📊 Daftar kata kunci**"
    buttons = generate_keyboard(list(datakunci))
    
    await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))

def generate_keyboard(datakunci, page=1):
    # Fungsi untuk membuat keyboard sesuai dengan jumlah kata kunci yang dimiliki pengguna
    buttons = []
    buttons.append([InlineKeyboardButton("➕ Tambah kata kunci", callback_data="cb_tambah_filter")])
                   
    start_index = (page - 1) * 10
    end_index = min(page * 10, len(datakunci))
    for i in range(start_index, end_index, 2):
        row = [InlineKeyboardButton(datakunci[i], callback_data=f"aturkatakuncifilter {datakunci[i]}")]
        if i + 1 < end_index:
            row.append(InlineKeyboardButton(datakunci[i + 1], callback_data=f"aturkatakuncifilter {datakunci[i + 1]}"))
        buttons.append(row)
    
    if len(datakunci) <= 10:
        buttons.append([InlineKeyboardButton("🔙 Kembali", callback_data="setting")])
    else:
        total_pages = (len(datakunci) - 1) // 10 + 1
        
        if total_pages == 1:
            buttons.append([InlineKeyboardButton("🔙 Kembali", callback_data="setting")])
        elif total_pages == 2:
            if page == 1:
                buttons.append([
                    InlineKeyboardButton(f"{page}/{total_pages}", callback_data="cb_filter_current"),
                    InlineKeyboardButton("▶️", callback_data=f"cb_filter_next {page}"),
                    InlineKeyboardButton("⏭️", callback_data="cb_filter_last"),
                ])
            else:
                buttons.append([
                    InlineKeyboardButton("⏮️", callback_data="cb_filter_first"),
                    InlineKeyboardButton("◀️", callback_data=f"cb_filter_previous {page}"),
                    InlineKeyboardButton(f"{page}/{total_pages}", callback_data="cb_filter_current"),                    
                ])           
        else:
            if page == 1:
                buttons.append([
                    InlineKeyboardButton(f"{page}/{total_pages}", callback_data="cb_filter_current"),
                    InlineKeyboardButton("▶️", callback_data=f"cb_filter_next {page}"),
                    InlineKeyboardButton("⏭️", callback_data="cb_filter_last"),
                ])
            elif page <= total_pages - 1:
                buttons.append([
                    InlineKeyboardButton("⏮️", callback_data="cb_filter_first"),
                    InlineKeyboardButton("◀️", callback_data=f"cb_filter_previous {page}"),
                    InlineKeyboardButton(f"{page}/{total_pages}", callback_data="cb_filter_current"),
                    InlineKeyboardButton("▶️", callback_data=f"cb_filter_next {page}"),
                    InlineKeyboardButton("⏭️", callback_data="cb_filter_last"),
                ])
            else:
                buttons.append([
                    InlineKeyboardButton("⏮️", callback_data="cb_filter_first"),
                    InlineKeyboardButton("◀️", callback_data=f"cb_filter_previous {page}"),
                    InlineKeyboardButton(f"{page}/{total_pages}", callback_data="cb_filter_current"),                    
                ])
                                          
        buttons.append([InlineKeyboardButton("🔙 Kembali", callback_data="setting")])
                       
    return buttons


# Fungsi untuk menambahkan navigasi untuk keyboard jika jumlah kata kunci lebih dari 10
@bot.on_callback_query(filters.regex("cb_filter_first|cb_filter_previous|cb_filter_current|cb_filter_next|cb_filter_last"))
async def cb_filter_navigation(client, callback_query):
    user_id = callback_query.from_user.id
    datakunci = await all_filter(user_id)
    query = callback_query.data.split()
    if not datakunci:
        text = "🤷 Kamu belum memiliki kata kunci, silahkan buat!"
        buttons = [
            [InlineKeyboardButton("➕ Buat kata kunci", callback_data="cb_tambah_filter")],
            [InlineKeyboardButton("🔙 Kembali", callback_data="setting")]
        ]
        return await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))
    
    # Parse the callback data
    action = query[0]
    
    if action == "cb_filter_next":
        await handle_next_page(callback_query, datakunci, query[1])
    elif action == "cb_filter_previous":
        await handle_previous_page(callback_query, datakunci, query[1])
    elif action == "cb_filter_first":
        await handle_first_page(callback_query, datakunci)
    elif action == "cb_filter_last":
        await handle_last_page(callback_query, datakunci)
    else:
        # Invalid action, do nothing
        await callback_query.answer()

async def handle_next_page(callback_query, datakunci, page):
    user_id = callback_query.from_user.id
    pageu = int(page) + 1
    buttons = generate_keyboard(list(datakunci), pageu)
    
    await callback_query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))
    await callback_query.answer()

async def handle_previous_page(callback_query, datakunci, page):
    user_id = callback_query.from_user.id
    pageu = int(page) - 1    
    buttons = generate_keyboard(list(datakunci), pageu)
    
    await callback_query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))
    await callback_query.answer()
    


async def handle_first_page(callback_query, datakunci):
    user_id = callback_query.from_user.id
    buttons = generate_keyboard(list(datakunci), 1)
    
    await callback_query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))
    await callback_query.answer()

async def handle_last_page(callback_query, datakunci):
    user_id = callback_query.from_user.id
    total_pages = (len(datakunci) - 1) // 10 + 1
    buttons = generate_keyboard(list(datakunci), total_pages)
    
    await callback_query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))
    await callback_query.answer()
                           

# Gunakan fungsi ini di tempat Anda memerlukan tampilan keyboard kata kunci.



@bot.on_callback_query(filters.regex("cb_tambah_filter"))
async def cb_tambah_filter(client, callback_query):
    user_id = callback_query.from_user.id
    text = """
➕ **Tambah kata kunci**

👉🏻 Kirim kata kunci.

__kata kunci harus satu kata__
<u>contoh:</u> "payment" ✅
              "payment saya" ❌
"""
    buttons = [
        [
            InlineKeyboardButton("🔙 Kembali", callback_data="cb_set_filter"),          
        ]        
    ]    
    buttons_batal = [
        [
            InlineKeyboardButton("❌ Batalkan", callback_data="cb_set_filter"),          
        ]        
    ]  
     
    await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons_batal))
    try:
        s_text = await client.listen(chat_id=user_id, user_id=user_id)
    except meki:
        return

    if s_text.text:
        textlanjut = f"""
🔠 Kata kunci <b>{s_text.text}</b> berhasil dibuat

👉 __Silahkan atur.__
"""
        button_lanjut = [
            [
                InlineKeyboardButton("📨 Pesan", callback_data=f"cbaddpesanfilter {s_text.text}"),
                InlineKeyboardButton("👀 Lihat", callback_data=f"cblihatfilter {s_text.text}"),                
            ],          
            [
                InlineKeyboardButton("🗑️ Hapus", callback_data="cb_set_filter"),                 
            ],                           
            [
                InlineKeyboardButton("🔙 Kembali", callback_data="cb_set_filter"),          
                  
            ],                  
        ]        
        
        await client.send_message(user_id, textlanjut, reply_markup=InlineKeyboardMarkup(button_lanjut))
    else:
        await client.send_message(user_id, f"😤 Kata kunci tidak valid!", reply_markup=InlineKeyboardMarkup(buttons))


@bot.on_callback_query(filters.regex("cbaddpesanfilter"))
async def cb_add_pesan_filter(client, callback_query):
    user_id = callback_query.from_user.id
    query = callback_query.data.split()    
    text = """
**Kirim Pesan atau Media Sekarang**
__Format berikut dapat ditambahkan dalam teks dan akan digantikan dengan data pengguna:__

• `{mename}`: Nama anda.
• `{memention}`: Mention anda.
• `{name}`: Nama lengkap pengguna.
• `{username}`: Username pengguna. Jika tidak tersedia, mention pengguna.
• `{mention}`: Mention pengguna dengan nama depannya.
• `{id}`: ID pengguna.
• `{date}`: Tanggal.
• `{time}`: Waktu

Pesan bisa berupa Text, Media, atau Media dengan caption.

__Jenis media yang diizinkan: foto, video, berkas, stiker, GIF, audio, pesan suara, video bulat.__
"""
    button_edit = [
        [
            InlineKeyboardButton("🔙 Kembali", callback_data=f"aturkatakuncifilter {query[1]}")    
          
        ],          
        
    ]                
    await callback_query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(button_edit))
    try:
        p_media = await client.listen(chat_id=user_id, user_id=user_id)
    except meki:
        return
    await add_filter(user_id, query[1], query[1])
    if p_media.text:
        await add_text_filter(user_id, query[1], p_media.text.markdown)
    elif p_media.photo:
        await add_media_filter(user_id, query[1], p_media.photo.file_id)
    elif p_media.video:
        await add_media_filter(user_id, query[1], p_media.video.file_id)
    elif p_media.audio:
        await add_media_filter(user_id, query[1], p_media.audio.file_id)
    elif p_media.voice:
        await add_media_filter(user_id, query[1], p_media.voice.file_id)    
    elif p_media.sticker:
        await add_media_filter(user_id, query[1], p_media.sticker.file_id)   
    elif p_media.animation:
        await add_media_filter(user_id, query[1], p_media.animation.file_id)        
    elif p_media.video_note:
        await add_media_filter(user_id, query[1], p_media.video_note.file_id)        
    elif p_media.document:
        await add_media_filter(user_id, query[1], p_media.document.file_id)        
        
    if p_media.caption:
        await add_text_filter(user_id, query[1], p_media.caption.markdown)

        
    await client.send_message(callback_query.from_user.id, f"✅ Pesan di atur untuk kata kunci <b>{query [1]}</b>", reply_markup=InlineKeyboardMarkup (button_edit))
    



@bot.on_callback_query(filters.regex("aturkatakuncifilter"))
async def aturkatakuncifilter(client, callback_query):
    user_id = callback_query.from_user.id
    query = callback_query.data.split()
    await client.stop_listening(chat_id=user_id, user_id=user_id)
    textlanjut = f"""
🔠 Kata kunci <b>{query[1]}</b>

👉 __Silahkan atur.__
"""
    button_lanjut = [
        [
            InlineKeyboardButton("📨 Pesan", callback_data=f"cbaddpesanfilter {query[1]}"),
            InlineKeyboardButton("👀 Lihat", callback_data=f"cblihatfilter {query[1]}"),
          
        ], 
        [      
            InlineKeyboardButton("🗑️ Hapus", callback_data=f"cbrmpesanfilteryesno {query[1]}"),
        ],
        [
            InlineKeyboardButton("🔙 Kembali", callback_data="cb_set_filter"),          
          
        ],          
        
    ]           
    await callback_query.edit_message_text(text=textlanjut, reply_markup=InlineKeyboardMarkup(button_lanjut))



@bot.on_callback_query(filters.regex("cbrmpesanfilteryesno|cbrmpesanfiltergo"))
async def cb_remove_text_media_filter(client, callback_query):
    user_id = callback_query.from_user.id
    query = callback_query.data.split()
    button_yesno = [
        [
            InlineKeyboardButton("✅ Ya", callback_data=f"cbrmpesanfiltergo {query[1]}"),            
            InlineKeyboardButton("❌ Tidak", callback_data=f"aturkatakuncifilter {query[1]}"),
        ],                 
        
    ]


    if query[0] == "cbrmpesanfilteryesno":
        text = f"🗑️ **Hapus kata kunci {query[1]}**\nAnda yakin ingin menghapus?"
        return await callback_query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(button_yesno))        
    elif query[0] == "cbrmpesanfiltergo":
        await rm_media_filter(user_id, query[1])
        await rm_text_filter(user_id, query[1])  
        await rm_filter(user_id, query[1])        
        datakunci = await all_filter(user_id)
        textlanjut = "**📊 Daftar kata kunci**"
        button_lanjut = generate_keyboard(list(datakunci))        
        await callback_query.answer(f"✅ Kata kunci {query[1]} berhasil dihapus", show_alert=False)
        await callback_query.edit_message_text(text=textlanjut, reply_markup=InlineKeyboardMarkup(button_lanjut))
    

@bot.on_callback_query(filters.regex("cblihatfilter"))
async def see_(client, callback_query):
    user_id = callback_query.from_user.id
    query = callback_query.data.split()
    db_get = await get_filter(user_id, query[1])
    textlanjut = f"""
🔠 Kata kunci <b>{query[1]}</b>

👉 __Silahkan atur.__
"""
    button_lanjut = [
        [
            InlineKeyboardButton("📨 Pesan", callback_data=f"cbaddpesanfilter {query[1]}"),
            InlineKeyboardButton("👀 Lihat", callback_data=f"cblihatfilter {query[1]}"),
          
        ], 
        [      
            InlineKeyboardButton("🗑️ Hapus", callback_data=f"cbrmpesanfilteryesno {query[1]}"),
        ],
        [
            InlineKeyboardButton("🔙 Kembali", callback_data="cb_set_filter"),          
          
        ],          
        
    ]         
    
    if not db_get:
        return await callback_query.answer("Pesan belum diatur!", show_alert=True)
    else: 
        await callback_query.message.delete()
        await client.send_message(user_id, "👀")        
        db_media= await get_media_filter(user_id, query[1])
        db_caption = await get_text_filter(user_id, query[1])

        await sleep(2)
        if db_caption and not db_media:
            await client.send_message(user_id, db_caption)
        elif db_caption and db_media:
            await client.send_cached_media(user_id, db_media, caption=db_caption)
        elif db_media and not db_caption:
            await client.send_cached_media(user_id, db_media)

        await client.send_message(user_id, textlanjut, reply_markup=InlineKeyboardMarkup(button_lanjut))







# notes
@bot.on_callback_query(filters.regex("cb_set_notes"))
async def cb_set_notes(client, callback_query):
    user_id = callback_query.from_user.id    
    await client.stop_listening(chat_id=user_id, user_id=user_id)
    datakunci = await all_notes(user_id)
    
    if not datakunci:
        text = "🤷 Kamu belum memiliki nama catatan silahkan buat!"
        buttons = [
            [InlineKeyboardButton("➕ Buat catatan", callback_data="cb_tambah_notes")],
            [InlineKeyboardButton("🔙 Kembali", callback_data="setting")]
        ]
        return await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))
    
    text = "**📊 Daftar nama catatan**\n\n• `/get nama_kunci` - mengirim catatan\n• `/listnote` - List catatan"
    buttons = generate_keyboard_notes(list(datakunci))
    
    await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))


def generate_keyboard_notes(datakunci, page=1):
    # Fungsi untuk membuat keyboard sesuai dengan jumlah kata kunci yang dimiliki pengguna
    buttons = []
    buttons.append([InlineKeyboardButton("➕ Tambah nama catatan", callback_data="cb_tambah_notes")])
                   
    start_index = (page - 1) * 10
    end_index = min(page * 10, len(datakunci))
    for i in range(start_index, end_index, 2):
        row = [InlineKeyboardButton(datakunci[i], callback_data=f"aturkatakuncinotes {datakunci[i]}")]
        if i + 1 < end_index:
            row.append(InlineKeyboardButton(datakunci[i + 1], callback_data=f"aturkatakuncinotes {datakunci[i + 1]}"))
        buttons.append(row)
    
    if len(datakunci) <= 10:
        buttons.append([InlineKeyboardButton("🔙 Kembali", callback_data="setting")])
    else:
        total_pages = (len(datakunci) - 1) // 10 + 1
        
        if total_pages == 1:
            buttons.append([InlineKeyboardButton("🔙 Kembali", callback_data="setting")])
        elif total_pages == 2:
            if page == 1:
                buttons.append([
                    InlineKeyboardButton(f"{page}/{total_pages}", callback_data="cb_notes_current"),
                    InlineKeyboardButton("▶️", callback_data=f"cb_notes_next {page}"),
                    InlineKeyboardButton("⏭️", callback_data="cb_notes_last"),
                ])
            else:
                buttons.append([
                    InlineKeyboardButton("⏮️", callback_data="cb_notes_first"),
                    InlineKeyboardButton("◀️", callback_data=f"cb_notes_previous {page}"),
                    InlineKeyboardButton(f"{page}/{total_pages}", callback_data="cb_notes_current"),                    
                ])           
        else:
            if page == 1:
                buttons.append([
                    InlineKeyboardButton(f"{page}/{total_pages}", callback_data="cb_notes_current"),
                    InlineKeyboardButton("▶️", callback_data=f"cb_notes_next {page}"),
                    InlineKeyboardButton("⏭️", callback_data="cb_notes_last"),
                ])
            elif page <= total_pages - 1:
                buttons.append([
                    InlineKeyboardButton("⏮️", callback_data="cb_notes_first"),
                    InlineKeyboardButton("◀️", callback_data=f"cb_notes_previous {page}"),
                    InlineKeyboardButton(f"{page}/{total_pages}", callback_data="cb_notes_current"),
                    InlineKeyboardButton("▶️", callback_data=f"cb_notes_next {page}"),
                    InlineKeyboardButton("⏭️", callback_data="cb_notes_last"),
                ])
            else:
                buttons.append([
                    InlineKeyboardButton("⏮️", callback_data="cb_notes_first"),
                    InlineKeyboardButton("◀️", callback_data=f"cb_notes_previous {page}"),
                    InlineKeyboardButton(f"{page}/{total_pages}", callback_data="cb_notes_current"),                    
                ])
                                          
        buttons.append([InlineKeyboardButton("🔙 Kembali", callback_data="setting")])
                       
    return buttons


# Fungsi untuk menambahkan navigasi untuk keyboard jika jumlah kata kunci lebih dari 10
@bot.on_callback_query(filters.regex("cb_notes_first|cb_notes_previous|cb_notes_current|cb_notes_next|cb_notes_last"))
async def cb_notes_navigation(client, callback_query):
    user_id = callback_query.from_user.id
    datakunci = await all_notes(user_id)
    query = callback_query.data.split()
    if not datakunci:
        text = "🤷 Kamu belum memiliki nama catatan, silahkan buat!"
        buttons = [
            [InlineKeyboardButton("➕ Buat catatan", callback_data="cb_tambah_notes")],
            [InlineKeyboardButton("🔙 Kembali", callback_data="setting")]
        ]
        return await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))
    
    # Parse the callback data
    action = query[0]
    
    if action == "cb_notes_next":
        await handle_next_page_notes(callback_query, datakunci, query[1])
    elif action == "cb_notes_previous":
        await handle_previous_page_notes(callback_query, datakunci, query[1])
    elif action == "cb_notes_first":
        await handle_first_page_notes(callback_query, datakunci)
    elif action == "cb_notes_last":
        await handle_last_page_notes(callback_query, datakunci)
    else:
        # Invalid action, do nothing
        await callback_query.answer()

async def handle_next_page_notes(callback_query, datakunci, page):
    user_id = callback_query.from_user.id
    pageu = int(page) + 1
    buttons = generate_keyboard_notes(list(datakunci), pageu)
    
    await callback_query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))
    await callback_query.answer()

async def handle_previous_page_notes(callback_query, datakunci, page):
    user_id = callback_query.from_user.id
    pageu = int(page) - 1    
    buttons = generate_keyboard_notes(list(datakunci), pageu)
    
    await callback_query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))
    await callback_query.answer()
    


async def handle_first_page_notes(callback_query, datakunci):
    user_id = callback_query.from_user.id
    buttons = generate_keyboard_notes(list(datakunci), 1)
    
    await callback_query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))
    await callback_query.answer()

async def handle_last_page_notes(callback_query, datakunci):
    user_id = callback_query.from_user.id
    total_pages = (len(datakunci) - 1) // 10 + 1
    buttons = generate_keyboard_notes(list(datakunci), total_pages)
    
    await callback_query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))
    await callback_query.answer()
                           

# Gunakan fungsi ini di tempat Anda memerlukan tampilan keyboard kata kunci.



@bot.on_callback_query(filters.regex("cb_tambah_notes"))
async def cb_tambah_notes(client, callback_query):
    user_id = callback_query.from_user.id
    text = """
➕ **Tambah nama catatan**

👉🏻 Kirim nama catatan.

__nama catatan harus satu kata__
<u>contoh:</u> "payment" ✅
              "payment saya" ❌
"""
    buttons = [
        [
            InlineKeyboardButton("🔙 Kembali", callback_data="cb_set_notes"),          
        ]        
    ]    
    buttons_batal = [
        [
            InlineKeyboardButton("❌ Batalkan", callback_data="cb_set_notes"),          
        ]        
    ]  
     
    await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons_batal))
    try:
        s_text = await client.listen(chat_id=user_id, user_id=user_id)
    except meki:
        return

    if s_text.text:
        textlanjut = f"""
🔠 Nama catatan <b>{s_text.text}</b> berhasil dibuat

👉 __Silahkan atur.__
"""
        button_lanjut = [
            [
                InlineKeyboardButton("📨 Pesan", callback_data=f"cbaddpesannotes {s_text.text}"),
                InlineKeyboardButton("👀 Lihat", callback_data=f"cblihatnotes {s_text.text}"),                
            ],          
            [
                InlineKeyboardButton("🗑️ Hapus", callback_data="cb_set_notes"),                 
            ],                           
            [
                InlineKeyboardButton("🔙 Kembali", callback_data="cb_set_notes"),          
                  
            ],                  
        ]        
        
        await client.send_message(user_id, textlanjut, reply_markup=InlineKeyboardMarkup(button_lanjut))
    else:
        await client.send_message(user_id, f"😤 Nama catatan tidak valid!", reply_markup=InlineKeyboardMarkup(buttons))


@bot.on_callback_query(filters.regex("cbaddpesannotes"))
async def cb_add_pesan_notes(client, callback_query):
    user_id = callback_query.from_user.id
    query = callback_query.data.split()    
    text = """
**Kirim Pesan atau Media Sekarang**
__Format berikut dapat ditambahkan dalam teks dan akan digantikan dengan data pengguna:__

• `{mename}`: Nama anda.
• `{memention}`: Mention anda.
• `{name}`: Nama lengkap pengguna.
• `{username}`: Username pengguna. Jika tidak tersedia, mention pengguna.
• `{mention}`: Mention pengguna dengan nama depannya.
• `{id}`: ID pengguna.
• `{date}`: Tanggal.
• `{time}`: Waktu.

Pesan bisa berupa Text, Media, atau Media dengan caption.

__Jenis media yang diizinkan: foto, video, berkas, stiker, GIF, audio, pesan suara, video bulat.__
"""
    button_edit = [
        [
            InlineKeyboardButton("🔙 Kembali", callback_data=f"aturkatakuncinotes {query[1]}")    
          
        ],          
        
    ]                
    await callback_query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(button_edit))
    try:
        p_media = await client.listen(chat_id=user_id, user_id=user_id)
    except meki:
        return
    await add_notes(user_id, query[1], query[1])
    if p_media.text:
        await add_text_notes(user_id, query[1], p_media.text.markdown)
    elif p_media.photo:
        await add_media_notes(user_id, query[1], p_media.photo.file_id)
    elif p_media.video:
        await add_media_notes(user_id, query[1], p_media.video.file_id)
    elif p_media.audio:
        await add_media_notes(user_id, query[1], p_media.audio.file_id)
    elif p_media.voice:
        await add_media_notes(user_id, query[1], p_media.voice.file_id)    
    elif p_media.sticker:
        await add_media_notes(user_id, query[1], p_media.sticker.file_id)   
    elif p_media.animation:
        await add_media_notes(user_id, query[1], p_media.animation.file_id)        
    elif p_media.video_note:
        await add_media_notes(user_id, query[1], p_media.video_note.file_id)        
    elif p_media.document:
        await add_media_notes(user_id, query[1], p_media.document.file_id)        
        
    if p_media.caption:
        await add_text_notes(user_id, query[1], p_media.caption.markdown)

        
    await client.send_message(callback_query.from_user.id, f"✅ Pesan di atur untuk nama catatan <b>{query [1]}</b>", reply_markup=InlineKeyboardMarkup (button_edit))
    



@bot.on_callback_query(filters.regex("aturkatakuncinotes"))
async def aturkatakuncinotes(client, callback_query):
    user_id = callback_query.from_user.id
    query = callback_query.data.split()
    await client.stop_listening(chat_id=user_id, user_id=user_id)
    textlanjut = f"""
🔠 Nama catatan <b>{query[1]}</b>

👉 __Silahkan atur.__
"""
    button_lanjut = [
        [
            InlineKeyboardButton("📨 Pesan", callback_data=f"cbaddpesannotes{query[1]}"),
            InlineKeyboardButton("👀 Lihat", callback_data=f"cblihatnotes {query[1]}"),
          
        ], 
        [      
            InlineKeyboardButton("🗑️ Hapus", callback_data=f"cbrmpesannotesyesno {query[1]}"),
        ],
        [
            InlineKeyboardButton("🔙 Kembali", callback_data="cb_set_notes"),          
          
        ],          
        
    ]           
    await callback_query.edit_message_text(text=textlanjut, reply_markup=InlineKeyboardMarkup(button_lanjut))



@bot.on_callback_query(filters.regex("cbrmpesannotesyesno|cbrmpesannotesgo"))
async def cb_remove_text_media_notes(client, callback_query):
    user_id = callback_query.from_user.id
    query = callback_query.data.split()
    button_yesno = [
        [
            InlineKeyboardButton("✅ Ya", callback_data=f"cbrmpesannotesgo {query[1]}"),            
            InlineKeyboardButton("❌ Tidak", callback_data=f"aturkatakuncinotes {query[1]}"),
        ],                 
        
    ]


    if query[0] == "cbrmpesannotesyesno":
        text = f"🗑️ **Hapus nama catatan {query[1]}**\nAnda yakin ingin menghapus?"
        return await callback_query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(button_yesno))        
    elif query[0] == "cbrmpesannotesgo":
        await rm_media_notes(user_id, query[1])
        await rm_text_notes(user_id, query[1])  
        await rm_notes(user_id, query[1])        
        datakunci = await all_notes(user_id)
        textlanjut = "**📊 Daftar nama catatan**"
        button_lanjut = generate_keyboard_notes(list(datakunci))        
        await callback_query.answer(f"✅ Nama catatan {query[1]} berhasil dihapus", show_alert=False)
        await callback_query.edit_message_text(text=textlanjut, reply_markup=InlineKeyboardMarkup(button_lanjut))
    

@bot.on_callback_query(filters.regex("cblihatnotes"))
async def see_notes(client, callback_query):
    user_id = callback_query.from_user.id
    query = callback_query.data.split()
    db_get = await get_notes(user_id, query[1])
    textlanjut = f"""
🔠 Nama catatan <b>{query[1]}</b>

👉 __Silahkan atur.__
"""
    button_lanjut = [
        [
            InlineKeyboardButton("📨 Pesan", callback_data=f"cbaddpesannotes {query[1]}"),
            InlineKeyboardButton("👀 Lihat", callback_data=f"cblihatnotes{query[1]}"),
          
        ], 
        [      
            InlineKeyboardButton("🗑️ Hapus", callback_data=f"cbrmpesannotesyesno {query[1]}"),
        ],
        [
            InlineKeyboardButton("🔙 Kembali", callback_data="cb_set_notes"),          
          
        ],          
        
    ]         
    
    if not db_get:
        return await callback_query.answer("Pesan belum diatur!", show_alert=True)
    else: 
        await callback_query.message.delete()
        await client.send_message(user_id, "👀")        
        db_media= await get_media_notes(user_id, query[1])
        db_caption = await get_text_notes(user_id, query[1])

        await sleep(2)
        if db_caption and not db_media:
            await client.send_message(user_id, db_caption)
        elif db_caption and db_media:
            await client.send_cached_media(user_id, db_media, caption=db_caption)
        elif db_media and not db_caption:
            await client.send_cached_media(user_id, db_media)

        await client.send_message(user_id, textlanjut, reply_markup=InlineKeyboardMarkup(button_lanjut))
    

#welcome
@bot.on_callback_query(filters.regex("cb_set_welcome"))
async def cb_set_welcome(client, callback_query):
    user_id = callback_query.from_user.id  
    await client.stop_listening(chat_id=user_id, user_id=user_id)
    status = await info_wlcm(user_id)
    if status == "on":
        statustext = "On ✅"
    else:
        statustext = "Off ❌"
        
    text_db = await get_wlcm_text(user_id)
    if not text_db:
        text = f"**Status:** {statustext}\n\n**Text Welcome:**\n" + "`Welcome {mention} 👋🏻\n\nHow are you today?, Hope everything will be fine.`"
    else:
        text = f"**Status:** {statustext}\n\n**Text Welcome:**\n" + f"`{text_db}`"
        
    buttons = [
        [
            InlineKeyboardButton("🚦 On/Off", callback_data="cb_status_welcometext"),          
        ],                
        [
            InlineKeyboardButton("↪️ Set ke Default", callback_data="cb_default_welcometext"),                            
            InlineKeyboardButton("✏️ Set Welcome text", callback_data="cb_tambah_welcometext"),          
        ],          
        [
            InlineKeyboardButton("🔙 Kembali", callback_data="setting"),             
        ]  
    ]
    await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))


    
@bot.on_callback_query(filters.regex("cb_tambah_welcometext|cb_default_welcometext"))
async def cb_tambah_wlcmtext(client, callback_query):
    user_id = callback_query.from_user.id
    query = callback_query.data.split()
    if query[0] == "cb_tambah_welcometext":    
        text = """
**Kirimkan Pesan**
__Format berikut dapat ditambahkan dalam teks dan akan digantikan dengan data pengguna:__

• `{mename}`: Nama anda.
• `{memention}`: Mention anda.
• `{name}`: Nama lengkap pengguna.
• `{username}`: Username pengguna. Jika tidak tersedia, mention pengguna.
• `{mention}`: Mention pengguna dengan nama depannya.
• `{id}`: ID pengguna.
• `{date}`: Tanggal.
• `{time}`: Waktu.
"""
        buttons = [  
            [
                InlineKeyboardButton("🔙 Kembali", callback_data="cb_set_welcometext"),          
            ]         
        ]    
        buttons_batal = [      
            [            
                InlineKeyboardButton("❌ Batalkan", callback_data="cb_set_welcometext"),          
            ]        
        ]             
        await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons_batal))
        try:
            s_text = await client.listen(chat_id=user_id, user_id=user_id)
        except meki:
            return
            
        if s_text.text:
            await add_wlcm_text(user_id, s_text.text.markdown)
            await client.send_message(user_id, "✅ **Text Welcome** berhasil diset!", reply_markup=InlineKeyboardMarkup(buttons))            
        else:
            await client.send_message(user_id, "😤 Format Text tidak valid!", reply_markup=InlineKeyboardMarkup(buttons_batal))
            
    elif query[0] == "cb_default_welcometext":
        text = "↪️ **Text Welcome** berhasil di set ke Default"
        buttons = [  
            [
                InlineKeyboardButton("🔙 Kembali", callback_data="cb_set_welcometext"),          
            ]         
        ]  
        ada = await get_wlcm_text(user_id)
        if ada:
            await rm_wlcm_text(user_id)
            await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))
        else:
            await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@bot.on_callback_query(filters.regex("cb_status_welcometext"))
async def cb_status_welcometext(client, callback_query):
    text = f"""
Silahkan atur!
"""
    buttons = [
        [
            InlineKeyboardButton("✅ Hidupkan", callback_data="wlcm_true"),
            InlineKeyboardButton("❌ Matikan", callback_data="wlcm_false"),            
        ],             
        [
            InlineKeyboardButton("🔙 Kembali", callback_data="cb_set_welcome"),          
        ]        
    ]    
    await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@bot.on_callback_query(filters.regex("wlcm_true|wlcm_false"))
async def wlcm_true_false(client, callback_query):
    user_id = callback_query.from_user.id
    query = callback_query.data.split()  

    buttons = [
        [
            InlineKeyboardButton("🚦 On/Off", callback_data="cb_status_welcometext"),          
        ],                
        [
            InlineKeyboardButton("↪️ Set ke Default", callback_data="cb_default_welcometext"),                            
            InlineKeyboardButton("✏️ Set Welcome text", callback_data="cb_tambah_welcometext"),          
        ],          
        [
            InlineKeyboardButton("🔙 Kembali", callback_data="setting"),             
        ]  
    ]

    
    if query[0] == "wlcm_true":
        await set_wlcm(user_id, "on")
        await add_client_wlcm(user_id)
        text = f"""
✅ Welcome berhasil dihidupkan
"""
        statustext = "On ✅"  
        text_db = await get_wlcm_text(user_id)
        if not text_db:
            textawal = f"**Status:** {statustext}\n\n**Text Welcome:**\n" + "`Welcome {mention} 👋🏻\n\nHow are you today?, Hope everything will be fine.`"
        else:
            textawal = f"**Status:** {statustext}\n\n**Text Welcome:**\n" + f"`{text_db}`"
        
    elif query[0] == "wlcm_false":
        await set_wlcm(user_id, "off")
        text = f"""
❌ Welcome berhasil dimatikan
"""        
        statustext = "Off ❌"  
        text_db = await get_wlcm_text(user_id)
        if not text_db:
            textawal = f"**Status:** {statustext}\n\n**Text Welcome:**\n" + "`Welcome {mention} 👋🏻\n\nHow are you today?, Hope everything will be fine.`"
        else:
            textawal = f"**Status:** {statustext}\n\n**Text Welcome:**\n" + f"`{text_db}`"
                
    await callback_query.answer(text)        
    await callback_query.edit_message_text(textawal, reply_markup=InlineKeyboardMarkup(buttons))


