from logging import info
import discord
import os
import requests
import json

# TO DO
# Message for generating tokens 
# Ping Kanka
# Get server specific info by name
# Get kanka campaign by name not id (Needs to be a special funciton)

DEFAULT_SETTINGS = {"token": None, "language": "en", "hide_private": True}
REQUEST_PATH = "https://kanka.io/api/1.0/"
MSG_ENTITY_NOT_FOUND = "Entity not found."
MSG_REQUIRE_TOEKN = "Please provide token"

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
    
    # Finds user's campaign by server name
    kanka_info = api_call(os.getenv(message.author.name + '_TOKEN'))
    # print(kanka_info ["data"]["name"])


    # ./campaigns endpoint dict syntax "kanka_info[data][campaign number][information]"
    # ./campaigns/{id} dict syntax "kanka_info[data][name]"
    # Can use this to verify which campaign player is in by server
    # TODO Will not use this form of calling to send campign info need to rewrite to skip campaign number
    await message.channel.send(kanka_info ["data"][0]["name"])

# TODO
# Get Kanka server by name 
# Need to call player campaign list from api, then parse json find the server name/ID for the campaign, then match server name to campaign name 
def get_server_by_name(server_name):
    return


# May need to make a seperate api call for entities and characters
# ^  Don't forget that all endpoints documented here need to be prefixed with "1.0/campaigns/{campaign.id}/."
def api_call (user_name):
    url = "https://api.kanka.io/1.0/campaigns/" # here we add variable to specific sections? can add campaign id to the end of url to specify among every campaign stored on kanka

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + user_name
    }

    response = requests.request("GET", url, headers=headers)
    response = response.json()

    return response 

client.run(os.getenv('TOKEN'))
