import discord
from discord.ext import commands
from discord import app_commands
import os
from flask import Flask
from threading import Thread

# --- RENDER CANLI TUTMA ---
app = Flask('')
@app.route('/')
def home(): return "MesxeZe Pro Aktif!"
def run(): app.run(host='0.0.0.0', port=8080)

# --- BOT AYARLARI ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Verileri tutmak için (Kalıcı olması için ileride veritabanı eklenebilir)
user_data = {}

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'🔥 MesxeZe PRO Sistemi Devrede: {bot.user}')

@bot.event
async def on_message(message):
    if message.author.bot: return
    uid = message.author.id
    if uid not in user_data:
        user_data[uid] = {"xp": 0, "level": 1}
    
    user_data[uid]["xp"] += 1
    
    # Seviye atlama mantığı (Her 100 mesajda 1 seviye)
    if user_data[uid]["xp"] >= user_data[uid]["level"] * 100:
        user_data[uid]["level"] += 1
        await message.channel.send(f"🎊 Tebrikler {message.author.mention}! Klan seviyen **{user_data[uid]['level']}** oldu!")
    
    await bot.process_commands(message)

# --- GELİŞMİŞ KOMUTLAR ---

@bot.tree.command(name="profil", description="Klan profilini gösterir")
async def profil(interaction: discord.Interaction, uye: discord.Member = None):
    target = uye or interaction.user
    data = user_data.get(target.id, {"xp": 0, "level": 1})
    
    embed = discord.Embed(title=f"🛡️ {target.name} - Klan Kartı", color=discord.Color.blue())
    embed.add_field(name="Seviye", value=data["level"], inline=True)
    embed.add_field(name="Toplam XP", value=data["xp"], inline=True)
    embed.set_thumbnail(url=target.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="top", description="Klanın en iyileri")
async def top(interaction: discord.Interaction):
    sorted_users = sorted(user_data.items(), key=lambda x: x[1]["xp"], reverse=True)[:10]
    embed = discord.Embed(title="🏆 MesxeZe Şeref Kürsüsü", color=discord.Color.gold())
    
    for i, (uid, data) in enumerate(sorted_users, 1):
        member = interaction.guild.get_member(uid)
        name = member.name if member else "Eski Üye"
        embed.add_field(name=f"{i}. {name}", value=f"Seviye {data['level']} | {data['xp']} XP", inline=False)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="duyuru", description="Yetkili duyurusu atar")
@app_commands.checks.has_permissions(administrator=True)
async def duyuru(interaction: discord.Interaction, mesaj: str):
    embed = discord.Embed(title="📢 MesxeZe KLAN DUYURUSU", description=mesaj, color=discord.Color.red())
    embed.set_footer(text=f"Yetkili: {interaction.user.name}")
    await interaction.channel.send(content="@everyone", embed=embed)
    await interaction.response.send_message("Duyuru atıldı kanka!", ephemeral=True)

# --- TICKET SİSTEMİ BUTONLU ---
class TicketKapat(discord.ui.View):
    @discord.ui.button(label="Talebi Kapat", style=discord.ButtonStyle.danger, emoji="🔒")
    async def kapat(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Kanal 5 saniye içinde siliniyor...")
        await interaction.channel.delete()

class DestekSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Klan Alımı", emoji="🛡️"),
            discord.SelectOption(label="Etkinlik Önerisi", emoji="💡"),
            discord.SelectOption(label="Şikayet", emoji="⚠️")
        ]
        super().__init__(placeholder="Konu seçin...", options=options)

    async def callback(self, interaction: discord.Interaction):
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        channel = await interaction.guild.create_text_channel(name=f"destek-{interaction.user.name}", overwrites=overwrites)
        await interaction.response.send_message(f"Kanal açıldı: {channel.mention}", ephemeral=True)
        await channel.send(f"Selam {interaction.user.mention}, talebin açıldı. İşin bitince butona bas.", view=TicketKapat())

@bot.tree.command(name="destek", description="Destek sistemini başlatır")
async def destek(interaction: discord.Interaction):
    view = discord.ui.View()
    view.add_item(DestekSelect())
    await interaction.response.send_message("Yardım lazım mı kanka?", view=view)

# Botu başlat
Thread(target=run).start()
bot.run(os.environ['TOKEN'])
