import asyncio
import os
import random
import shutil
import discord
import yt_dlp as youtube_dl
from discord.ext import commands

# ==========================================
# 1. YARDIMCI FONKSİYONLAR
# ==========================================

def emoji_olusturucu():
    emojiler = ["😀", "😎", "🤖", "🚀", "🔥", "🎉", "🐍", "💻"]
    return random.choice(emojiler)

def sifre_olusturucu(uzunluk=10):
    karakterler = "+-/*!&$#?=@abcdefghijklnopqrstuvwxynzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    return "".join(random.choice(karakterler) for _ in range(uzunluk))

def yazi_tura_sonucu(secim):
    sonuc = random.choice(["yazı", "tura"])
    if secim.lower() == sonuc:
        return f"Sonuç: **{sonuc}**! Kazandın! 🎉"
    return f"Sonuç: **{sonuc}**! Kaybettin. 😅"

def bilmece_sec():
    bilmeceler = [
        ("Uzaktan baktım bir taş, yanına gittim dört ayak bir baş.", "Kaplumbağa"),
        ("Karnı tok, sırtı pek, ne söylerse dinletir pek.", "Davul"),
        ("Benim bir kuyum var, iki türlü suyu var.", "Yumurta"),
        ("Gökte gördüm köprü, rengi yedi türlü.", "Gökkuşağı"),
        ("Akşam baktım çok idi, sabah baktım yok idi.", "Yıldız")
    ]
    
    soru, cevap = random.choice(bilmeceler)
    return soru, cevap

# ==========================================
# 2. YOUTUBE VE FFMPEG YAPILANDIRMASI
# ==========================================

youtube_dl.utils.bug_reports_message = lambda *args, **kwargs: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


def get_ffmpeg_executable():
    """Önce scriptin yanındaki ffmpeg.exe'yi, yoksa sistem PATH yolunu arar."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    local_ffmpeg = os.path.join(script_dir, 'ffmpeg.exe')
    if os.path.isfile(local_ffmpeg):
        return local_ffmpeg
    return shutil.which('ffmpeg') or 'ffmpeg'


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        search_query = url if url.startswith("http") else f"ytsearch1:{url}"

        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(search_query, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        ffmpeg_bin = get_ffmpeg_executable()

        return cls(discord.FFmpegPCMAudio(filename, executable=ffmpeg_bin, **ffmpeg_options), data=data)


# ==========================================
# 3. BOT BAŞLATMA
# ==========================================

intents = discord.Intents.default()
intents.message_content = True

# Hem ! hem $ ile komut çağrılabilir
bot = commands.Bot(command_prefix=['!', '$'], intents=intents)


@bot.event
async def on_ready():
    print(f'🤖 Diskodland göreve hazır: {bot.user}')
    print(f'🔧 FFmpeg konumu: {get_ffmpeg_executable()}')
    print('-----------------------------------------')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return  # Tanımlı olmayan komutlarda kanala hata yazıp kirletmesin
    print(f"--> KOMUT HATASI: {error}")
    await ctx.send(f"⚠️ Hata: `{error}`")


# ==========================================
# 4. EĞLENCE & KODLAND KOMUTLARI
# ==========================================

@bot.command()
async def merhaba(ctx):
    """Basit selamlama komutu"""
    await ctx.send(f"Selam {ctx.author.mention}! Ben **Diskodland**, Kodland projeleri için buradayım! 🚀")

@bot.command()
async def emoji(ctx):
    """Rastgele emoji gönderir"""
    await ctx.send(emoji_olusturucu())

@bot.command()
async def para(ctx, secim: str = None):
    """Yazı-tura atar: !para yazı veya !para tura"""
    if not secim or secim.lower() not in ["yazı", "tura"]:
        await ctx.send("Lütfen tahminini belirt! Örnek: `!para yazı` veya `$para tura`")
        return
    await ctx.send(yazi_tura_sonucu(secim))

@bot.command()
async def sifre(ctx, uzunluk: int = 10):
    """Belirtilen uzunlukta güvenli şifre üretir: !sifre 12"""
    if uzunluk > 50:
        await ctx.send("Şifre uzunluğu en fazla 50 olabilir!")
        return
    await ctx.send(f"🔑 Oluşturulan şifren: `{sifre_olusturucu(uzunluk)}`")

@bot.command()
async def zar(ctx):
    """1-6 arası zar atar"""
    gelen = random.randint(1, 6)
    await ctx.send(f"🎲 Zar atıldı: **{gelen}** geldi!")

@bot.command()
async def bilmece(ctx):
    """Rastgele bilmece soruyor"""
    soru, cevap = bilmece_sec()
    await ctx.send(f"🧩 **Bilmece:** {soru}\n||Cevap: {cevap}||")

# ==========================================
# 5. SES KANALINDA MÜZİK ÇALMA KOMUTLARI
# ==========================================

@bot.command()
async def yt(ctx, *, url):
    """YouTube'da arar ve ses kanalında çalar: !yt şarkı adı"""
    if ctx.voice_client is None:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("Önce bir ses kanalına girmelisin!")
            return
    elif ctx.voice_client.is_playing():
        ctx.voice_client.stop()

    await ctx.send(f"🔍 **{url}** aranıyor...")
    try:
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print(f'Çalma hatası: {e}') if e else None)
        await ctx.send(f'🎶 Çalıyor: **{player.title}**')
    except Exception as e:
        print(f"HATA: {e}")
        await ctx.send(f"❌ Şarkı çalınamadı: `{e}`")

@bot.command()
async def stop(ctx):
    """Müziği durdurur ve kanaldan ayrılır"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Ses kanalından ayrıldım.")
    else:
        await ctx.send("Zaten bir ses kanalında değilim.")


# ==========================================
# 6. SOHBETE DİREKT VİDEO GETİRME KOMUTU
# ==========================================

@bot.command(name="video", aliases=["vid", "izle"])
async def video_ara(ctx, *, arama_metni: str):
    """YouTube'da arama yapar ve videoyu doğrudan sohbette açar: !video kedi videoları"""
    await ctx.send(f"🔍 **{arama_metni}** için video aranıyor...")
    
    try:
        loop = bot.loop or asyncio.get_event_loop()
        arama_sorgusu = f"ytsearch1:{arama_metni}"
        
        # İndirme yapmadan sadece video verisini çeker (hızlıdır)
        data = await loop.run_in_executor(
            None, 
            lambda: ytdl.extract_info(arama_sorgusu, download=False)
        )
        
        if 'entries' in data and data['entries']:
            video = data['entries'][0]
            video_url = video.get('webpage_url')
            video_baslik = video.get('title')
            
            # Linki chate gönderir; Discord otomatik gömülü video oynatıcıya çevirir
            await ctx.send(f"🎬 **{video_baslik}**\n{video_url}")
        else:
            await ctx.send("❌ Aradığın kritere uygun bir video bulunamadı.")
            
    except Exception as e:
        print(f"Video Arama Hatası: {e}")
        await ctx.send(f"⚠️ Video getirilirken hata oluştu: `{e}`")


# ==========================================
# 7. BOT ÇALIŞTIRMA
# ==========================================

TOKEN = "tokenı yaz"
bot.run(TOKEN)
