import discord
from discord.ext import commands
import os

# İntents ayarları
intents = discord.Intents.default()
intents.members = True # Üye girişlerini izlemek için şart
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} kayıt botu aktif!')

# --- HOŞ GELDİN SİSTEMİ ---
@bot.event
async def on_member_join(member):
    # 'Kayıt' kanalının ID'sini buraya yaz
    channel = discord.utils.get(member.guild.text_channels, name="hoş-geldin")
    if channel:
        embed = discord.Embed(
            title="👋 Aramıza Hoş Geldin!",
            description=f"Selam {member.mention}, klanımıza hoş geldin! Kuralları okumayı unutma.",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        await channel.send(embed=embed)

# --- KAYIT KOMUTU ---
@bot.tree.command(name="kayit", description="Yeni üyeyi kayıt eder")
async def kayit(interaction: discord.Interaction, member: discord.Member, isim: str):
    # Sadece yetkili olanlar kullanabilsin
    if interaction.user.guild_permissions.manage_roles:
        await member.edit(nick=isim)
        role = discord.utils.get(interaction.guild.roles, name="Üye")
        if role:
            await member.add_roles(role)
        await interaction.response.send_message(f"{member.mention} başarıyla {isim} ismiyle kaydedildi ve rolü verildi!")
    else:
        await interaction.response.send_message("Bunun için yetkin yok!", ephemeral=True)

# Botu Başlat
bot.run(os.environ['TOKEN'])