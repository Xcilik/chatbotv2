import importlib
import asyncio
from pyrogram import idle
from datetime import datetime, timedelta
from pytz import timezone

from cilik.plugins import loadModule
from cilik.database import get_client_wlcm, get_user_wlcm, clear_user_wlcm, get_prem, remove_prem, get_date_end, remove_date_end
from cilik import *

LOOP = asyncio.get_event_loop()

async def clear_welcome():
    for user_id in await get_client_wlcm():
        anu = await get_user_wlcm(user_id)
        if anu:
            await clear_user_wlcm(user_id)



async def expired_user():
    now = datetime.now(timezone("Asia/Jakarta"))

    for user_id in await get_prem():
        exp_str = await get_date_end(user_id)
        if not exp_str:
            continue

        # Ubah exp_str ke timezone-aware jika belum
        if exp_str.tzinfo is None:
            exp_str = timezone("Asia/Jakarta").localize(exp_str)

        if now < exp_str:
            continue

        try:
            await bot.send_message(user_id, f"⛔️ Chat Bot kamu sudah expired.")
        except:
            pass

        await remove_date_end(user_id)
        await remove_prem(user_id)

        LOGGER("Info").info(f"Chatbot {user_id} expired & dihapus.")



async def auto_reset():
    now = datetime.now(timezone("Asia/Jakarta"))
    target_time = now.replace(hour=19, minute=47, second=0, microsecond=0)
    if now >= target_time:
        target_time += timedelta(days=1)
    time_until_target = target_time - now
    await asyncio.sleep(time_until_target.total_seconds())
    await clear_welcome()
    await expired_user()    



async def loadPlugins():
    modules = loadModule()
    for mod in modules:
        importlib.reload(importlib.import_module(f"cilik.plugins.{mod}"))
    LOGGER("Info").info("✅ Plugins imported")


async def main():
    await bot.start()
    LOGGER("Info").info(f"✅ Bot Active | {bot.me.username}")
    asyncio.gather(auto_reset())
    await asyncio.gather(loadPlugins(), idle())


if __name__ == "__main__":
    LOOP.run_until_complete(main())
