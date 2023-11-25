from html import entities
from logging import info
import discord
import os
import requests
import json

# TODO
# Message for generating tokens 
# Ping Kanka
# Get server specific info by name
# Get kanka campaign by name not id (Needs to be a special funciton)
# Search Function (https://app.kanka.io/api-docs/1.0/entities)
# Set variables earlier 


REQUEST_PATH = "https://kanka.io/api/1.0/"
MSG_ENTITY_NOT_FOUND = "Entity not found."
MSG_REQUIRE_TOKEN = "Please provide token"
MSG_NO_MATCHING_CAMPAIGN = "Found no matching campaign. \nPlease check that server matches Kanka campaign"

client = discord.Client(intents=discord.Intents.all())

@client.event

async def on_ready():
    print('Kanka Fairy is logged on'.format(client))

@client.event
async def on_message (message:discord.Message):
    if (message.author == client.user):
        return
    if (message.content.startswith('$hello')):
        await message.channel.send('Hello')
    # if (message.author.roles == message.author.roles):
    
    #
    server = get_campaignID_by_name(message)

    # print(kanka_info ["data"]["name"])
    print("this is the server:" + message.guild.name)

    await message.channel.send(server["id"])
    # ./campaigns endpoint dict syntax "kanka_info[data][campaign number][information]"
    # ./campaigns/{id} dict syntax "kanka_info[data][name]"
    # Can use this to verify which campaign player is in by server
    # TODO Will not use this form of calling to send campign info need to rewrite to skip campaign number
    # await message.channel.send(server ["data"][0]["id"])

# TODO
# Get Kanka server by name 
# return campaignID

def get_campaignID_by_name(message:discord.Message):
    kanka_info = api_call(os.getenv(message.author.name + '_TOKEN'))
    
    # Loops thorugh dict and matches server to campaign 
    # returns campaignID
    for x in kanka_info["data"]:
        if (message.guild.name == x["name"]):
            print ("this is the kanka campaign:" + x["name"])
            return x

    return MSG_NO_MATCHING_CAMPAIGN


# May need to make a seperate api call for entities and characters
# ^  Don't forget that all endpoints documented here need to be prefixed with "1.0/campaigns/{campaign.id}/."
def api_call (user_name, campaign_id = "", entity = ""):
    url = REQUEST_PATH + "campaigns/" + campaign_id + entity # here we add variable to specific sections? can add campaign id to the end of url to specify among every campaign stored on kanka

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + user_name
    }

    response = requests.request("GET", url, headers=headers)
    response = response.json()

    return response 

client.run(os.getenv('TOKEN'))
