import discord
from discord.ext import commands
from discord import app_commands
import os
from flask import Flask
from threading import Thread

# --- RENDER CANLI TUTMA ---
app = Flask('')
@app.route('/')
def home(): return "Kayıt Botu Aktif!"
def run(): app.run(host='0.0.0.0', port=8081) # Portu 8081 yaptım karışmasın diye

# --- BOT AYARLARI ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'{bot.user} Kayıt Botu Hazır!')

# HOŞ GELDİN MESAJI
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="hoş-geldin")
    if channel:
        embed = discord.Embed(title="Aramıza Hoş Geldin!", description=f"Selam {member.mention}, klan sunucumuza hoş geldin!", color=discord.Color.green())
        await channel.send(embed=embed)

# KAYIT KOMUTU
@bot.tree.command(name="kayit", description="Yeni üyeyi isimlendirir")
@app_commands.checks.has_permissions(manage_nicknames=True)
async def kayit(interaction: discord.Interaction, uye: discord.Member, yeni_isim: str):
    await uye.edit(nick=yeni_isim)
    await interaction.response.send_message(f"✅ {uye.mention} ismi **{yeni_isim}** olarak güncellendi.", ephemeral=True)

Thread(target=run).start()
bot.run(os.environ['TOKEN'])
