import os
import discord
from dotenv import load_dotenv
import datetime #required for countdown calculation
from PIL import Image, ImageFont, ImageDraw #required for image import, image font import, editing image

load_dotenv()
bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}.")

#put your server id here
testingservers = ['SERVER_ID']

#this function takes in ending datetime, returns countdown (ending days, ending hours, ending minutes as separate variables)
def countdown(stop):
    difference = stop - datetime.datetime.now()
    count_hours, rem = divmod(difference.seconds, 3600)
    count_minutes, count_seconds = divmod(rem, 60)
    for i in [difference.days, count_hours, count_minutes, count_seconds]:
      if i <= 0:
        i = 0
    return f"{difference.days}", f"{count_hours}", f"{count_minutes}"

@bot.slash_command(guild_ids=testingservers, name="countdown", description="Furina banner countdown!")
async def countdown(ctx):
    endtime = datetime.datetime(2023, 11, 8, 10, 0, 0) #modifying end date (you may modify it according to timezone for different coding platforms)
    if endtime <= datetime.datetime.now():
        await ctx.respond("**Furina is here! Now go pull for her!**")
        return
    end_d, end_h, end_m = countdown(endtime) #you may add `end_s` if needed
    font = ImageFont.truetype("Blue Yellow.ttf", 270) #importing font
    cd_image = Image.open("countdown_template.png") #importing countdown picture template
    edit_cd = ImageDraw.Draw(cd_image) #start editing picture with our countdown variables
    edit_cd.text((293,476), str(end_d), font=font, anchor="mm") #you may modify their coordinates if template was changed
    edit_cd.text((765,476), str(end_h), font=font, anchor="mm")
    edit_cd.text((1237,476), str(end_m), font=font, anchor="mm")
    cd_image.save("edited_cd.png") #save the edited picture
    await ctx.respond("", file=discord.File('edited_cd.png')) #call the edited picture file and send it in channel

bot.run(os.getenv('TOKEN'))
