import discord
import os
from dotenv import load_dotenv
import sqlite3
import datetime
from PIL import Image, ImageFont, ImageDraw

load_dotenv()
bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}.")

testingservers = [252772525790986240]

@bot.slash_command(guild_ids=testingservers, name="work", description="Check to see if im online")
async def work(ctx):
    await ctx.respond(f"I'm working! Latency: {bot.latency * 1000}ms.")

@bot.slash_command(guild_ids=testingservers, name="about", description="About this bot")
async def about(ctx):
    aboutEmbed=discord.Embed(title="About Irminsul", description="Irminsul is a bot based on the game Genshin Impact made by Hoyoverse. It allows its users to build friendships with fictional characters and unlock chatlines with them. The service is entirely free and we do not own credit of any characters referenced in this bot.", color=0x0581f5)
    aboutEmbed.add_field(name="New Update!", value="Currently working on characters, chatlines, and user database.", inline=True)
    await ctx.respond(embed=aboutEmbed)

#######################################PROFILE MODIFICATION#######################################
#tuple with single element -> ('abc',)
def profile_check(user):
    db = sqlite3.connect("./data/user.db")
    cursor = db.cursor()
    cursor.execute("SELECT ownedChara FROM user WHERE uid = ?", (str(user.id),))
    result = cursor.fetchone()
    if result is None:
        cursor.execute("INSERT INTO user(uid) VALUES(?)", (str(user.id),))
    db.commit()
    cursor.close()
    db.close()
    return

@bot.slash_command(guild_ids=testingservers, name="profile", description="Show your own profile of Irminsul (unless your a descender)")
async def profile(ctx):
    profile_check(ctx.author)
    db = sqlite3.connect("./data/user.db")
    cursor = db.cursor()
    cursor.execute("SELECT ownedChara, favChara, primo FROM user WHERE uid = ?", (str(ctx.author.id),))
    uOChara, uFChara, uPrimo = cursor.fetchone()
    uOChara = "None" if uOChara is None or uOChara == "" else "\n".join(uOChara.split(","))
    uFChara = "None" if uFChara is None or uFChara == "" else "\n".join(uFChara.split(","))
    db.commit()
    cursor.close()
    db.close()
    embed=discord.Embed(title="Profile", description=f"Below are the information about {ctx.author.name}#{ctx.author.discriminator}")
    embed.set_thumbnail(url=f"{ctx.author.avatar.url}")
    embed.add_field(name="Primo", value=f"{uPrimo}", inline=False)
    embed.add_field(name="Owned Characters", value=f"{uOChara}", inline=True)
    embed.add_field(name="Favorite Characters", value=f"{uFChara}", inline=True)
    await ctx.respond(embed=embed)

@bot.slash_command(guild_ids=testingservers, name="fav", description="Modify your favtorite character list")
async def fav(ctx, method=discord.Option(choices=["add", "remove"]), character=discord.Option(input_type=str)):
    profile_check(ctx.author)
    db = sqlite3.connect("./data/user.db")
    cursor = db.cursor()
    cursor.execute("SELECT ownedChara, favChara FROM user WHERE uid = ?", (str(ctx.author.id),))
    uOChara, uFChara = cursor.fetchone()
    uOChara = [] if uOChara is None or uOChara == "" else uOChara.split(",")
    uFChara = [] if uFChara is None or uFChara == "" else uFChara.split(",")
    if character not in uOChara:
        await ctx.respond("You do not own this character or you did not put in a proper argument!")
    elif character in uFChara and method == "add":
        await ctx.respond("The character is already in your favorite list!")
    elif character not in uFChara and method == "remove":
        await ctx.respond("The character isn't in your favorite list!")
    else:
        if method == "add":
            uFChara.append(character)
            uFChara = ",".join(uFChara)
        elif method == "remove":
            uFChara.remove(character)
            uFChara = ",".join(uFChara)
        await ctx.respond("Modification successful!")
    cursor.execute("UPDATE user SET favChara = ? WHERE uid = ?", (uFChara, str(ctx.author.id))) 
    db.commit()
    cursor.close()
    db.close()

##############################################SHOP#################################################
@bot.slash_command(guild_ids=testingservers, name="shop", description="Visit the shop with lack of primos")
async def shop(ctx, catagory=discord.Option(choices=["character", "chatline"])):
    profile_check(ctx.author)
    if catagory == "chatline":
        db = sqlite3.connect("./data/shop.db")
        cursor = db.cursor()
        cursor.execute("SELECT * FROM shop WHERE itemID < 11")
        output = cursor.fetchall()
        output = "\n".join([f"{'ID: ' + str(c[0]):<10}" + f"{'Name: ' + str(c[1]):<45}" + f"{'Price: ' + str(c[2]):<10}" for c in output])
    elif catagory == "character":
        db = sqlite3.connect("./data/shop.db")
        cursor = db.cursor()
        cursor.execute("SELECT * FROM shop WHERE itemID > 10 AND itemID < 1000")
        output = cursor.fetchall()
        output = "\n".join([f"{'ID: ' + str(c[0]):<10}" + f"{'Name: ' + str(c[1]):<45}" + f"{'Price: ' + str(c[2]):<10}" for c in output])
    else:
        await ctx.respond("You did not pick an option!")
        return
    db.commit()
    cursor.close()
    db.close()
    await ctx.respond(output)
    

@bot.slash_command(guild_ids=testingservers, name="purchase", description="Exchange for what you want with enough primos")
async def purchase(ctx, catagory=discord.Option(choices=["character", "chatline"]), itemid=discord.Option(input_type=int)):
    profile_check(ctx.author)
    if catagory == "chatline" and itemid is not None:
        pass
    elif catagory == "character" and itemid is not None:
        pass
    else:
        ctx.respond("Please choose a proper catagory and item ID!")
        return

def countdown(stop):
    difference = stop - datetime.datetime.now()
    count_hours, rem = divmod(difference.seconds, 3600)
    count_minutes, count_seconds = divmod(rem, 60)
    for i in [difference.days, count_hours, count_minutes, count_seconds]:
      if i <= 0:
        i = 0
    return f"{difference.days}", f"{count_hours}", f"{count_minutes}"
@bot.slash_command(guild_ids=testingservers, name="countdown", description="Furina banner countdown!")
async def purchase(ctx):
    endtime = datetime.datetime(2023, 11, 8, 10, 0, 0) #modifying end date (you may modify it according to timezone for different coding platforms)
    if endtime <= datetime.datetime.now():
        await ctx.respond("Focalors is here! Now go pull for her~")
        return
    end_d, end_h, end_m = countdown(endtime) #you may add `end_s` if needed
    font = ImageFont.truetype("Blue Yellow.ttf", 270) #importing font
    cd_image = Image.open("countdown_template.png") #importing countdown picture template
    edit_cd = ImageDraw.Draw(cd_image) #start editing picture with our countdown variables
    edit_cd.text((293,476), str(end_d), font=font, anchor="mm") #you may modify their coordinates if template was changed
    edit_cd.text((765,476), str(end_h), font=font, anchor="mm")
    edit_cd.text((1237,476), str(end_m), font=font, anchor="mm")
    #edit_cd.text((x,y), str(end_s), font=font) #this may be enabled if seconds countdown is required
    cd_image.save("edited_cd.png") #save the edited picture
    await ctx.respond("", file=discord.File('edited_cd.png')) #call the edited picture file and send it in channel

bot.run(os.getenv('TOKEN'))