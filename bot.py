import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import json
import random
import time

load_dotenv()  # Carga variables del .env

TOKEN = os.getenv("DISCORD_TOKEN")
DATA_PATH = "levels.json"
FONDO = "fondo-bot.jpeg"  # Tu imagen descargada

# Intents básicos y message_content
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Inicializar datos
if os.path.exists(DATA_PATH):
    with open(DATA_PATH, "r") as f:
        data = json.load(f)
else:
    data = {}

ROLE_REWARDS = {5: "Solid Snake", 10: "Liquid Snake", 20: "Solidus Snake"}
last_xp_time = {}
XP_MIN = 10
XP_MAX = 20
COOLDOWN_SECONDS = 60
LEVEL_XP = 100

def get_level(xp):
    return xp // LEVEL_XP

def save_data():
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)

async def grant_role_if_any(member, new_level):
    pass  # deshabilitado porque requiere members intent

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")
    for guild in bot.guilds:
        canal = discord.utils.get(guild.text_channels, name="niveles")
        if not canal:
            await guild.create_text_channel("niveles")

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    uid = str(message.author.id)
    gid = str(message.guild.id)

    if gid not in data:
        data[gid] = {"users": {}}
    if uid not in data[gid]["users"]:
        data[gid]["users"][uid] = {"xp": 0, "level": 0}

    key = (gid, uid)
    now = time.time()
    last = last_xp_time.get(key, 0)
    if now - last >= COOLDOWN_SECONDS:
        gained = random.randint(XP_MIN, XP_MAX)
        user = data[gid]["users"][uid]
        user["xp"] += gained
        new_level = get_level(user["xp"])
        if new_level > user["level"]:
            user["level"] = new_level
            # Embed con avatar y fondo
            embed = discord.Embed(
                title=f"🎉 {message.author.display_name} subió a nivel {new_level}!",
                description=f"Ganó +{gained} XP",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=message.author.avatar.url)  # Avatar del miembro
            embed.set_image(url="attachment://" + FONDO)        # Fondo
            canal_niveles = discord.utils.get(message.guild.text_channels, name="niveles")
            if canal_niveles:
                await canal_niveles.send(file=discord.File(FONDO), embed=embed)
        save_data()
        last_xp_time[key] = now

    await bot.process_commands(message)

@bot.command()
async def nivel(ctx, member: discord.Member = None):
    member = member or ctx.author
    gid, uid = str(ctx.guild.id), str(member.id)
    user = data.get(gid, {}).get("users", {}).get(uid)

    if user:
        embed = discord.Embed(
            title=f"📊 Nivel de {member.display_name}",
            description=f"Nivel: {user['level']}\nXP: {user['xp']}",
            color=discord.Color.blue()
        )
        # Avatar del miembro
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        # Fondo
        embed.set_image(url="attachment://" + FONDO)
        await ctx.send(file=discord.File(FONDO), embed=embed)
    else:
        await ctx.send(f"{member.mention} aún no tiene progreso.")


bot.run(TOKEN)
