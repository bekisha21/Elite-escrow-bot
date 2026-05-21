from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from datetime import datetime
import os

# =========================
# CONFIG
# =========================

TOKEN = os.getenv("BOT_TOKEN")

PROOF_CHANNEL = "@eliteescrowproof"

ADMINS = [8216037421, 5635739078, 7986300943, 6632452285, 6953440368]

# =========================
# STORAGE
# =========================

deals = {}
refunds = {}
deal_id = 0


def is_admin(user_id):
    return user_id in ADMINS


# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Escrow Bot Online")


# =========================
# DEAL CREATE
# =========================

async def deal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global deal_id

    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("❌ Not allowed")

    if len(context.args) < 3:
        return await update.message.reply_text("Usage: /deal @buyer @seller amount details")

    deal_id += 1

    buyer = context.args[0]
    seller = context.args[1]
    amount = context.args[2]
    details = " ".join(context.args[3:]) if len(context.args) > 3 else "N/A"

    deals[str(deal_id)] = {
        "buyer": buyer,
        "seller": seller,
        "amount": amount,
        "details": details,
        "status": "ACTIVE"
    }

    await update.message.reply_text(f"✅ Deal created #{deal_id:04d}")


# =========================
# DONE
# =========================

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        return await update.message.reply_text("Usage: /done deal_id")

    did = context.args[0]

    if did not in deals:
        return await update.message.reply_text("❌ Deal not found")

    deals[did]["status"] = "WAITING ESCROW"

    await update.message.reply_text(f"⏳ Deal #{int(did):04d} marked DONE")


# =========================
# CONFIRM (FINAL POST)
# =========================

async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("❌ Not allowed")

    if len(context.args) < 1:
        return await update.message.reply_text("Usage: /confirm deal_id")

    did = context.args[0]

    if did not in deals:
        return await update.message.reply_text("❌ Deal not found")

    if deals[did]["status"] != "WAITING ESCROW":
        return await update.message.reply_text("❌ Deal not ready")

    d = deals[did]
    time = datetime.now().strftime("%Y-%m-%d %H:%M")

    escrow_admin = update.effective_user.username
    if escrow_admin is None:
        escrow_admin = "unknown"

    message = f"""
━━━━━━━━━━━━━━
💼 ESCROW PROOF (FINAL)

🆔 Deal ID: #{int(did):04d}

👤 Buyer: {d['buyer']}
👤 Seller: {d['seller']}
💰 Amount: {d['amount']}
📝 Details: {d['details']}

🛡 Escrow Agent: @{escrow_admin}

📅 {time}

🔒 STATUS: COMPLETED & VERIFIED
━━━━━━━━━━━━━━
"""

    await context.bot.send_message(PROOF_CHANNEL, message)
    await update.message.reply_text("✅ Posted to channel")


# =========================
# REFUND REQUEST
# =========================

async def refund(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        return await update.message.reply_text("Usage: /refund deal_id reason")

    did = context.args[0]
    reason = " ".join(context.args[1:])

    if did not in deals:
        return await update.message.reply_text("❌ Deal not found")

    refunds[did] = {
        "reason": reason,
        "status": "PENDING"
    }

    keyboard = [
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{did}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{did}")
        ]
    ]

    markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=PROOF_CHANNEL,
        text=f"""
🚨 REFUND REQUEST

🆔 Deal #{int(did):04d}
👤 Buyer: {d['buyer']}
👤 Seller: {d['seller']}
💰 Amount: {d['amount']}
📝 Reason: {reason}

⚠ Pending admin decision
""",
        reply_markup=markup
    )

    await update.message.reply_text("🚨 Refund sent")


# =========================
# BUTTON HANDLER
# =========================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if user_id not in ADMINS:
        return await query.edit_message_text("❌ Not allowed")

    data = query.data
    action, did = data.split("_")

    if did not in refunds:
        return await query.edit_message_text("❌ Not found")

    if action == "approve":
        refunds[did]["status"] = "APPROVED"
        await query.edit_message_text("✅ REFUND APPROVED")

    elif action == "reject":
        refunds[did]["status"] = "REJECTED"
        await query.edit_message_text("❌ REFUND REJECTED")


# =========================
# BOT START
# =========================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("deal", deal))
app.add_handler(CommandHandler("done", done))
app.add_handler(CommandHandler("confirm", confirm))
app.add_handler(CommandHandler("refund", refund))
app.add_handler(CallbackQueryHandler(button_handler))

print("✅ Escrow Bot Online")

app.run_polling()
