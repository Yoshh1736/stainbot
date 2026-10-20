import os
import asyncio
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery

# ================= CONFIGURATION =================
API_ID = 31658480
API_HASH = "9becba7687e9d33c9e201dbcf1e13e52"
BOT_TOKEN = "8947812851:AAHaYiJEhwZrDB-Z0oUPMO989Bs-Wbv0XgM"

# Required Channel for Referral Gating
REQUIRED_CHANNEL = "@Inw7l0sCM81mYzE1"

# ================= DATABASE / STORAGE (Mock) =================
user_subscriptions = {}  # { user_id: expiry_datetime }
user_attempts = {}       # { user_id: remaining_free_attempts }
user_targets = {}        # { user_id: {"target": phone, "service": type} }

# Custom access keys categorized by duration (Private keys managed by admin)
VALID_KEYS = {
    "STAIN-7DAYS-PRO77": {"days": 7, "tier": "7 Days Access"},
    "STAIN-1MONTH-VIP30": {"days": 30, "tier": "1 Month Access"},
    "STAIN-LIFETIME-ULTRA": {"days": 99999, "tier": "Lifetime Access"}
}

app = Client(
    "stain_flood_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ================= HELPER FUNCTIONS =================
def check_access(user_id: int) -> bool:
    """Check if user has an active subscription or remaining free attempts."""
    if user_id in user_subscriptions:
        if datetime.now() < user_subscriptions[user_id]:
            return True
        else:
            del user_subscriptions[user_id] # Expired
            
    # Check free attempts
    attempts = user_attempts.get(user_id, 3)
    return attempts > 0

def get_remaining_text(user_id: int) -> str:
    if user_id in user_subscriptions:
        expiry = user_subscriptions[user_id]
        if expiry == datetime.max:
            return "♾️ LIFETIME VIP"
        return f"⏳ Expires: {expiry.strftime('%b %d, %Y - %H:%M')}"
    else:
        attempts = user_attempts.get(user_id, 3)
        return f"⚡ Free Trials Left: {attempts}/3"

# ================= MAIN INTERFACE & COMMANDS =================
@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    user = message.from_user
    user_id = user.id
    
    if user_id not in user_attempts and user_id not in user_subscriptions:
        user_attempts[user_id] = 3  # Give 3 free attempts to new users

    status_str = get_remaining_text(user_id)

    ui_caption = (
        f"⚡ 𝙁 𝙇 𝙊 𝙊 𝘿   𝘽 𝙊 𝙏 ⚡\n"
        f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        f"👤 **Operator:** `{user.first_name}`\n"
        f"🔮 **Status:** `{status_str}`\n"
        f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        f"⚙️ *Welcome to the ultimate execution hub.*\n"
        f"*Select an option below to deploy operations or manage keys.*"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💥 𝗟𝗔𝗨𝗡𝗖𝗛 𝗙𝗟𝗢𝗢𝗗", callback_data="menu_flood")],
        [
            InlineKeyboardButton("💎 𝗣𝗥𝗜𝗖𝗜𝗡𝗚", callback_data="menu_pricing"),
            InlineKeyboardButton("🔑 𝗥𝗘𝗗𝗘𝗘𝗠 𝗞𝗘𝗬", callback_data="menu_redeem")
        ],
        [InlineKeyboardButton("📖 𝗛𝗘𝗟𝗣 & 𝗚𝗨𝗜𝗗𝗘", callback_data="menu_help")]
    ])

    await message.reply_text(ui_caption, reply_markup=keyboard)

@app.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    help_text = (
        "🛠️ **𝗙𝗟𝗢𝗢𝗗 𝗕𝗢𝗧 — 𝗢𝗣𝗘𝗥𝗔𝗧𝗜𝗢𝗡𝗔𝗟 𝗚𝗨𝗜𝗗𝗘**\n\n"
        "• **Free Access:** New operators receive **3 free execution attempts** automatically upon starting the bot.\n"
        "• **Execution:** Go to `Launch Flood`, select your service module (SMS, Call Voice, OTP, Payload), input the target number, and launch.\n"
        "• **Redeeming Keys:** Contact admin to avail an access key, then use `/redeem <YOUR_KEY>` or click the **Redeem Key** button to activate your tier.\n\n"
        "💡 *Need assistance or want to purchase a key? Contact administration.*"
    )
    await message.reply_text(help_text)

@app.on_message(filters.command("redeem"))
async def redeem_command(client: Client, message: Message):
    user_id = message.from_user.id
    args = message.text.split()
    
    if len(args) < 2:
        await message.reply_text(
            "⚠️ **Format Error:**\n"
            "Please provide your key alongside the command.\n\n"
            "💬 *Example:* `/redeem STAIN-7DAYS-PRO77`"
        )
        return

    key = args[1].strip()

    if key in VALID_KEYS:
        data = VALID_KEYS[key]
        days = data["days"]
        tier_name = data["tier"]

        if days >= 9999:
            user_subscriptions[user_id] = datetime.max
            expiry_str = "♾️ Lifetime Access"
        else:
            expiry_date = datetime.now() + timedelta(days=days)
            user_subscriptions[user_id] = expiry_date
            expiry_str = expiry_date.strftime('%B %d, %Y - %H:%M')

        # Clear free attempts since they upgraded
        if user_id in user_attempts:
            del user_attempts[user_id]

        await message.reply_text(
            f"✅ **𝗔𝗖𝗖𝗘𝗦𝗦 𝗚𝗥𝗔𝗡𝗧𝗘𝗗 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟𝗟𝗬**\n"
            f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
            f"🎖️ **Tier Unlocked:** `{tier_name}`\n"
            f"⏳ **Valid Until:** `{expiry_str}`\n"
            f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
            f"🚀 *All system restraints removed. Ready for deployment.*"
        )
    else:
        await message.reply_text("❌ **Invalid or expired access key.** Verify your sequence and try again.")

# ================= TEXT INPUT HANDLER FOR TARGETS =================
@app.on_message(filters.text & ~filters.command(["start", "help", "redeem"]))
async def handle_target_input(client: Client, message: Message):
    user_id = message.from_user.id
    
    # Check if user is waiting to input a target number for a service
    if user_id in user_targets:
        service_type = user_targets[user_id]
        target_number = message.text.strip()
        
        # Clear the waiting state
        del user_targets[user_id]
        
        if not check_access(user_id):
            await message.reply_text("❌ **Access Denied!** No free attempts or active key found. Please redeem a key.")
            return

        # Deduct free attempt if not subscribed
        if user_id not in user_subscriptions:
            if user_id in user_attempts and user_attempts[user_id] > 0:
                user_attempts[user_id] -= 1

        remaining_display = get_remaining_text(user_id)
        
        # Execution confirmation message
        await message.reply_text(
            f"⚡ **𝗘𝗫𝗘𝗖𝗨𝗧𝗜𝗢𝗡 𝗜𝗡 𝗣𝗥𝗢𝗚𝗥𝗘𝗦𝗦...**\n"
            f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
            f"🎯 **Target:** `{target_number}`\n"
            f"📡 **Module:** `{service_type}`\n"
            f"📊 Status: `Payload successfully dispatched.`\n"
            f"🔮 `{remaining_display}`\n"
            f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Return to Dashboard", callback_data="menu_main")]
            ])
        )

# ================= CALLBACK HANDLERS =================
@app.on_callback_query()
async def callback_router(client: Client, callback_query: CallbackQuery):
    data = callback_query.data
    user_id = callback_query.from_user.id

    if data == "menu_main":
        if user_id in user_targets:
            del user_targets[user_id]
            
        status_str = get_remaining_text(user_id)
        ui_caption = (
            f"⚡ 𝙁 𝙇 𝙊 𝙊 𝘿   𝘽 𝙊 𝙏 ⚡\n"
            f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
            f"🔮 **Status:** `{status_str}`\n"
            f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
            f"⚙️ *Welcome to the ultimate execution hub.*\n"
            f"*Select an option below to deploy operations or manage keys.*"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💥 𝗟𝗔𝗨𝗡𝗖𝗛 𝗙𝗟𝗢𝗢𝗗", callback_data="menu_flood")],
            [
                InlineKeyboardButton("💎 𝗣𝗥𝗜𝗖𝗜𝗡𝗚", callback_data="menu_pricing"),
                InlineKeyboardButton("🔑 𝗥𝗘𝗗𝗘𝗘𝗠 𝗞𝗘𝗬", callback_data="menu_redeem")
            ],
            [InlineKeyboardButton("📖 𝗛𝗘𝗟𝗣 & 𝗚𝗨𝗜𝗗𝗘", callback_data="menu_help")]
        ])
        await callback_query.message.edit_text(ui_caption, reply_markup=keyboard)

    elif data == "menu_flood":
        if not check_access(user_id):
            await callback_query.answer("❌ Access Denied! No free attempts or active key found.", show_alert=True)
            return

        status_msg = get_remaining_text(user_id)
        await callback_query.message.edit_text(
            f"💥 **𝗙𝗟𝗢𝗢𝘿 𝗖𝗢𝗡𝗦𝗢𝗟𝗘 — 𝗦𝗘𝗟𝗘𝗖𝗧 𝗠𝗢𝗗𝗨𝗟𝗘**\n"
            f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
            f"📊 `{status_msg}`\n"
            f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
            f"🎯 *Choose the execution service vector below:*",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📨 SMS Flood Service", callback_data="srv_sms")],
                [InlineKeyboardButton("📞 Call Voice Service", callback_data="srv_call")],
                [InlineKeyboardButton("🔐 OTP Bomber Service", callback_data="srv_otp")],
                [InlineKeyboardButton("💣 Custom Payload Service", callback_data="srv_payload")],
                [InlineKeyboardButton("🔙 Return to Dashboard", callback_data="menu_main")]
            ])
        )

    elif data.startswith("srv_"):
        if not check_access(user_id):
            await callback_query.answer("❌ Limit reached! Please upgrade or redeem a key.", show_alert=True)
            return

        service_map = {
            "srv_sms": "SMS Flood",
            "srv_call": "Call Voice",
            "srv_otp": "OTP Bomber",
            "srv_payload": "Custom Payload"
        }
        
        selected_service = service_map.get(data, "Unknown Service")
        user_targets[user_id] = selected_service

        await callback_query.message.edit_text(
            f"🎯 **𝗧𝗔𝗥𝗚𝗘𝗧 𝗜𝗡𝗣𝗨𝗧 — {selected_service.upper()}**\n"
            f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
            f"⌨️ *Please reply directly in chat with the target phone number or details.*\n\n"
            f"💬 *Example:* `+639123456789`\n"
            f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Cancel", callback_data="menu_flood")]
            ])
        )

    elif data == "menu_pricing":
        pricing_text = (
            "💎 **𝗔𝗖𝗖𝗘𝗦𝗦 𝗧𝗜𝗘𝗥𝗦 & 𝗣𝗥𝗜𝗖𝗜𝗡𝗚**\n"
            "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
            "🗓️ **7 Days Access**\n"
            "└ 💵 `₱100`\n\n"
            "🗓️ **1 Month Access**\n"
            "└ 💵 `₱150`\n\n"
            "♾️ **Lifetime Access**\n"
            "└ 💵 `₱199`\n"
            "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
            "💡 *Access keys are private. Avail your key directly from admin first, then choose 'Redeem Key' to activate.*"
        )
        await callback_query.message.edit_text(
            pricing_text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔑 Redeem Key Now", callback_data="menu_redeem")],
                [InlineKeyboardButton("🔙 Return to Dashboard", callback_data="menu_main")]
            ])
        )

    elif data == "menu_redeem":
        await callback_query.message.edit_text(
            "🔑 **𝗞𝗘𝗬 𝗥𝗘𝗗𝗘𝗠𝗣𝗧𝗜𝗢𝗡 𝗣𝗢𝗥𝗧𝗔𝗟**\n"
            "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
            "To activate your purchased tier, send the command in chat format:\n\n"
            "💬 `/redeem <YOUR_ACCESS_KEY>`\n\n"
            "*Example:*\n`/redeem STAIN-7DAYS-PRO77`\n"
            "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Return to Dashboard", callback_data="menu_main")]
            ])
        )

    elif data == "menu_help":
        help_text = (
            "📖 **𝗢𝗣𝗘𝗥𝗔𝗧𝗜𝗢𝗡𝗔𝗟 𝗜𝗡𝗦𝗧𝗥𝗨𝗖𝗧𝗜𝗢𝗡𝗦**\n"
            "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
            "• **Free Tiers:** Every new operator gets **3 free attempts** to test system features.\n"
            "• **Services:** Select from SMS, Call Voice, OTP, or Payload modules and supply your target number.\n"
            "• **Access Control:** Once free attempts are exhausted, acquire a private key from admin and redeem it.\n"
            "• **Commands:**\n"
            "  - `/start` - Open dashboard\n"
            "  - `/help` - View quick guide\n"
            "  - `/redeem <key>` - Activate key\n"
            "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
        )
        await callback_query.message.edit_text(
            help_text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Return to Dashboard", callback_data="menu_main")]
            ])
        )

# ================= STARTUP =================
if __name__ == "__main__":
    print("[+] FLOOD BOT Online. Deploying polling loop...")
    app.run()
