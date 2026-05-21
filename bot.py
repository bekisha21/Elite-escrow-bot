from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime
import os

TOKEN = os.getenv("BOT_TOKEN")
PROOF_CHANNEL = "@elieescrowproof"

deal_counter = 0
ADMINS = [5635739078]  # replace with your Telegram ID

def is_admin(user_id):
    return user_id in ADMINS


async def save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global deal_counter

    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Not allowed")
        return

    if len(context.args) < 3:
        await update.message.reply_text("Usage: /save @buyer @seller amount details")
        return

    deal_counter += 1

    buyer = context.args[0]
    seller = context.args[1]
    amount = context.args[2]
    details = " ".join(context.args[3:]) if len(context.args) > 3 else "N/A"

    time = datetime.now().strftime("%Y-%m-%d %H:%M")

    msg = f"""
━━━━━━━━━━━━━━
💼 ESCROW PROOF

🆔 #{deal_counter:04d}
👤 Buyer: {buyer}
👤 Seller: {seller}
💰 Amount: {amount}
📝 Details: {details}
🕒 Time: {time}

✅ COMPLETED
━━━━━━━━━━━━━━
"""

    await context.bot.send_message(chat_id=PROOF_CHANNEL, text=msg)
    await update.message.reply_text(f"Saved ✔ #{deal_counter:04d}")


app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("save", save))

app.run_polling()
