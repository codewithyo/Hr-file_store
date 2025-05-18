# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on Telegram @KingVJ01

import sys
import glob
import importlib.util
import asyncio
import logging
import logging.config
from pathlib import Path
from datetime import date, datetime

import pytz
from aiohttp import web
from pyrogram import idle
from pyrogram.raw.all import layer

from config import LOG_CHANNEL, ON_HEROKU, CLONE_MODE, PORT
from Script import script
from TechVJ.server import web_server
from TechVJ.bot import StreamBot
from TechVJ.utils.keepalive import ping_server
from TechVJ.bot.clients import initialize_clients
from plugins.clone import restart_bots

# Setup logging
try:
    logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
except Exception as e:
    logging.basicConfig(level=logging.INFO)
    logging.error("Failed to load logging.conf: %s", e)

logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

PLUGIN_PATH = "plugins/*.py"

async def load_plugins():
    """Dynamically import all plugins in plugins/"""
    for file in glob.glob(PLUGIN_PATH):
        plugin_path = Path(file)
        plugin_name = plugin_path.stem
        import_path = f"plugins.{plugin_name}"
        try:
            spec = importlib.util.spec_from_file_location(import_path, plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            sys.modules[import_path] = module
            print(f"Tech VJ Imported => {plugin_name}")
        except Exception as e:
            logging.error(f"Failed to import {plugin_name}: {e}")

async def start():
    print('\nInitializing Tech VJ Bot...')
    await StreamBot.start()

    await initialize_clients()
    await load_plugins()

    if ON_HEROKU:
        asyncio.create_task(ping_server())

    me = await StreamBot.get_me()
    StreamBot.username = me.username

    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    time_str = now.strftime("%H:%M:%S %p")

    await StreamBot.send_message(
        chat_id=LOG_CHANNEL,
        text=script.RESTART_TXT.format(today, time_str)
    )

    app_runner = web.AppRunner(await web_server())
    await app_runner.setup()
    await web.TCPSite(app_runner, "0.0.0.0", PORT).start()

    if CLONE_MODE:
        await restart_bots()

    print("Bot Started Powered By @VJ_Botz")
    await idle()

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(start())
    except KeyboardInterrupt:
        logging.info('Service Stopped. Bye!')
