import discord
import os
import random
import requests
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
bot.run("TOKENİ_BURAYA_YAZIN")
