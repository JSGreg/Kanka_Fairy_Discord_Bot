import random
import discord
from discord import app_commands
from discord.ext import commands
import os
import requests
import re
import json
import asyncio
from pathlib import Path
from dotenv import load_dotenv



# TODO
# Search Function (https://app.kanka.io/api-docs/1.0/entities)
# Transfer page from one campaign to another
# Show viewing perms
# Make changes to viewing perms
# music
# dice
# Actual calendar
# Quests command 

REQUEST_PATH = "https://api.kanka.io/1.0/"
MSG_ENTITY_NOT_FOUND = "Entity not found."
MSG_REQUIRE_TOKEN = "Please provide token"
MSG_NO_MATCHING_CAMPAIGN = "Found no matching campaign. \nPlease check that server matches Kanka campaign"
REGEX_P = '<p.*?>|</p>'
REGEX_I = '<i.*?>|</i>'
REGEX_B = '<b.*?>|</b>'
REGEX_HR = '<hr.*?>'
REGEX_BR = '<br>'
REGEX_U = '<u.*?>|</u>'
REGEX_ALL = r'<[^>]+>'
REGEX_BRACKET = r'\[.*?:.*?\|'
REGEX_NBSP = r'(&nbsp;)'
REGEX_STRIKE = '<strike>|</strike>'
MIRALL_KANKA = "Mysteries of Mirall"
MIRALL_DISCORD = "Mirall Beach Academy"
ENTITY_TYPE = ["characters", "locations", "journals", "notes", "maps", "creatures"]

load_dotenv()

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print('Kanka Fairy is logged on'.format(bot))
    try: 
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

# Slash command intergration
# TODO
# Can set up so that each campaign is in its own file and replaced as needed (could store some info as backups incase something goes wrong)
# Figure out what the api actually has in it because the commands will have to be overhauled 
# Worry about permissions who is allowed to access what can solve by binding discord user names to kanka stuff? see who has viewing permissions in each page?
# if the entity does not exist update cache and try again? print error if still not there

# Try optimise later
@bot.tree.command(name = "wakeup")
async def wakeUp (interaction: discord.Interaction):
    await interaction.response.defer()
    
    member_list = interaction.guild.members
    campaign_id = get_campaignID_by_name(interaction)
    last_sync = "lastSync=2025-04-15T09:30:11.000000Z"

    # print(os.getenv(discord.Client.users[0] + "_TOKEN"))
    # entity_type = "entities?name=" 
    # serverID = get_campaignID_by_name(interaction)+"/"

    # loop through pages and get each 
    for members in member_list:
        player = members.name + "_TOKEN"
        if os.getenv(player) is not None:
            for type in ENTITY_TYPE:
                page = 1
                data = []
                print(members.name)
                print(type)
                while True: 
                    # url = f"{REQUEST_PATH}campaigns/{campaign_id}/{type}?page={page}&{last_sync}"
                    url = f"{REQUEST_PATH}campaigns/{campaign_id}/{type}?page={page}"
                    # url = f"{REQUEST_PATH}campaigns/{campaign_id}/{type}?{last_sync}"

                    headers = {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'Authorization': 'Bearer ' + os.getenv(player)
                    }
                    response = requests.request("GET", url, headers=headers)

                    if response.status_code != 200:
                        print(f"Error: {response.status_code} - {response.text}")
                        break
                    elif response.headers["Content-Type"] != "application/json":
                        print(f"Error: {response.status_code} - {response.headers['Content-Type']}")
                        break
                    print(response.headers['Content-Type'])
                    
                    response = response.json()
                    data.extend(response["data"])

                    if response["links"]["next"] is None:
                        print("Reached end of pages")
                        break

                    page+=1

                if not os.path.exists(f"./campaigns/{interaction.guild.name}/{members.name}"):
                    os.makedirs(f"./campaigns/{interaction.guild.name}/{members.name}")
                with open(f'./campaigns/{interaction.guild.name}/{members.name}/{type}.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)

                
                await asyncio.sleep(0)         
    print("Done")
    await interaction.followup.send("Hmph fine! I'M U[P]. I'll spill the tea but not because you asked!!!! :anger:")

@bot.tree.command(name = "flirt", description= "You're interested in me!? Oh you meant t̵̡̡̨̜̺͖̟̖̋̈͌͂̓̈́͊̃ḩ̸̫̼̠̘̪͔̮́͆̊̌͑̽̀̕̚͜͠ͅę̴̺̫̠̊̆̓͊͆̎̌̈́̚̕̕m̵̮͓̙͇͔̖̰͍͓̋͆̏͋͂͋̈́͘͝ ... ok no matter.")
async def flirt (interaction: discord.Interaction):
    await interaction.response.send_message(rand_line("flirt.txt"))

@bot.tree.command(name = "kmap", description="It's a bit dusty isn't it.")
@app_commands.describe(kmap_name = "Map name")
async def kmap (interaction: discord.Interaction, kmap_name: str):
    await interaction.response.defer()

    with open(f'./campaigns/{interaction.guild.name}/{interaction.user.name}/{ENTITY_TYPE[4]}.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        embed = None

        for entries in range(len(data)):
            print("Data: " + data[entries]["name"])
            print(re.search(kmap_name, data[entries]["name"], re.IGNORECASE))

            if re.search(kmap_name, data[entries]["name"], re.IGNORECASE):
                kmap_name, kmap_url, image_url = data[entries]["name"], data[entries]["urls"]["view"], data[entries]["image_full"]

                embed = dis_card(name=kmap_name, ent_url=kmap_url, image_url=image_url)
                break
        print(embed)
        if embed is None:
            await interaction.followup.send("Entity does not exist. Perhaps you spelt something wrong? Length error: " + kmap_name)
        await interaction.followup.send(embed=embed)
    return

# TODO
@bot.tree.command(name = "location", description="Oh yeah I've been there!")
@app_commands.describe(loc_name = "Location name")
async def location (interaction: discord.Interaction, loc_name: str):
    await interaction.response.defer()

    with open(f'./campaigns/{interaction.guild.name}/{interaction.user.name}/{ENTITY_TYPE[1]}.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        embed = None

        for entries in range(len(data)):
            print("Data: " + data[entries]["name"])
            print(re.search(loc_name, data[entries]["name"], re.IGNORECASE))

            if re.search(loc_name, data[entries]["name"], re.IGNORECASE):
                loc_name, entry, loc_url, image_url, is_private = data[entries]["name"], data[entries]["entry_parsed"], data[entries]["urls"]["view"], data[entries]["image_full"], data[entries]["is_private"]

                if interaction.guild.owner.name is interaction.user.name and is_private:
                    loc_name = loc_name + " :lock:"

                entry = body_parser(entry)
                embed = dis_card(name=loc_name, ent_url=loc_url, entry=entry, image_url=image_url)
                break
        print(embed)
        if embed is None:
            await interaction.followup.send("Entity does not exist. Perhaps you spelt something wrong? Length error: " + loc_name)
        await interaction.followup.send(embed=embed)

    return

# TODO
@bot.tree.command(name = "journal", description="No no! That's mine give it back!!!")
@app_commands.describe(journal_name = "Journal name")
async def journal (interaction: discord.Interaction, journal_name: str):
    await interaction.response.defer()

    with open(f'./campaigns/{interaction.guild.name}/{interaction.user.name}/{ENTITY_TYPE[2]}.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        embed = None

        for entries in range(len(data)):
            print("Data: " + data[entries]["name"])
            print(re.search(journal_name, data[entries]["name"], re.IGNORECASE))

            if re.search(journal_name, data[entries]["name"], re.IGNORECASE):
                journal_name, entry, journal_url, image_url, is_private = data[entries]["name"], data[entries]["entry_parsed"], data[entries]["urls"]["view"], data[entries]["image_full"], data[entries]["is_private"]
                
                if interaction.guild.owner.name is interaction.user.name and is_private:
                    journal_name = journal_name + " :lock:"
                
                entry = body_parser(entry)
                embed = dis_card(name=journal_name, ent_url=journal_url, entry=entry, image_url=image_url)
                break
        print(embed)
        if embed is None:
            await interaction.followup.send("Entity does not exist. Perhaps you spelt something wrong? Length error: " + journal_name)
        await interaction.followup.send(embed=embed)
    return


@bot.tree.command(name = "note", description="Peeking now? Scandalous!")
@app_commands.describe(note_name = "Note name")
async def note (interaction: discord.Interaction, note_name: str):
    await interaction.response.defer()

    with open(f'./campaigns/{interaction.guild.name}/{interaction.user.name}/{ENTITY_TYPE[3]}.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        embed = None

        for entries in range(len(data)):
            print("Data: " + data[entries]["name"])
            print(re.search(note_name, data[entries]["name"], re.IGNORECASE))

            if re.search(note_name, data[entries]["name"], re.IGNORECASE):
                note_name, entry, note_url, image_url, is_private= data[entries]["name"], data[entries]["entry_parsed"], data[entries]["urls"]["view"], data[entries]["image_full"], data[entries]["is_private"]
                
                if interaction.guild.owner.name is interaction.user.name and is_private:
                    note_name = note_name + " :lock:"

                entry = body_parser(entry)
                embed = dis_card(name=note_name, ent_url=note_url, entry=entry, image_url=image_url)
                break
        print(embed)
        if embed is None:
            await interaction.followup.send("Entity does not exist. Perhaps you spelt something wrong? Length error: " + note_name)
        await interaction.followup.send(embed=embed)
    return

# # TODO Can not complete due to API problems
# @bot.tree.command(name = "music", description="Brings up music")
# @app_commands.describe(music_name = "Music Category")
# async def music (interaction: discord.Interaction, music_name:str):
#     await interaction.response.send_message("Music?")

#     # await interaction.response.defer()
#     serverID = get_campaignID_by_name(interaction) + "/"
#     entity_type = "notes/"

#     music_url=""
#     music_info = api_call(os.getenv(interaction.user.name + '_TOKEN'), serverID, entity_type)
#     print(music_info)

#     for key in range(len(music_info["data"])):
#         if music_info["data"][key]["name"] == "Music":
#             music_url = music_info["data"][key]["urls"]["api"]

#     # print(music_info["data"][1]["name"])
#     print(music_url)

#     music_response = api_call_url(os.getenv(interaction.user.name + "_TOKEN"), music_url)

#     print(music_response)

#     return

# TODO
@bot.tree.command(name = "character", description="Are you looking for me?")
@app_commands.describe(character_name = "Character name")
async def character (interaction: discord.Interaction, character_name:str):
    await interaction.response.defer()

    with open(f'./campaigns/{interaction.guild.name}/{interaction.user.name}/{ENTITY_TYPE[0]}.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        embed = None

        for entries in range(len(data)):
            print("Data: " + data[entries]["name"])
            print(re.search(character_name, data[entries]["name"], re.IGNORECASE))
            
            if re.search(character_name, data[entries]["name"], re.IGNORECASE):
                character_name, entry, note_url, image_url, title, is_private = data[entries]["name"], data[entries]["entry_parsed"], data[entries]["urls"]["view"], data[entries]["image_full"], data[entries]["title"], data[entries]["is_private"]

                if interaction.guild.owner.name is interaction.user.name and is_private:
                    title = str(title) + " :lock:"
                entry = body_parser(entry)
                embed = dis_card(name=character_name, ent_url=note_url, entry=entry, title= title, image_url=image_url)
                
                break
        print(embed)
        if embed is None:
            await interaction.followup.send("Entity does not exist. Perhaps you spelt something wrong? Length error: " + character_name)
            
        await interaction.followup.send(embed=embed)
    return

# TODO
@bot.tree.command(name = "creature", description="No no! That's mine give it back!!!")
@app_commands.describe(creature_name = "Creature name")
async def creature (interaction: discord.Interaction, creature_name: str):
    await interaction.response.defer()

    with open(f'./campaigns/{interaction.guild.name}/{interaction.user.name}/{ENTITY_TYPE[5]}.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        embed = None

        for entries in range(len(data)):
            print("Data: " + data[entries]["name"])
            print(re.search(creature_name, data[entries]["name"], re.IGNORECASE))

            if re.search(creature_name, data[entries]["name"], re.IGNORECASE):
                creature_name, entry, creature_url, image_url, is_private = data[entries]["name"], data[entries]["entry_parsed"], data[entries]["urls"]["view"], data[entries]["image_full"], data[entries]["is_private"]
                
                if interaction.guild.owner.name is interaction.user.name and is_private:
                    creature_name = creature_name + " :lock:"
                
                entry = body_parser(entry)
                embed = dis_card(name=creature_name, ent_url=creature_url, entry=entry, image_url=image_url)
                break
        print(embed)
        if embed is None:
            await interaction.followup.send("Entity does not exist. Perhaps you spelt something wrong? Length error: " + creature_name)
        await interaction.followup.send(embed=embed)
    return


@bot.tree.command(name = "talk", description="Shh!")
@app_commands.describe(message = "Make a message")
async def character (interaction: discord.Interaction, message:str):
    print("Repeated message")
    if (interaction.user.name == "pom_pom_pom"):
        print ("I respond")
        await interaction.response.send_message(str(message))
    else:
        await interaction.response.send_message("Sorry! Can't hear you !!!")
    
    return

# TODO add an embed for titles
def dis_card(name, ent_url, entry="", title=None, image_url=""):
    if  title != None:
        name = name + " | " + title 
    embed = discord.Embed(title= name, url=ent_url, description= entry, color=0xff9b9b)
    embed.set_image(url=image_url)
    return embed

def body_parser(entry):
    if not entry == None:
        entry = re.sub(REGEX_BRACKET, "", entry)
        entry = re.sub(REGEX_I, "_ ", entry)
        entry = re.sub(REGEX_BR, "\n\n", entry)
        entry = re.sub(REGEX_B, "** ", entry)
        entry = re.sub(REGEX_HR, "\n", entry)
        entry = re.sub(REGEX_STRIKE, "~~ ", entry)
        entry = re.sub(REGEX_U, "__ ", entry)
        entry = re.sub(REGEX_P, " \n", entry)
        entry = re.sub(REGEX_ALL, "", entry)
        entry = re.sub(REGEX_NBSP, " ", entry)
    else:
        entry = "N/a"
    
    # if title == "":
    #     title = ""
    # else:
    #     title = "**" + title + "**\n\n"
    #     entry = title + entry
    return entry

# Get Kanka server by name, return campaignID
def get_campaignID_by_name(interaction:discord.Interaction):
    token = os.getenv(interaction.user.name + '_TOKEN')
    kanka_info = api_call(token)
    
    # Loops thorugh dict and matches server to campaign 
    for x in kanka_info["data"]:
        if (interaction.guild.name == MIRALL_DISCORD and str(x["name"]) == MIRALL_KANKA):
            campaignID = str(x["id"])
            return campaignID
        elif (interaction.guild.name == x["name"]):
            campaignID = str(x["id"])
            return campaignID

    print(MSG_NO_MATCHING_CAMPAIGN)
    return MSG_NO_MATCHING_CAMPAIGN

def api_call (token, campaign_id = "", entity_type = "", entity_name =""):
    url = REQUEST_PATH + "campaigns/" + campaign_id + entity_type + entity_name 
    print (url)
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + token
    }

    response = requests.request("GET", url, headers=headers)

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
    
    response = response.json()
    return response 

# def api_call_url(token, url):

#     headers = {
#         'Content-Type': 'application/json',
#         'Accept': 'application/json',
#         'Authorization': 'Bearer ' + token
#     }

#     response = requests.request("GET", url, headers=headers)
#     response = response.json()

#     return response 

def rand_line(file_name): 
    with open(file_name, 'r', encoding="utf-8") as file: 
        lines = file.readlines() 
        random_index = random.randrange(len(lines))
        random_line = lines[random_index] 
        random_line = "Ok fine then. Line " + str(random_index) + ": " + random_line
    return random_line 

bot.run(os.getenv('TOKEN'))