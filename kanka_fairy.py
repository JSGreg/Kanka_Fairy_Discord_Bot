from logging import info
import discord
from discord import app_commands
from discord.ext import commands
import os
import requests
import re


# TODO
# Message for generating tokens 
# Ping Kanka
# Get server specific info by name
# Get kanka campaign by name not id (Needs to be a special funciton)
# Search Function (https://app.kanka.io/api-docs/1.0/entities)
# Set variables earlier 


REQUEST_PATH = "https://api.kanka.io/1.0/"
MSG_ENTITY_NOT_FOUND = "Entity not found."
MSG_REQUIRE_TOKEN = "Please provide token"
MSG_NO_MATCHING_CAMPAIGN = "Found no matching campaign. \nPlease check that server matches Kanka campaign"
REGEX_P = '<p.*?>|</p>'
REGEX_I = '<i.*?>|</i>'
REGEX_B = '<b.*?>|</b>'
REGEX_HR = '<hr.*?>'
REGEX_BR = '<br>'
REGEX_ALL = r'<[^>]+>'
# REGEX_BRACKET = r'\[.*?:.*?\|.*?\],|\[.*?:.*?\],'
REGEX_BRACKET = r'\[.*?:.*?\|'
REGEX_NBSP = r'(&nbsp;)'
# |\s-(&nbsp;)?\s*)'


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
@bot.tree.command(name = "hello")
async def hello (interaction: discord.Interaction):
    await interaction.response.send_message(f"Hi {interaction.user.mention}!")

#TODO
@bot.tree.command(name = "flirt")
async def hello (interaction: discord.Interaction):
    await interaction.response.send_message(f"Hi {interaction.user.mention}!")


# TODO
@bot.tree.command(name = "map", description="Bring up the map. No Input needed")
# @app_commands.describe(map_name = "Map name")
async def kmap (interaction: discord.Interaction):
    await interaction.response.defer()
    serverID = get_campaignID_by_name(interaction) + "/"
    entity_type = "maps/"

    map_info = api_call(os.getenv(interaction.user.name + '_TOKEN'), serverID, entity_type)
    map_url = map_info["data"][0]["image_full"]
    kanka_url = map_info["data"][0]["urls"]["view"]

    await interaction.followup.send("" + map_url)
    await interaction.followup.send("Kanka Link: " + kanka_url)

    return

# TODO
@bot.tree.command(name = "location")
@app_commands.describe(loc_name = "Location name")
async def location (interaction: discord.Interaction, loc_name: str):
    await interaction.response.defer()
    serverID = get_campaignID_by_name(interaction) + "/"
    entity_type = "entities?name=" + loc_name

    # returns dict
    loc_info = api_call(os.getenv(interaction.user.name + '_TOKEN'), serverID, entity_type)

    if len(loc_info) == 0:
        await interaction.followup.send("Entity does not exist. Perhaps you spelt something wrong?")
        return
    
    if len(loc_info["data"]) == 0:
        await interaction.followup.send("Entity does not exist. Perhaps you spelt something wrong?")
        return
    
    if "error" in loc_info:
        await interaction.followup.send("Output Error")
        return
    
    if loc_info["data"][0]["type"] != "location":
        await interaction.followup.send("No locations found using input '" + loc_name + "'")
        return

    print(loc_info)
    loc_url = loc_info["data"][0]["urls"]["view"]
    loc_name = loc_info["data"][0]["name"]
    message = "# " + loc_name + "\n" + loc_url
    await interaction.followup.send(message)
    
    return

# TODO
@bot.tree.command(name = "journal", description="Search by name")
@app_commands.describe(journal_name = "Journal name")
async def journal (interaction: discord.Interaction, journal_name: str):
    await interaction.response.defer()
    serverID = get_campaignID_by_name(interaction) + "/"
    entity_type = "entities?name=" + journal_name

    # returns dict
    journal_info = api_call(os.getenv(interaction.user.name + '_TOKEN'), serverID, entity_type)

    if len(journal_info) == 0:
        await interaction.followup.send("Entity does not exist. Perhaps you spelt something wrong?")
        return
    
    if len(journal_info["data"]) == 0:
        await interaction.followup.send("Entity does not exist. Perhaps you spelt something wrong?")
        return
    
    if "error" in journal_info:
        await interaction.followup.send("Output Error")
        return
    
    if journal_info["data"][0]["type"] != "journal":
        await interaction.followup.send("No journals found using input '" + journal_name + "'")
        return

    print(journal_info)
    journal_url = journal_info["data"][0]["urls"]["view"]
    journal_name = journal_info["data"][0]["name"]
    message = "# " + journal_name + "\n" + journal_url
    await interaction.followup.send(message)
    
    return

# TODO
@bot.tree.command(name = "note")
@app_commands.describe(note_name = "Note name")
async def note (interaction: discord.Interaction, note_name: str):
    await interaction.response.defer()
    serverID = get_campaignID_by_name(interaction) + "/"
    entity_type = "entities?name=" + note_name

    note_info = api_call(os.getenv(interaction.user.name + '_TOKEN'), serverID, entity_type)

    if len(note_info) == 0:
        await interaction.followup.send("Entity does not exist. Perhaps you spelt something wrong?")
        return
    
    if len(note_info["data"]) == 0:
        await interaction.followup.send("Entity does not exist. Perhaps you spelt something wrong?")
        return
    
    if "error" in note_info:
        await interaction.followup.send("Output Error")
        return
    
    if note_info["data"][0]["type"] != "note":
        await interaction.followup.send("No note found using input '" + note_name + "'")
        return
    
    note_response = api_call_url(os.getenv(interaction.user.name + '_TOKEN'), note_info["data"][0]["urls"]["api"])

    # print(note_response)
    note_name = note_response["data"]["name"]
    note_url = note_response["data"]["urls"]["view"]
    entry = note_response["data"]["entry_parsed"]
    image_url = note_response["data"]["image_full"]


    print("Entry Before" + entry)

    entry = body_parser(entry)

    embed = dis_card(name=note_name, ent_url=note_url, entry=entry, title= "", image_url=image_url)

    await interaction.followup.send(embed=embed)


    # await interaction.followup.send(message)

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
@bot.tree.command(name = "character")
@app_commands.describe(character_name = "Character name")
async def character (interaction: discord.Interaction, character_name:str):
    await interaction.response.defer()
    message = "N/a"
    serverID = get_campaignID_by_name(interaction) + "/"
    entity_type = "entities?name=" + character_name 

    # returns dict
    char_info = api_call(os.getenv(interaction.user.name + '_TOKEN'), serverID, entity_type)

    if len(char_info) == 0:
        await interaction.followup.send("Entity does not exist. Perhaps you spelt something wrong?")
        return
    
    if len(char_info["data"]) == 0:
        await interaction.followup.send("Entity does not exist. Perhaps you spelt something wrong?")
        return
    
    if "error" in char_info:
        await interaction.followup.send("Output Error")
        return
    
    if char_info["data"][0]["type"] != "character":
        await interaction.followup.send("No characters found using input '" + character_name + "'")
        return

    # entity_type = "character/"

    # Can get the api url for charactes from the entities api response
    char_response = api_call_url(os.getenv(interaction.user.name + '_TOKEN'), char_info["data"][0]["urls"]["api"])

    # print("Entry Before" + entry)

   
    # Parses HTML tags out of entries
    entry = char_response["data"]["entry_parsed"]
    title = char_response["data"]["title"]
    name = char_response["data"]["name"]
    char_url = char_response["data"]["urls"]["view"]
    image_url=char_response["data"]["image_full"]


    entry, title = body_parser(entry, title)

    embed = dis_card(name, char_url, entry, title, image_url)
    await interaction.followup.send(embed=embed)

    return

    # ./campaigns endpoint dict syntax "kanka_info[data][campaign number][information]"
    # ./campaigns/{id} dict syntax "kanka_info[data][name]"
    # Can use this to verify which campaign player is in by server
    # await message.channel.send(server ["data"][0]["id"])


def dis_card(name, ent_url, entry, title="", image_url=""):
    embed = discord.Embed(title= name, url=ent_url)
    embed.add_field(name="", value=title, inline=False)

    embed.add_field(name="Entry", value = entry, inline = True)
    embed.set_image(url=image_url)
    return embed

def body_parser(entry, title=""):
    if not entry == None:
        entry = re.sub(REGEX_BRACKET, "", entry)
        entry = re.sub(REGEX_I, "_ ", entry)
        entry = re.sub(REGEX_BR, "\n\n", entry)
        entry = re.sub(REGEX_B, "** ", entry)
        entry = re.sub(REGEX_HR, "\n\n", entry)
        entry = re.sub(REGEX_P, "", entry)
        entry = re.sub(REGEX_ALL, "", entry)
        entry = re.sub(REGEX_NBSP, " ", entry)

        print("Entry After" + entry)
    else:
        entry = "N/a"
    
    if title == None:
        title = ""
    else:
        title = "**" + title + "**"

    return entry, title

# Get Kanka server by name, return campaignID
def get_campaignID_by_name(interaction:discord.Interaction):
    token = os.getenv(interaction.user.name + '_TOKEN')
    kanka_info = api_call(token)
    
    # Loops thorugh dict and matches server to campaign 
    for x in kanka_info["data"]:
        if (interaction.guild.name == x["name"]):
            campaignID = str(x["id"])
            return campaignID

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
    response = response.json()

    return response 

def api_call_url(token, url):

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + token
    }

    response = requests.request("GET", url, headers=headers)
    response = response.json()

    return response 

bot.run(os.getenv('TOKEN'))
