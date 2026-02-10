import discord
from discord.ext import commands
from discord import app_commands
import json, sqlite3, asyncio

# ===== LOAD CONFIG =====
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

with open("theme.json", "r", encoding="utf-8") as f:
    theme = json.load(f)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# ===== DATABASE =====
db = sqlite3.connect("database.sqlite")
cur = db.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS wallet (
    user_id INTEGER PRIMARY KEY,
    money INTEGER
)""")
db.commit()

# ===== UTILS =====
def embed(title, desc):
    em = discord.Embed(
        title=title,
        description=desc,
        color=theme["color"]
    )
    em.set_footer(text=theme["footer"])
    if theme["banner"]:
        em.set_image(url=theme["banner"])
    return em

# ===== READY =====
@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Bot Online!")

# ===== WALLET =====
@bot.tree.command(name="wallet")
async def wallet(interaction: discord.Interaction):
    uid = interaction.user.id
    cur.execute("SELECT money FROM wallet WHERE user_id=?", (uid,))
    data = cur.fetchone()
    if not data:
        cur.execute("INSERT INTO wallet VALUES (?,?)", (uid, 0))
        db.commit()
        money = 0
    else:
        money = data[0]

    await interaction.response.send_message(
        embed("💰 Wallet", f"ยอดเงินของคุณ: **{money} บาท**")
    )

# ===== GACHA =====
@bot.tree.command(name="gacha")
async def gacha(interaction: discord.Interaction):
    import random
    result = random.choice(["SSR ⭐⭐⭐⭐⭐", "SR ⭐⭐⭐⭐", "R ⭐⭐⭐"])
    await interaction.response.send_message(
        embed("🎰 กาชา", f"คุณสุ่มได้: **{result}**")
    )

# ===== SHOP =====
@bot.tree.command(name="shop")
async def shop(interaction: discord.Interaction):
    await interaction.response.send_message(
        embed("🛒 ร้านค้า", "• VIP 100฿\n• ITEM 50฿")
    )

# ===== BOOST SYSTEM =====
@bot.event
async def on_member_update(before, after):
    role = after.guild.get_role(config["BOOST_ROLE_ID"])
    if not role:
        return

    if not before.premium_since and after.premium_since:
        await after.add_roles(role)
        ch = after.guild.system_channel
        if ch:
            await ch.send(
                embed("🚀 Boost", f"{after.mention} ขอบคุณสำหรับการบูสต์!")
            )

# ===== MUSIC (BASIC) =====
@bot.tree.command(name="play")
async def play(interaction: discord.Interaction, url: str):
    await interaction.response.send_message(
        embed("🎵 Music", "ระบบเพลง (โหมดพื้นฐาน)")
    )

# ===== PUNISH =====
@bot.tree.command(name="mute")
async def mute(interaction: discord.Interaction, member: discord.Member):
    if config["ADMIN_ROLE_ID"] not in [r.id for r in interaction.user.roles]:
        return await interaction.response.send_message("❌ ไม่มีสิทธิ์", ephemeral=True)

    await member.timeout(discord.utils.utcnow() + discord.timedelta(minutes=10))
    await interaction.response.send_message(
        embed("🔇 ลงโทษ", f"{member.mention} ถูก mute")
    )

bot.run(config["TOKEN"])
