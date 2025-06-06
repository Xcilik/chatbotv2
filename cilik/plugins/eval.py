import sys
import traceback
import asyncio
import os
import subprocess
from io import BytesIO, StringIO
from os import execvp
from sys import executable
from subprocess import Popen, PIPE, TimeoutExpired
from pyrogram import filters
from pyrogram.errors import FloodWait
from cilik.database import get_served_users, remove_date_end, add_date_end, remove_prem
from cilik import bot
from config import *
from datetime import datetime, timedelta
from pytz import timezone



async def aexec(code, client, message):
    exec(
        "async def __aexec(client, message): "
        + "\n chat = message.chat"
        + "\n r = message.reply_to_message"
        + "\n c = client"
        + "\n m = message"
        + "\n p = print"
        + "".join(f"\n {l_}" for l_ in code.split("\n"))
    )
    return await locals()["__aexec"](client, message)


def rest():
    execvp(executable, [executable, "-m", "cilik"])




@bot.on_message(filters.command("restart") & filters.user(OWNER))
async def _(client, message):    
    await message.reply("✅ Bot sedang di restart silahkan tunggu...")    
    rest()


@bot.on_message(filters.command("update") & filters.user(OWNER))
async def upd(client, message):
    try:
        out = subprocess.check_output(["git", "pull"]).decode("UTF-8")
        if "Already up to date." in str(out):
            return await message.reply_text("Its already up-to date!")
        await message.reply_text(f"```{out}```")
    except Exception as e:
        return await message.reply_text(str(e))
    m = await message.reply_text("**Updated with default branch, restarting now.**")
    rest()


@bot.on_message(filters.user(OWNER) & filters.command("eval"))
async def _(client, message):
    if len(message.command) < 2:
        return await message.reply("Silahkan kombinasikan dengan kode")
    cmd = message.text.split(None, maxsplit=1)[1]        
    status_message = await message.reply_text("Processing ...")
    reply_to_ = message.reply_to_message if message.reply_to_message else message
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    redirected_error = sys.stderr = StringIO()
    stdout, stderr, exc = None, None, None

    try:
        await aexec(cmd, client, message)
    except Exception:
        exc = traceback.format_exc()

    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr

    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"
        
    final_output = f"{evaluation.strip()}"

    if len(final_output) > 4096:
        with BytesIO(str.encode(final_output)) as out_file:
            out_file.name = "eval.text"
            await reply_to_.reply_document(
                document=out_file,
                caption=cmd[: 4096 // 4 - 1],
                disable_notification=True,
                quote=True,
            )
    else:
        await reply_to_.reply_text(final_output, quote=True)
    await status_message.delete()



@bot.on_message(filters.user(OWNER) & filters.command(["br", "broadcast"]))
async def bruser_message(client, message):
    if message.reply_to_message:
        x = message.reply_to_message.id
        y = message.chat.id
    else:
        if len(message.command) < 2:
            return await message.reply_text("text or reply to message")
        query = message.text.split(None, 1)[1]
    susr = 0
    served_users = []
    susers = await get_served_users()
    for user in susers:
        served_users.append(int(user["user_id"]))
    for i in served_users:
        try:
            m = (
                await message.reply_to_message.copy(i)
                if message.reply_to_message
                else await bot.send_message(i, text=query)
            )
            susr += 1
        except FloodWait as e:
            flood_time = int(e.value)
            if flood_time > 200:
                continue
            await asyncio.sleep(flood_time)
        except Exception:
            pass
    try:
        await message.reply_text("Broadcast Success to {} user".format(susr))
    except:
        pass

@bot.on_message(filters.command("setexp") & filters.user(OWNER))
async def abis_handler(client, message):
    if len(message.command) < 3:
        return await message.reply_text(
            "Usage:\n/setexp user_id value"
        )

    user_id = int(message.command[1])
    value = message.command[2]
    if value == "now": 
        time = datetime.now(timezone("Asia/Jakarta"))
    else:
        time = datetime.now(timezone("Asia/Jakarta")) + timedelta(int(value))

    try:
        await add_date_end(user_id, time)
        await message.reply(f"{user_id} - {time}")
    except Exception as e:
        await message.reply(e)
        
@bot.on_message(filters.command("dead") & filters.user(OWNER))
async def dead(client, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "Usage:\n/dead user_id"
        )

    user_id = int(message.command[1])
    try:
        await remove_prem(user_id)
        await remove_date_end(user_id)
        await message.reply(f"Success dead {user_id}")
    except Exception as e:
        await message.reply(e)
            