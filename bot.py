import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# ========== PUT YOUR KEYS HERE ==========
TELEGRAM_TOKEN = 8993862862:AAFWVyvQVpy91ISvk7Ih1IaLkt1DvJOI1qc

GEMINI_API_KEY = AQ.Ab8RN6KzZhEQ8HdpoS79IzoK7TsnYeSd1YksZREPRcNW_Npo7A
# ========================================

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-3.5-flash")   # free & supports images

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

SYSTEM_PROMPT = """
You are a professional price-action trader using Gautam Jha style analysis.
Always follow this exact structure:

**Chart Context**
- Instrument + timeframe + current price location relative to daily levels

**Key Liquidity Levels**
- Daily open
- Previous day high / low
- Any other high-probability levels

**Market Structure**
- Trend status (strong trend / pullback / range)

**Trade Idea(s)**
- Setup name (Break-and-Go / Retrace-to-Level / Level Reversal)
- Entry
- Stop
- Target / Exit rule
- Rationale (1-2 sentences)

**Risk Reminder**
- Educational only. Not financial advice. Manage risk.

Rules:
- Always start top-down from Daily Open.
- Prefer clear trends. Avoid FOMO.
- If chart is choppy, say so clearly.
- Keep language simple.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 Chart Analyzer Bot (Gautam Jha style)\n\n"
        "Send me:\n"
        "1. A chart screenshot + caption (e.g. BTC 15m or Gold daily)\n"
        "2. Or just type a description of the chart\n\n"
        "I will give you liquidity levels + trade ideas."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "How to use:\n"
        "• Photo + caption = best results\n"
        "• Text description also works\n"
        "• Mention instrument and timeframe"
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Analyzing chart... please wait ⏳")

    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    image_bytes = await file.download_as_bytearray()

    caption = update.message.caption or "No caption provided. Analyze the chart."

    try:
        response = model.generate_content(
            [SYSTEM_PROMPT, caption, {"mime_type": "image/jpeg", "data": image_bytes}]
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text(f"Error analyzing image: {e}\n\nTry sending a clearer chart or text description.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text("Analyzing... ⏳")

    try:
        response = model.generate_content([SYSTEM_PROMPT, text])
        await update.message.reply_text(response.text)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & \~filters.COMMAND, handle_text))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
