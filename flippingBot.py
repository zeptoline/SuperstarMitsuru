import discord
import asyncio

client = discord.Client()
@client.event
async def on_ready():
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('------')

@client.event
async def on_message(message):
    if message.content.startswith("(╯°□°）╯"):
        await client.send_message(message.channel, "┬─┬﻿ ノ( ゜-゜ノ)")

#client.run('MzIxMDM5MjA0ODExMjc2Mjk5.DB3FCw.9hptGTZi4U-MNvb-XsTELCMzpJ4')
client.run('microline@hotmail.fr', 'motdepasseSuperMitsuru')
