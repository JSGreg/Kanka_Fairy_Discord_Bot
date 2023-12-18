from logging import info
import discord
from discord import app_commands
from discord.ext import commands
import os
import requests


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

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# client = discord.Client(intents=discord.Intents.all())

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
    # print(api_call(user_name=os.getenv('pom_pom_pom_TOKEN')))
    await interaction.response.send_message(f"Hi {interaction.user.mention}!")

#TODO
@bot.tree.command(name = "flirt")
async def hello (interaction: discord.Interaction):
    await interaction.response.send_message(f"Hi {interaction.user.mention}!")


# TODO
@bot.tree.command(name = "map")
@app_commands.describe(map_name = "Map name")
async def kmap (interaction: discord.Interaction, map_name:str):
    return

# TODO
@bot.tree.command(name = "location")
@app_commands.describe(loc_name = "Location name")
async def location (interaction: discord.Interaction, loc_name: str):
    return

# TODO
@bot.tree.command(name = "journal")
@app_commands.describe(journal_name = "Journal name")
async def journal (interaction: discord.Interaction, journal_name: str):
    return

# TODO
@bot.tree.command(name = "note")
@app_commands.describe(note_name = "Note name")
async def note (interaction: discord.Interaction, note_name: str):
    return

# TODO
# Needs filters
@bot.tree.command(name = "character")
@app_commands.describe(character_name = "Character name")
async def character (interaction: discord.Interaction, character_name:str):
    serverID = get_campaignID_by_name(interaction) + "/"
    entity_type = "entities?name=" + character_name 

    # returns dict
    char_info = api_call(os.getenv(interaction.user.name + '_TOKEN'), serverID, entity_type)
    if "error" in char_info:
        print(char_info)
        # await interaction.response.send_message(char_info["error"])
        await interaction.response.send_message("There was an error")
        return

    #TODO use entity to search and filter then use character/quest/ect to find specific entity and format from there
    print(char_info)
    print(char_info["data"][0]["id"])
    print(char_info["data"][0]["name"])
    message = "Character Name: " + char_info["data"][0]["name"] + "Character id: " + str(char_info["data"][0]["id"])
    await interaction.response.send_message(message)
    return

    # ./campaigns endpoint dict syntax "kanka_info[data][campaign number][information]"
    # ./campaigns/{id} dict syntax "kanka_info[data][name]"
    # Can use this to verify which campaign player is in by server
    # TODO Will not use this form of calling to send campign info need to rewrite to skip campaign number
    # await message.channel.send(server ["data"][0]["id"])

# TODO
# Get Kanka server by name 
# return campaignID

def get_campaignID_by_name(interaction:discord.Interaction):
    token = os.getenv(interaction.user.name + '_TOKEN')
    kanka_info = api_call(token)
    
    # Loops thorugh dict and matches server to campaign 
    for x in kanka_info["data"]:
        if (interaction.guild.name == x["name"]):
            # print ("this is the kanka campaign:" + x["name"])
            # Converts int to string
            campaignID = str(x["id"])
            return campaignID

    return MSG_NO_MATCHING_CAMPAIGN


# May need to make a seperate api call for entities and characters
# ^  Don't forget that all endpoints documented here need to be prefixed with "1.0/campaigns/{campaign.id}/."
def api_call (token, campaign_id = "", entity_type = "", entity_name =""):
    url = REQUEST_PATH + "campaigns/" + campaign_id + entity_type + entity_name # here we add variable to specific sections? can add campaign id to the end of url to specify among every campaign stored on kanka
    # url = "https://api.kanka.io/1.0/campaigns/176953/characters/3952731"
    print (url)
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + token
    }

    response = requests.request("GET", url, headers=headers)
    response = response.json()

    return response 

bot.run(os.getenv('TOKEN'))
