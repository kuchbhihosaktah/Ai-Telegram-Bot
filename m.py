import os, subprocess, shlex, time, logging
from huggingface_hub import snapshot_download
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# ============================================================
# CONFIGURATION
# ============================================================

TELEGRAM_TOKEN = "8386912250:AAHWppIHrXHpG8lQuZ7l3xkO4AjMUkIkhZg"  # replace with your token
repo_id = "LanguageBind/Open-Sora-Plan-v1.3.0"
MODEL_DIR = "/content/open_sora_model"
OUT_DIR = "/content/outputs"
os.makedirs(OUT_DIR, exist_ok=True)

# ============================================================
# STEP 1: Download Model
# ============================================================
print("⬇️ Downloading model... please wait")
snapshot_download(
    repo_id=repo_id,
    local_dir=MODEL_DIR,
    repo_type="model",
    allow_patterns=["*.safetensors","*.json","*.txt"]
)
print("✅ Model ready at:", MODEL_DIR)

# ============================================================
# STEP 2: Video Generation Function
# ============================================================
def run_opensora_text2video(prompt, duration_seconds=4, out_fname="out.mp4"):
    out_path = os.path.join(OUT_DIR, out_fname)
    cmd = f"python /content/Open-Sora-Plan/scripts/inference_text_to_video.py \
        --model-dir {MODEL_DIR} \
        --prompt {shlex.quote(prompt)} \
        --length {duration_seconds} \
        --output {shlex.quote(out_path)}"
    print("▶️ Running:", cmd)
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(p.stdout)
    print(p.stderr)
    if os.path.exists(out_path):
        return out_path
    return None

# ============================================================
# STEP 3: Telegram Bot
# ============================================================
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

def start(update, context):
    update.message.reply_text("👋 Send me a text prompt. I'll generate a short (4s) video.")

def handle_text(update, context):
    prompt = update.message.text
    update.message.reply_text("🎬 Generating video... Please wait ⏳")

    uid = update.message.from_user.id
    fname = f"vid_{uid}_{int(time.time())}.mp4"
    try:
        out_path = run_opensora_text2video(prompt, duration_seconds=4, out_fname=fname)
        if out_path:
            with open(out_path, "rb") as f:
                update.message.reply_video(video=f, timeout=300)
        else:
            update.message.reply_text("❌ Video generation failed.")
    except Exception as e:
        logging.exception(e)
        update.message.reply_text(f"Error: {e}")

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))
    updater.start_polling()
    print("✅ Bot started! Send text prompts to your bot.")
    updater.idle()

main()
