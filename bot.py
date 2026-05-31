import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import io
import os
import threading
from flask import Flask
import requests
import time

# ── Config ──────────────────────────────────────────────
TOKEN = os.environ.get("DISCORD_TOKEN")
WELCOME_CHANNEL_ID = int(os.environ.get("WELCOME_CHANNEL_ID", 0))
RENDER_URL = os.environ.get("RENDER_URL", "")  # tu URL de Render ej: https://hola-bot.onrender.com

# ── Keep-alive Flask ────────────────────────────────────
app = Flask(__name__)

@app.route("/")
def home():
    return "Hola bot está vivo 🐱", 200

def run_flask():
    app.run(host="0.0.0.0", port=8080)

def keep_alive_ping():
    """Hace ping cada 10 min para que Render no duerma el bot"""
    while True:
        time.sleep(600)
        try:
            if RENDER_URL:
                requests.get(RENDER_URL, timeout=10)
                print("✅ Ping enviado")
        except Exception as e:
            print(f"⚠️ Ping falló: {e}")

# ── Banner con nombre ───────────────────────────────────
BANNER_PATH = "banner.png"  # la imagen del gato que subiste

def make_welcome_image(username: str) -> io.BytesIO:
    img = Image.open(BANNER_PATH).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Fuentes
    try:
        font_name = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 90)
    except:
        font_name = ImageFont.load_default()

    white = (255, 255, 255, 255)

    # Poner el nombre abajo a la izquierda
    x, y = 60, img.height - 160
    # Sombra para legibilidad
    draw.text((x + 3, y + 3), username, font=font_name, fill=(0, 0, 0, 180))
    draw.text((x, y), username, font=font_name, fill=white)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

# ── Bot ─────────────────────────────────────────────────
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

@bot.event
async def on_member_join(member: discord.Member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if not channel:
        print(f"⚠️ Canal {WELCOME_CHANNEL_ID} no encontrado")
        return

    img_buf = make_welcome_image(member.display_name)
    file = discord.File(img_buf, filename="bienvenida.png")
    await channel.send(file=file)

# ── Arranque ────────────────────────────────────────────
if __name__ == "__main__":
    # Flask en hilo separado
    threading.Thread(target=run_flask, daemon=True).start()
    # Keep-alive ping en hilo separado
    threading.Thread(target=keep_alive_ping, daemon=True).start()
    # Bot
    bot.run(TOKEN)
