from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)
from datetime import datetime
import os

# Railway BOT TOKEN
TOKEN = os.getenv("BOT_TOKEN")

# Your public proof channel username
PROOF_CHANNEL = "@eliteescrowproof"

# Your Telegram ID(s)
ADMINS = [123456789]

# Deal counter
deal_counter = 0


def is_admin(user_id):
    return user_id in ADMINS


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Escrow Bot Online")


async def save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global deal_counter

    user_id = update.effective_user.id

    # Admin check
    if not is_admin(user_id):
        await update.message.reply_text("❌ Not allowed")
        return

    # Command format check
    if len(context.args) < 3:
        await update.message.reply_text(
            "Usage:\n/save @buyer @seller amount details"
        )
        return

    deal_counter += 1

    buyer = context.args[0]
    seller = context.args[1]
    amount = context.args[2]
    details = " ".join(context.args[3:]) if len(context.args) > 3 else "N/A"

    time = datetime.now().strftime("%Y-%m-%d %H:%M")

    message = f"""
━━━━━━━━━━━━━━
💼 ESCROW PROOF

🆔 Deal ID: #{deal_counter:04d}
👤 Buyer: {buyer}
👤 Seller: {seller}
💰 Amount: {amount}
📝 Details: {details}
🕒 Time: {time}

✅ COMPLETED
━━━━━━━━━━━━━━
"""

    # Send proof to channel
    await context.bot.send_message(
        chat_id=PROOF_CHANNEL,
        text=message
    )

    # Reply in group
    await update.message.reply_text(
        f"✅ Deal saved #{deal_counter:04d}"
    )


# Build bot
app = ApplicationBuilder().token(TOKEN).build()

# Commands
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("save", save))

print("✅ Escrow Bot Online")

# Run bot
app.run_polling()
