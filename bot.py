import discord
from discord.ext import commands
from discord import app_commands
import os
from flask import Flask
from threading import Thread
import random
import datetime

# --- RENDER CANLI TUTMA ---
app = Flask('')
@app.route('/')
def home(): return "🔥 MesxeZe Pro Aktif!"
def run(): app.run(host='0.0.0.0', port=8080)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

klan_puani = {}

@bot.event
async def on_ready():
    await bot.tree.sync()
    activity = discord.Game(name="🛡️ MesxeZe Klanını Yönetiyor")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print(f'🚀 {bot.user} Ultimate Klan Botu Devrede!')

# --- GELİŞMİŞ EKONOMİ ---
@bot.tree.command(name="profil", description="Klan kimliğini gösterir")
async def profil(interaction: discord.Interaction, uye: discord.Member = None):
    target = uye or interaction.user
    puan = klan_puani.get(target.id, 0)
    embed = discord.Embed(title=f"⚔️ {target.name} Klan Kartı", color=0x2f3136)
    embed.add_field(name="💰 Klan Puanı (KP)", value=f"`{puan} KP`", inline=True)
    embed.add_field(name="🏅 Rütbe", value="Savaşçı", inline=True)
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.set_footer(text="MesxeZe Ekonomi Sistemi")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="gonder", description="Üyeye klan puanı transfer eder")
async def gonder(interaction: discord.Interaction, uye: discord.Member, miktar: int):
    if miktar <= 0 or klan_puani.get(interaction.user.id, 0) < miktar:
        return await interaction.response.send_message("❌ Yetersiz bakiye veya hatalı miktar!", ephemeral=True)
    
    klan_puani[interaction.user.id] -= miktar
    klan_puani[uye.id] = klan_puani.get(uye.id, 0) + miktar
    await interaction.response.send_message(f"✅ {interaction.user.mention}, {uye.mention} adlı üyeye **{miktar} KP** başarıyla gönderdi!")

@bot.tree.command(name="top", description="Klanın en güçlü 10 üyesi")
async def top(interaction: discord.Interaction):
    sorted_list = sorted(klan_puani.items(), key=lambda x: x[1], reverse=True)[:10]
    desc = ""
    for i, (uid, pts) in enumerate(sorted_list, 1):
        m = interaction.guild.get_member(uid)
        name = m.mention if m else "Bilinmeyen"
        desc += f"**{i}.** {name} — `{pts} KP`\n"
    
    embed = discord.Embed(title="🏆 MesxeZe Şeref Kürsüsü", description=desc or "Henüz puan kazanan yok.", color=0xe74c3c)
    await interaction.response.send_message(embed=embed)

# --- YETKİLİ KOMUTLARI ---
@bot.tree.command(name="klan-duyuru", description="Resmi klan bildirisi yayınlar")
@app_commands.checks.has_permissions(administrator=True)
async def klan_duyuru(interaction: discord.Interaction, mesaj: str):
    embed = discord.Embed(title="📢 RESMİ KLAN BİLDİRİSİ", description=mesaj, color=0xf1c40f, timestamp=datetime.datetime.now())
    embed.set_author(name="MesxeZe Yönetim", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
    embed.set_footer(text="Bu duyuru @everyone etiketlidir.")
    await interaction.channel.send(content="@everyone", embed=embed)
    await interaction.response.send_message("✅ Duyuru yayınlandı.", ephemeral=True)

@bot.tree.command(name="temizle", description="Sohbeti temizler")
@app_commands.checks.has_permissions(manage_messages=True)
async def temizle(interaction: discord.Interaction, miktar: int):
    await interaction.channel.purge(limit=miktar)
    await interaction.response.send_message(f"🧹 `{miktar}` adet mesaj klan arşivinden silindi.", ephemeral=True)

# --- TICKET 2.0 (MODERN) ---
class TicketKapat(discord.ui.View):
    @discord.ui.button(label="Talebi Arşivle & Kapat", style=discord.ButtonStyle.danger, emoji="🔒")
    async def kapat(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 Kanal 3 saniye içinde imha ediliyor...")
        await interaction.channel.delete()

class DestekSelect(discord.ui.Select):
    def __init__(self):
        super().__init__(placeholder="Destek konusu seçiniz...", options=[
            discord.SelectOption(label="Klan Alımı", emoji="🛡️", description="Klanımıza katılmak için."),
            discord.SelectOption(label="Şikayet", emoji="⚠️", description="Bir sorun mu var?"),
            discord.SelectOption(label="Öneri", emoji="💡", description="Fikirlerini bizimle paylaş.")
        ])
    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        ch = await guild.create_text_channel(name=f"🎫-{interaction.user.name}", overwrites=overwrites)
        await interaction.response.send_message(f"✅ Talebin açıldı: {ch.mention}", ephemeral=True)
        
        embed = discord.Embed(title="🎫 Destek Talebi", description=f"Selam {interaction.user.mention}, **{self.values[0]}** konusu için buradayız.\nLütfen sorununuzu detaylıca yazın.", color=discord.Color.blurple())
        await ch.send(embed=embed, view=TicketKapat())

@bot.tree.command(name="destek", description="MesxeZe Destek menüsünü açar")
async def destek(interaction: discord.Interaction):
    view = discord.ui.View(); view.add_item(DestekSelect())
    await interaction.response.send_message("🛡️ **MesxeZe Destek Hattına Hoş Geldin**\nLütfen bir kategori seç:", view=view)

# --- EĞLENCE ---
@bot.tree.command(name="yazi-tura", description="Kaderini belirle!")
async def yazi_tura(interaction: discord.Interaction):
    sonuc = random.choice(["Yazı", "Tura"])
    await interaction.response.send_message(f"🪙 Para havada dönüyor... ve sonuç: **{sonuc}**!")

Thread(target=run).start()
bot.run(os.environ['TOKEN'])
