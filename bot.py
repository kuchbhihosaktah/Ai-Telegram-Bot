import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from diffusers import StableDiffusionPipeline
from opensora.models import create_model
from opensora.pipelines import TextToVideoPipeline
import torch

# =========================
# SET YOUR BOT TOKEN HERE
# =========================
TOKEN = "7743425789:AAHv3U-QhDB4KX0JCFVoydBANaFOdz39k38"

# =========================
# IMAGE GENERATOR (Stable Diffusion)
# =========================
device = "cuda" if torch.cuda.is_available() else "cpu"
sd_pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5").to(device)

def generate_image(prompt):
    image = sd_pipe(prompt).images[0]
    path = "output.png"
    image.save(path)
    return path

# =========================
# VIDEO GENERATOR (Open-Sora)
# =========================
model = create_model("weights")
video_pipe = TextToVideoPipeline(model)

def generate_video(prompt):
    video = video_pipe(prompt, num_frames=48, fps=24, height=512, width=512)
    path = "output.mp4"
    video.save(path)
    return path

# =========================
# TELEGRAM HANDLERS
# =========================
def start(update: Update, context: CallbackContext):
    update.message.reply_text("🤖 Welcome! Use /img <prompt> for images and /video <prompt> for videos.")

def img(update: Update, context: CallbackContext):
    prompt = " ".join(context.args)
    if not prompt:
        update.message.reply_text("❌ Please provide a prompt. Example: `/img a cute cat`")
        return
    update.message.reply_text("⏳ Generating image...")
    path = generate_image(prompt)
    update.message.reply_photo(photo=open(path, "rb"))

def video(update: Update, context: CallbackContext):
    prompt = " ".join(context.args)
    if not prompt:
        update.message.reply_text("❌ Please provide a prompt. Example: `/video flying car in future city`")
        return
    update.message.reply_text("⏳ Generating video... this may take a few minutes.")
    path = generate_video(prompt)
    update.message.reply_video(video=open(path, "rb"))

# =========================
# MAIN
# =========================
def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("img", img))
    dp.add_handler(CommandHandler("video", video))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
