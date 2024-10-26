import os
import discord
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import imageio
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_USER_ID = int(os.getenv("DISCORD_USER_ID"))

# Telegram Bot Setup
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправьте мне гифку, и я отправлю её в Discord.")

async def convert_video_to_gif(video_path):
    reader = imageio.get_reader(video_path)
    gif_path = video_path.replace(".mp4", ".gif")
    writer = imageio.get_writer(gif_path, fps=reader.get_meta_data()['fps'])
    for frame in reader:
        writer.append_data(frame)
    writer.close()
    return gif_path

async def handle_gif(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.animation:
        gif_file = await update.message.animation.get_file()
        video_path = await gif_file.download_to_drive()
        gif_path = await convert_video_to_gif(str(video_path))
        await send_gif_to_discord(gif_path)
        os.remove(video_path)
        os.remove(gif_path)
        await update.message.reply_text("Гифка отправлена в Discord!")

async def send_gif_to_discord(gif_path):
    client = discord.Client(intents=discord.Intents.default())

    @client.event
    async def on_ready():
        user = await client.fetch_user(DISCORD_USER_ID)
        await user.send(file=discord.File(gif_path))
        await client.close()

    await client.start(DISCORD_TOKEN)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ANIMATION, handle_gif))
    app.run_polling()

if __name__ == "__main__":
    main()
