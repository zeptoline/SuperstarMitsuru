import discord
import asyncio
import opuslib
import opuslib.api
import opuslib.api.encoder
import opuslib.api.decoder
import urllib.request
import urllib.parse
import re
import urllib
import json
from pprint import pprint
from random import randint
from collections import deque
from discord import opus

client = None

async def music_control(message, voice, getclient):
	#discord.opus.load_opus('/usr/local/lib/python3.5/dist-packages/opuslib')
	client = getclient
	split = message.content.split()
	try:
		subject = split[1]
		if subject == 'stop':
			if voice is None:
				await client.send_message(message.channel, "It's probably already off, man")
			else:
				await client.delete_message(message)
				cc = 0
				users = []
				min_user = (len(voice.channel.voice_members)) - 1
				msg = await client.send_message(message.channel, "Add :stop_button: reaction to stop the bot ({} more needed)".format(int(min_user)))
				await client.add_reaction(msg, '◼')
				while cc <= min_user:
					ms = await client.wait_for_reaction('◼', message=msg)
					if ms.user not in users:
						cc += 1
						users.append(ms.user)
				await voice.disconnect()
		elif subject.startswith('http'):
			url = subject
			await client.delete_message(message)
			await add_song(voice, url, message)
		elif subject == 'play':
			url = split[2]
			await client.delete_message(message)
			await add_song(voice, url, message)
		elif subject == 'skip':
			await client.delete_message(message)
			cc = 0
			users = []
			min_user = (len(voice.channel.voice_members) - 1) / 2
			msg = await client.send_message(message.channel, "Add :track_next: reaction to skip song ({} more needed)".format(int(min_user)))
			await client.add_reaction(msg, '⏩')
			while cc <= min_user:
				ms = await client.wait_for_reaction('⏩', message=msg)
				if ms.user not in users:
					cc += 1
					users.append(ms.user)
			await skip_song(voice, message.channel)
		elif subject == 'current':
			await current_info(voice, message.channel)
		elif subject == 'volume':
			await set_volume(voice, split[2])
		elif subject == 'search':
			await search_youtube(message, voice, message.content[10:])

	except IndexError:
		await client.send_message(message.channel, "Not enough arguments. Give me somethin', man !")

async def add_song(voice, url, message):
	if voice is None:
		voice = await client.join_voice_channel(message.author.voice.voice_channel)
		await play_song(voice, url, message.channel)
	else:
		if voice in songs:
			song_queue = songs[voice]
			song_queue.append(url)
		else:
			song_queue = deque()
			song_queue.append(url)
			songs.update({voice: song_queue})
		await client.send_message(message.channel, "URL {} has been added.".format(url))

async def current_info(voice, chan):
	if voice in players:
		player = players[voice]
		if player is not None:
			minutes = int(player.duration / 60)
			secondes = player.duration % 60
			await client.send_message(chan, "Currently playing :\n {} [{}:{}]:\n{}".format(player.title, minutes, secondes, player.url))


async def skip_song(voice, chan):
	if voice in players:
		player = players[voice]
		if player is not None:
			if player.is_playing():
				player.stop()

async def set_volume(voice, new_vol):
	if voice in players:
		player = players[voice]
		if player is not None:
			if player.is_playing():
				volume = float(new_vol)
				if volume >= 0 and volume < 2.0:
					player.volume = volume
					volumes.update({voice: volume})

async def search_youtube(message, voice, query):
	query_string = urllib.parse.urlencode({"search_query" : query})
	html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
	search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
	search_results = search_results[::2]
	try:
		msgs = [message]
		msgs.append(await client.send_message(message.channel, "Select between theses :\n"))
		for i in range(0,4):
			msgs.append(await client.send_message(message.channel, "{}. {}".format(i + 1, "http://www.youtube.com/watch?v=" + search_results[i])))
		msg = await client.send_message(message.channel, "Vote here :")
		msgs.append(msg)
		await client.add_reaction(msg, '1⃣')
		await client.add_reaction(msg, '2⃣')
		await client.add_reaction(msg, '3⃣')
		await client.add_reaction(msg, '4⃣')
		await client.add_reaction(msg, '🚫')
		song_found = -1
		while song_found == -1:
			ms = await client.wait_for_reaction(message=msg)
			if ms.user == message.author:
				if ms.reaction.emoji == '1⃣':
					song_found = 0
				if ms.reaction.emoji == '2⃣':
					song_found = 1
				if ms.reaction.emoji == '3⃣':
					song_found = 2
				if ms.reaction.emoji == '4⃣':
					song_found = 3
				if ms.reaction.emoji == '🚫':
					song_found = 10
		await client.delete_messages(msgs)
		if song_found == 10:
			return None
		await add_song(voice, search_results[song_found], message)
	except IndexError:
		await client.send_message(message.channel, "Missin' somethin', man ?")

async def next_song(voice, chan):
	if voice in songs:
		song_queue = songs[voice]
		if song_queue:
			nextsong = song_queue.popleft()
			await play_song(voice, nextsong, chan)
		else:
			songs.pop(voice, None)
			await voice.disconnect()
			return None
	else:
		await voice.disconnect()


async def play_song(voice, url, chan):
	try:
		player = await voice.create_ytdl_player(url)
	except Exception as e:
		fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
		await client.send_message(chan, fmt.format(type(e).__name__, e))
		#while no queuing, disconnect
		await voice.disconnect()
		return None
	players.update({voice: player})
	player.start()
	if voice in volumes:
		volume = volumes[voice]
	else:
		volume = 0.5
	player.volume = volume
	await client.send_message(chan, "Playing {}".format(player.title))
	while not player.is_done():
		await asyncio.sleep(3)

	await next_song(voice, chan)
