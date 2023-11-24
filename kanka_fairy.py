import discord
import os

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

client.run(os.getenv('TOKEN'))
