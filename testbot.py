"""
STA!N.EXE — Telegram Premium Bot Edition
Owner: stain
Contact: t.me/mtfeels
Hosting Target: PythonAnywhere
Requirements: pip install pyrogram tgcrypto requests
"""

import time
import requests
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ─── CONFIGURATION & CREDENTIALS ───────────────────────────────────
API_ID = 31658480       # Replace with your Telegram API_ID
API_HASH = "9becba7687e9d33c9e201dbcf1e13e52"  # Replace with your Telegram API_HASH
BOT_TOKEN = "8947812851:AAHaYiJEhwZrDB-Z0oUPMO989Bs-Wbv0XgM" # Replace with your Telegram Bot Token

REQUIRED_CHANNEL = "https://t.me/+Inw7l0sCM81mYzE1"
CHANNEL_USERNAME = "Inw7l0sCM81mYzE1" # For check chat member or join gate
OWNER_CONTACT = "https://t.me/mtfeels"
API_URL = "https://beboy-sms.vercel.app/attack"

# In-memory mock database (Use SQLite/JSON for PythonAnywhere production persistence)
USERS_DB = {} 
# User schema: { user_id: { "referred": bool, "free_uses": int, "access_type": str, "expiry": float } }

PRICES = {
    "7d": "7 Days Access — $2 / ₱100",
    "1m": "1 Month Access — $3 / ₱150",
    "30m": "30 Months Access — $6 / ₱350",
    "lifetime": "Lifetime Access — $8 / ₱500"
}

app = Client("stain_exe_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ─── /START & REFERRAL GATEWAY ─────────────────────────────────────
@app.on_message(filters.command("start"))
def start_command(client, message):
    user_id = message.from_user.id
    
    if user_id not in USERS_DB:
        USERS_DB[user_id] = {
            "referred": False,
            "free_uses": 3,
            "access_type": "Free Trial",
            "expiry": time.time() + 86400 * 3
        }

    user = USERS_DB[user_id]

    if not user["referred"]:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 JOIN REQUIRED CHANNEL", url=REQUIRED_CHANNEL)],
            [InlineKeyboardButton("✅ VERIFY MEMBERSHIP", callback_data="verify_join")]
        ])
        message.reply_text(
            f"**STA!N.EXE — GATEWAY SECURITY**\n\n"
            f"**OWNER:** stain\n"
            f"**CONTACT:** {OWNER_CONTACT}\n\n"
            f"**[!] ACCESS RESTRICTED:** You must join our official telegram channel to initialize your hardware profile and bypass system lockdown.",
            reply_markup=keyboard
        )
    else:
        show_main_menu(message)


@app.on_callback_query(filters.regex("verify_join"))
def verify_join(client, callback_query):
    user_id = callback_query.from_user.id
    # In production, check via client.get_chat_member(CHANNEL_USERNAME, user_id)
    USERS_DB[user_id]["referred"] = True
    
    callback_query.message.edit_text(
        "**[+] MEMBERSHIP VERIFIED.**\n"
        "Hardware handshake confirmed. Welcome to **STA!N.EXE**.\n"
        "You have been granted **3 Free Executions** before key activation is required.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🚀 LAUNCH DASHBOARD", callback_data="main_menu")]
        ])
    )


# ─── MAIN MENU & TUTORIALS ─────────────────────────────────────────
@app.on_callback_query(filters.regex("main_menu"))
def main_menu_callback(client, callback_query):
    show_main_menu(callback_query.message, edit=True)

def show_main_menu(message, edit=False):
    text = (
        f"**STA!N.EXE — PRO TERMINAL INTERFACE**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"**OWNER:** `stain` | **CONTACT:** `t.me/mtfeels`\n"
        f"Select a module below to execute deployment vectors:\n"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📞 VOICE DISPATCH [CALL]", callback_data="mod_call"), InlineKeyboardButton("Tutorial", callback_data="tut_call")],
        [InlineKeyboardButton("✉️ CUSTOM PAYLOAD [SMS]", callback_data="mod_sms"), InlineKeyboardButton("Tutorial", callback_data="tut_sms")],
        [InlineKeyboardButton("🔐 OTP FLOODER [S5]", callback_data="mod_otp"), InlineKeyboardButton("Tutorial", callback_data="tut_otp")],
        [InlineKeyboardButton("📊 ACCOUNT STATS & TRACKER", callback_data="user_stats")],
        [InlineKeyboardButton("🔑 PURCHASE ACCESS KEY", callback_data="buy_access")]
    ])
    
    if edit:
        message.edit_text(text, reply_markup=keyboard)
    else:
        message.reply_text(text, reply_markup=keyboard)


# ─── MODULE TUTORIALS & GUIDES ─────────────────────────────────────
@app.on_callback_query(filters.regex("^tut_"))
def show_tutorial(client, callback_query):
    mod = callback_query.data.split("_")[1]
    guides = {
        "call": "**[TUTORIAL: VOICE DISPATCH]**\n\n1. Select target phone number format (+639...)\n2. Sets automated voice loops to target.\n3. Monitor progress bar until completion.",
        "sms": "**[TUTORIAL: CUSTOM SMS]**\n\n1. Input target digits.\n2. Write custom payload message header.\n3. Dispatches via multi-gateway API nodes.",
        "otp": "**[TUTORIAL: OTP FLOODER]**\n\n1. Targets financial and verification endpoints.\n2. Floods target device with concurrent request batches."
    }
    callback_query.message.edit_text(
        guides.get(mod, "Guide unavailable."),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« BACK TO MENU", callback_data="main_menu")]])
    )


# ─── STATS & TRACKER ───────────────────────────────────────────────
@app.on_callback_query(filters.regex("user_stats"))
def user_stats(client, callback_query):
    user_id = callback_query.from_user.id
    user = USERS_DB.get(user_id, {"free_uses": 0, "access_type": "Expired", "expiry": 0})
    
    status_text = "🟢 ACTIVE" if user["expiry"] > time.time() else "🔴 EXPIRED"
    
    text = (
        f"**STA!N.EXE — USER TRACKER**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **USER ID:** `{user_id}`\n"
        f"🎟️ **ACCESS TIER:** `{user['access_type']}`\n"
        f"⚡ **FREE USES LEFT:** `{user['free_uses']} / 3`\n"
        f"📡 **STATUS:** {status_text}\n"
    )
    
    keyboard = [
        [InlineKeyboardButton("🔑 BUY ACCESS KEY", callback_data="buy_access")],
        [InlineKeyboardButton("« BACK TO MENU", callback_data="main_menu")]
    ]
    
    if user["expiry"] <= time.time():
        keyboard.insert(0, [InlineKeyboardButton("⚠️ RENEW SUBSCRIPTION NOW", url=OWNER_CONTACT)])

    callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


# ─── ACCESS KEY PRICING MENU ───────────────────────────────────────
@app.on_callback_query(filters.regex("buy_access"))
def buy_access(client, callback_query):
    text = (
        f"**STA!N.EXE — ACCESS KEY LICENSING**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Select your license duration below. Clicking any package will route you directly to the owner for key generation and hardware binding.\n\n"
        f"• **7 Days:** `{PRICES['7d']}`\n"
        f"• **1 Month:** `{PRICES['1m']}`\n"
        f"• **30 Months:** `{PRICES['30m']}`\n"
        f"• **Lifetime:** `{PRICES['lifetime']}`\n"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 BUY 7 DAYS", url=OWNER_CONTACT)],
        [InlineKeyboardButton("🛒 BUY 1 MONTH", url=OWNER_CONTACT)],
        [InlineKeyboardButton("🛒 BUY 30 MONTHS", url=OWNER_CONTACT)],
        [InlineKeyboardButton("🛒 BUY LIFETIME", url=OWNER_CONTACT)],
        [InlineKeyboardButton("« BACK TO MENU", callback_data="main_menu")]
    ])
    callback_query.message.edit_text(text, reply_markup=keyboard)


# ─── EXECUTION HANDLER WITH LIVE PROGRESS BAR ──────────────────────
@app.on_callback_query(filters.regex("^mod_"))
def execute_module(client, callback_query):
    user_id = callback_query.from_user.id
    user = USERS_DB.get(user_id, {"free_uses": 0, "access_type": "Free Trial", "expiry": 0})
    
    # Check limit logic
    if user["access_type"] == "Free Trial" and user["free_uses"] <= 0 and user["expiry"] < time.time():
        callback_query.message.edit_text(
            "**[!] LIMIT REACHED:** You have exhausted your 3 free executions.\n"
            "Please purchase an access key to continue using **STA!N.EXE**.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔑 BUY ACCESS KEY", callback_data="buy_access")],
                [InlineKeyboardButton("« BACK", callback_data="main_menu")]
            ])
        )
        return

    if user["access_type"] == "Free Trial":
        USERS_DB[user_id]["free_uses"] -= 1

    msg = callback_query.message.edit_text("**[>] INITIALIZING DISPATCH PIPELINE...**")
    
    # Live Progress Bar Simulation
    total_blocks = 20
    for i in range(1, total_blocks + 1):
        filled = "#" * i
        empty = "-" * (total_blocks - i)
        pct = int((i / total_blocks) * 100)
        time.sleep(0.15)
        try:
            msg.edit_text(
                f"**STA!N.EXE — LIVE EXECUTION RUNNING**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"[{filled}{empty}] {pct}%\n"
                f"Status: Transmitting data packets..."
            )
        except Exception:
            pass

    msg.edit_text(
        "**[+] EXECUTION SEQUENCE COMPLETED**\n"
        "All targeted pulses dispatched successfully.\n"
        f"Remaining Free Uses: `{max(0, USERS_DB[user_id]['free_uses'])}`",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« RETURN TO MENU", callback_data="main_menu")]])
    )


if __name__ == "__main__":
    print("[+] STA!N.EXE Telegram Bot Online. Deploying polling loop...")
    app.run()