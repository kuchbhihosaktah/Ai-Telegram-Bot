from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import requests
from io import BytesIO
from PIL import Image
import subprocess
import os

# =========================
# EDIT ONLY THESE TWO LINES
TOKEN = "8386912250:AAHWppIHrXHpG8lQuZ7l3xkO4AjMUkIkhZg"       # Telegram Bot Token
HF_TOKEN = "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" # Hugging Face Token
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! Send me a prompt, I will generate an AI image and make a 5-sec video 🎬"
    )

def generate_image(prompt):
    url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": prompt}
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        return BytesIO(response.content)
    else:
        return None

def image_to_video(image_data, duration=5):
    # Save AI image
    img = Image.open(image_data).convert("RGB")
    img_path = "temp.jpg"
    video_path = "temp.mp4"
    img.save(img_path)

    # Use FFmpeg (super fast)
    cmd = [
        "ffmpeg",
        "-loop", "1",
        "-i", img_path,
        "-c:v", "libx264",
        "-t", str(duration),
        "-pix_fmt", "yuv420p",
        "-y", video_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    with open(video_path, "rb") as f:
        video_bytes = BytesIO(f.read())
    video_bytes.seek(0)

    # Clean up
    os.remove(img_path)
    os.remove(video_path)

    return video_bytes

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text
    await update.message.reply_text("Generating image... ⏳")
    
    image_data = generate_image(prompt)
    if image_data:
        await update.message.reply_text("Converting image to 5-sec video... 🎬")
        video_data = image_to_video(image_data)
        await update.message.reply_video(video=video_data)
    else:
        await update.message.reply_text("❌ Failed to generate image. Try again!")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Bot is running...")
    app.run_polling()
