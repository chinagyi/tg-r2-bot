import os
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
WORKER_URL = os.environ.get("WORKER_URL") 

bot = Client("r2_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.private & (filters.video | filters.document))
async def upload_to_r2(client: Client, message: Message):
    msg = await message.reply_text("⏳ ဗီဒီယိုကို Cloudflare R2 ဆီ တိုက်ရိုက် တင်နေပါပြီ၊ ခဏစောင့်ပါ...")
    
    file = message.video or message.document
    file_id = file.file_id
    file_info = await client.get_media_file_path(file_id)
    
    tg_file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info}"
    file_name = getattr(file, "file_name", f"video_{message.id}.mp4")

    payload_url = f"{WORKER_URL}?tg_url={tg_file_url}&filename={file_name}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(payload_url) as resp:
            if resp.status == 200:
                data = await resp.json()
                playback_url = f"https://stream.joegyi.shop/{data['filename']}"
                await msg.edit_text(
                    f"✅ **R2 ဆီသို့ အောင်မြင်စွာ တင်ပြီးပါပြီ!**\n\n🔗 **Stream Link:**\n`{playback_url}`",
                    disable_web_page_preview=True
                )
            else:
                await msg.edit_text("❌ R2 ဆီ တင်ရာတွင် Error ဖြစ်သွားပါသည်။")

bot.run()
