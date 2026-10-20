import discord
import os
import random
import requests
import urllib.parse
# Discord botları için komut tabanlı bir framework sağlar.
# Bu framework sayesinde, botumuzun belirli komutlara yanıt vermesini kolayca tanımlayabiliriz.
from discord.ext import commands


intents = discord.Intents.default()
intents.message_content = True  # botun mesaj içeriğine erişimini aktif hale getiriyoruz

bot = commands.Bot(command_prefix='$', intents=intents)

# Bu özellik, botun kendisine gönderilen komutları tanıması için bir ön ek tanımlar.
# $ işareti komut ön eki olarak belirlenmiştir. Yani bot sadece $ ile başlayan komutları algılar.


@bot.event  # bot belirli bir olay gerçekleştiğinde tetiklensin.
async def on_ready():  # bot başarılı bir şekilde Discord'a bağlandığında tetiklenir
    print(f'{bot.user} olarak giriş yaptık')
@bot.command()
async def mem(ctx):
    img_name = random.choice(os.listdir("images"))
    with open(f'images/{img_name}', 'rb') as f:
        # Dönüştürülen Discord kütüphane dosyasını bu değişkende saklayalım!
        picture = discord.File(f)
   # Daha sonra bu dosyayı bir parametre olarak gönderebiliriz!
    await ctx.send(file=picture)
    # Dosya adını bir değişkenden bu şekilde değiştirebilirsiniz!
def get_duck_image_url():    
    url = 'https://random-d.uk/api/random'
    res = requests.get(url)
    data = res.json()
    return data['url']


@bot.command('duck')
async def duck(ctx):
    '''duck komutunu çağırdığımızda, program ordek_resmi_urlsi_al fonksiyonunu çağırır.'''
    image_url = get_duck_image_url()
    await ctx.send(image_url)

def get_dog_image_url():    
    url = 'https://random.dog/woof.json'
    res = requests.get(url)
    data = res.json()
    return data['url']

"""https://kitsu.io/api/edge/anime/9135"""
@bot.command('dog')
async def dog(ctx):
    '''dog komutunu çağırdığımızda, program kopek_resmi_urlsi_al fonksiyonunu çağırır.'''
    image_url = get_dog_image_url()
    await ctx.send(image_url)

def get_anime_image_url(anime_adi):    
    url = f'https://kitsu.io/api/edge/anime?filter[text]={anime_adi}'
    res = requests.get(url)
    data = res.json()
    
    if not data.get('data'):
        return None
        
    return data['data'][0]['attributes']['posterImage']['original']

@bot.command('anime')
async def anime(ctx, *, anime_adi: str = "tokyo"):
    '''Kullanıcı isim yazmazsa varsayılan olarak tokyo arar, yazarsa o animeyi getirir.'''
    image_url = get_anime_image_url(anime_adi)
    
    if image_url:
        await ctx.send(image_url)
    else:
        await ctx.send(f"'{anime_adi}' adında bir anime bulunamadı!")

def get_futbolcu_bilgi(oyuncu_adi):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # 1. Adım: Arama terimine 'futbolcu' ekleyip Wikipedia'da doğrudan aratıyoruz
    search_url = "https://tr.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": f"{oyuncu_adi} futbolcu",
        "format": "json"
    }
    
    try:
        r = requests.get(search_url, params=params, headers=headers, timeout=5)
        data = r.json()
        search_results = data.get("query", {}).get("search", [])
        
        # Sonuç bulunamazsa sadece girdiği ismi arat
        if not search_results:
            params["srsearch"] = oyuncu_adi
            r = requests.get(search_url, params=params, headers=headers, timeout=5)
            data = r.json()
            search_results = data.get("query", {}).get("search", [])
            
        if not search_results:
            return None
            
        # İlk sonucun tam sayfa başlığını al
        page_title = search_results[0]["title"]
        
        # 2. Adım: Başlığın özetini ve görselini çek
        summary_url = f"https://tr.wikipedia.org/api/rest_v1/page/summary/{page_title}"
        sum_res = requests.get(summary_url, headers=headers, timeout=5)
        sum_data = sum_res.json()
        
        return {
            "isim": sum_data.get("title"),
            "ozet": sum_data.get("extract"),
            "foto": sum_data.get("thumbnail", {}).get("source")
        }
    except Exception as e:
        print(f"Hata detayı: {e}")
        return None

@bot.command('futbolcu')
async def futbolcu(ctx, *, isim: str):
    bilgi = get_futbolcu_bilgi(isim)
    
    if not bilgi or not bilgi.get('ozet'):
        await ctx.send(f"**{isim}** bulunamadı.")
        return
        
    metin = bilgi['ozet']
    if len(metin) > 450:
        metin = metin[:450] + "..."
        
    embed = discord.Embed(
        title=bilgi['isim'], 
        description=metin,
        color=discord.Color.green()
    )
    if bilgi.get('foto'):
        embed.set_image(url=bilgi['foto'])
        
    await ctx.send(embed=embed)
bot.run("TOKENİ_BURAYA_YAZIN")
