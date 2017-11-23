import discord
import asyncio
import opuslib
import opuslib.api
import opuslib.api.encoder
import opuslib.api.decoder
import urllib.request
import urllib.parse
import psycopg2
import sys
import re
import urllib
import json
import random
from pprint import pprint
from random import randint
from collections import deque
from discord import opus
import AniListAPI
import youtube_dl
import setting

##TODO : separer en plusieurs fichiers pour plus de lisibilités

client = discord.Client()
transfert = dict()
voice_state = {}
helpdict = {
'' : 'List of all commands :\n!help : display help, you retard\n!fu : fuuuu\n!love\n!reddit\n!ora\n!m media\n!anime\n!manga\n!ln (marche pas trop)\n!pl ou !playlist',
'help' : 'fu',
'fu' : 'fu you',
'admin' : 'grant, degrant, delete',
'm' : 'media control\n!m play [url] : play the media from the url (also works with !m [url])\n!m current : display info on current song\n!m skip : skip a song (need a vote)\n!m stop : completely stop the bot (need a vote)\n!m volume : change the volume (from 0 to 1.9)',
'anime' : 'affiche des infos sur un anime',
'manga' : 'affiche des infos sur un manga',
'ln' : 'ça sert à rien de regarder la doc si la commande marche pas',
'love' : '*l* *o* *v* *e*',
'ora' : 'ORA ORA ORA ORA ORA',
'pl' : "playlist control\n!pl li : liste toutes les playlists\n!pl ls [playlist] : listes toutes les musiques de la playlsit\n!pl create [playlist] [genre] : créés une nouvelle playliste\n!pl remove [playlist] : retire une playlist\n!pl add [playlist] [url] : ajoute une URL à une playlist\n!pl start [playlist] : lance une playlist",
'playlist' : "playlist control\n!playlist li : liste toutes les playlists\n!playlist ls [playlist] : listes toutes les musiques de la playlsit\n!playlist create [playlist] [genre] : créés une nouvelle playliste\n!playlist remove [playlist] : retire une playlist\n!playlist add [playlist] [url] : ajoute une URL à une playlist\n!playlist start [playlist] : lance une playlist"
}
songs = {}
players = dict()
volumes = dict()

@client.event
async def on_ready():
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('------')

@client.event
async def on_message(message):
	permissions = message.author.permissions_in(message.channel)
	verified = any(role.name == "botControl" for role in message.author.roles) or permissions.manage_server

	if message.channel.is_private:
		await client.send_message(message.channel, "Don't chat with me like that, you know it won't work out :'(")

	if not await redirection(message, verified):
		if verified: #do verified stuff
			await admin_function(message)

		if message.content.startswith('!sleep'):
			await asyncio.sleep(5)
			await client.send_message(message.channel, 'Done sleeping')
		elif message.content.startswith('!help'):
			await get_help(message)
		elif message.content.startswith('!anime'):
			await get_anime(message)
		elif message.content.startswith('!manga'):
			await get_manga(message)
		elif message.content.startswith('!ln'):
			await get_ln(message)
		elif message.content.startswith('!fu'):
			listUsers = message.mentions
			msg = 'fu no one, it\'s important to realise that everyone deserve to be happy'
			await client.send_message(message.channel, msg)
			if len(listUsers) > 0:
				msg = 'but fu '
				msg += ' and '.join([str(x.mention) for x in listUsers])
				msg += ', though.'
				await asyncio.sleep(2)
				await client.send_message(message.channel, msg)
		elif message.content.startswith('!m'):
			voice = None
			for voiceclient in client.voice_clients:
				if voiceclient.server == message.channel.server:
					voice = voiceclient
			await music_control(message, voice)
		elif message.content.startswith("!playlist") or message.content.startswith("!pl"):
			voice = None
			for voiceclient in client.voice_clients:
				if voiceclient.server == message.channel.server:
					voice = voiceclient
			await playlist_control(message, voice, verified)
		elif message.content.startswith('!love'):
			await love_function(message)
		elif message.content.startswith('!reddit'):
			try:
			    subject = message.content.split()[1]
			except IndexError:
			    subject = 'all'
			await get_random_reddit(message, subject, verified)
		elif message.content.startswith('!ohayo'):
			await get_ohayo(message)
		elif message.content.startswith('!nier'):
			with open('content/FaKfwBQ.png', 'rb') as f:
				await client.send_file(message.channel, f)
		elif message.content.startswith('!chart'):
			await get_anime_chart(message)
		if message.content.lower().count('@everyone') > 0:
			with open('content/everyone_discord_meme.jpg', 'rb') as f:
				await client.send_file(message.channel, f)
		elif message.content.lower().count('ora') > 0:
			await client.send_message(message.channel, 'Muda ' * message.content.lower().count('ora'))
		elif message.content.startswith('(╯°□°）╯︵ ┻━┻'):
			await client.send_message(message.channel, '┬─┬﻿ ノ( ゜-゜ノ)')
		elif message.content.lower().startswith('awawa'):
			with open('content/awawa.jpg', 'rb') as f:
				await client.send_file(message.channel, f)
		elif message.content.lower().count('pathetic') > 0:
			with open('content/pathetic.jpg', 'rb') as f:
				await client.send_file(message.channel, f)




## ADMIN STUFF

async def admin_function(message):
	if message.content.startswith('!grant'):
		listUsers = message.mentions
		listRoles = message.role_mentions
		for user in listUsers:
			for role in listRoles:
				await client.add_roles(user, role)
			await client.send_message(message.channel, user.mention + ' has been granted the roles')
	elif message.content.startswith('!degrant'):
		listUsers = message.mentions
		listRoles = message.role_mentions
		for user in listUsers:
			for role in listRoles:
				await client.remove_roles(user, role)
			await client.send_message(message.channel, user.mention + ' has had roles removed')
	elif message.content.startswith('!delete'):
		split = message.content.split()
		try:
			subject = message.content.split()[1]
			deleted = await client.purge_from(message.channel, limit=int(subject))
			msg = await client.send_message(message.channel, 'Deleted {} messages'.format(len(deleted)))
			await asyncio.sleep(2)
			await client.delete_message(msg)
		except IndexError:
			await client.send_message(message.channel, 'Unspecified argument')


## ANIME / MANGA / LN


async def get_anime(message):
	try:
		subject = message.content[7:]
	except TypeError:
		await client.send_message(message.channel, 'Unspecified argument')
		return
	anime = AniListAPI.getAnimeDetails(subject)
	if anime is None:
		await client.send_message(message.channel, "No anime found amigo :/")
		return
	anime_embed = discord.Embed(color=0x1a7ad1)
	cleanr = re.compile('<.*?>')
	synopsis = re.sub(cleanr, '', anime["description"])
	anime_embed.description = synopsis
	anime_embed.title = anime["title_english"]
	anime_embed.add_field(name="Romaji", value=anime["title_romaji"], inline=True)
	anime_embed.add_field(name="Japanese", value=anime["title_japanese"], inline=True)
	anime_embed.add_field(name="Status", value=anime["airing_status"], inline=True)
	anime_embed.add_field(name="Type", value=anime["type"], inline=True)
	start_date = "not yet aired"
	if anime["start_date"] is not None:
		start_date = anime["start_date"][:10]
	anime_embed.add_field(name="Début de difusion", value=start_date, inline=True)
	end_date = "still airing"
	if anime["end_date"] is not None:
		end_date = anime["end_date"][:10]
	anime_embed.add_field(name="Fin de difusion", value=end_date, inline=True)
	anime_embed.add_field(name="Genre", value=', '.join([str(x) for x in anime["genres"]]), inline=True)
	anime_embed.add_field(name="Nb. Episodes", value=anime["total_episodes"], inline=True)
	anime_embed.add_field(name="Score moyen", value=anime["mean_score"], inline=True)
	if anime["image_url_lge"] is not None:
		anime_embed.set_thumbnail(url=anime["image_url_lge"])
	lien = "https://anilist.co/anime/"+str(anime["id"])
	anime_embed.set_author(name=lien, url=lien)
	if anime["image_url_banner"] is not None:
		anime_embed.set_image(url=anime["image_url_banner"])
	await client.send_message(message.channel, embed=anime_embed)

async def get_manga(message):
	try:
		subject = message.content[7:]
	except TypeError:
		await client.send_message(message.channel, 'Unspecified argument')
		return
	manga = AniListAPI.getMangaDetails(subject)
	if manga is None:
		await client.send_message(message.channel, "No manga found amigo :/")
		return
	manga_embed = discord.Embed(color=0xffff00)
	cleanr = re.compile('<.*?>')
	synopsis = re.sub(cleanr, '', manga["description"])
	manga_embed.description = synopsis
	manga_embed.title = manga["title_english"]
	manga_embed.add_field(name="Romaji", value=manga["title_romaji"], inline=True)
	manga_embed.add_field(name="Japanese", value=manga["title_japanese"], inline=True)
	manga_embed.add_field(name="Type", value=manga["type"], inline=True)
	start_date = "not yet aired"
	if manga["start_date"] is not None:
		start_date = manga["start_date"][:10]
	manga_embed.add_field(name="Début de difusion", value=start_date, inline=True)
	end_date = "still airing"
	if manga["end_date"] is not None:
		end_date = manga["end_date"][:10]
	manga_embed.add_field(name="Fin de difusion", value=end_date, inline=True)
	manga_embed.add_field(name="Genre", value=', '.join([str(x) for x in manga["genres"]]), inline=True)
	manga_embed.add_field(name="Score moyen", value=manga["mean_score"], inline=True)
	synopsis = manga["description"]
	if manga["image_url_lge"] is not None:
		manga_embed.set_thumbnail(url=manga["image_url_lge"])
	lien = "https://anilist.co/manga/"+str(manga["id"])
	manga_embed.set_author(name=lien, url=lien)
	if manga["image_url_banner"] is not None:
		manga_embed.set_image(url=manga["image_url_banner"])

	await client.send_message(message.channel, embed=manga_embed)

async def get_ln(message):
	try:
		subject = message.content[7:]
	except TypeError:
		await client.send_message(message.channel, 'Unspecified argument')
		return
	ln = AniListAPI.getLightNovelDetails(subject)
	if ln is None:
		await client.send_message(message.channel, "No ln found amigo :/")
		return
	pprint(ln)
	ln_embed = discord.Embed(color=0xffff00)
	ln_embed.description = ln["description"]
	ln_embed.title = ln["title_english"]
	ln_embed.add_field(name="Romaji", value=ln["title_romaji"], inline=True)
	ln_embed.add_field(name="Japanese", value=ln["title_japanese"], inline=True)
	ln_embed.add_field(name="Type", value=ln["type"], inline=True)
	start_date = "not yet aired"
	if ln["start_date"] is not None:
		start_date = ln["start_date"][:10]
	ln_embed.add_field(name="Début de difusion", value=start_date, inline=True)
	end_date = "still airing"
	if ln["end_date"] is not None:
		end_date = ln["end_date"][:10]
	ln_embed.add_field(name="Fin de difusion", value=end_date, inline=True)
	ln_embed.add_field(name="Genre", value=', '.join([str(x) for x in ln["genres"]]), inline=True)
	ln_embed.add_field(name="Score moyen", value=ln["mean_score"], inline=True)
	synopsis = ln["description"]
	if ln["image_url_lge"] is not None:
		ln_embed.set_thumbnail(url=ln["image_url_lge"])
	lien = "https://anilist.co/manga/"+str(ln["id"])
	ln_embed.set_author(name=lien, url=lien)
	if ln["image_url_banner"] is not None:
		ln_embed.set_image(url=ln["image_url_banner"])

	await client.send_message(message.channel, embed=ln_embed)

async def get_anime_chart(message):
	airing_list = AniListAPI.getAnimeAiring()
	pprint(airing_list)
	pprint(len(airing_list))
	count = 1
	airing_embed = discord.Embed(color=0xEEEEEE)
	for anime in airing_list:
		count += 1
		if count == 20:
			await client.send_message(message.channel, embed=airing_embed)
			airing_embed = discord.Embed(color=0x000000)
			count = 1
		airing_embed.add_field(name=anime["title_english"], value=', '.join([str(x) for x in anime["genres"]]))
	if airing_embed.fields is not discord.Embed.Empty:
		await client.send_message(message.channel, embed=airing_embed)




### RANDOM FUNCTIONS




async def get_help(message):
	try:
		subject = message.content.split()[1]
	except IndexError:
		subject = ''
	result = helpdict.get(subject, 'command not found')
	help_embed = discord.Embed(color=0xCCCCCC)
	help_embed.title = "Help " + subject
	help_embed.set_thumbnail(url="https://i.imgur.com/bb7vQzl.png")
	help_embed.description = result

	await client.send_message(message.channel, embed=help_embed)


async def get_random_reddit(message, subreddit, verified):
	url = "https://en.reddit.com/r/{}/random/.json".format(subreddit)
	hdr= { 'User-Agent' : 'super happy flair bot by /u/spladug' }
	r = urllib.request.urlopen(urllib.request.Request(url, headers=hdr))
	data_json = json.loads(r.read().decode(r.info().get_param('charset') or 'utf-8'))
	try:
		if type(data_json) is dict:
			data = data_json['data'][0]['children']['data']
		else:
			data = data_json[0]['data']['children'][0]['data']
	except:
		data = data_json['data']['children'][0]['data']
	# pprint(data)
	reddit_embed = discord.Embed(color=0x00ff00)
	reddit_embed.title = data['title']
	reddit_embed.description = data['selftext'][:600]
	reddit_embed.url = "https://en.reddit.com" + data['permalink']
	reddit_embed.add_field(name="upvotes", value=data['ups'])
	reddit_embed.add_field(name="link to image", value="[image]("+data['url']+")")
	nsfw = data['over_18']
	if nsfw:
		reddit_embed.add_field(name="over 18", value=':underage:' )
		if verified or "hot" in message.channel.name or "nsfw" in message.channel.name:
			reddit_embed.set_image(url=data['url'])
		else:
			reddit_embed.add_field(name="Ara ara !", value='You\'re too young for this !' )
	else:
		reddit_embed.set_image(url=data['url'])
	if data["media"] is not None or data['url'].endswith("gifv"):
		#embed doesn't accept video or gifv for some reasons, may be patch later
		await client.send_message(message.channel, data['title'] + " upvotes : " + str(data["ups"]) + "\n" + data['url'])
	else:
		await client.send_message(message.channel, embed=reddit_embed)


async def redirection(message, verified):
	if message.content.startswith('!!') and verified:
		if message.channel in transfert:
			transfert.pop(message.channel)
			await client.send_message(message.channel, 'Redirect off !')
		else:
			to_chan = (message.channel_mentions or [None])[0]
			if to_chan is None:
				await client.send_message(message.channel, 'You missed ! Combo Break !')
			elif(to_chan == message.channel):
				await client.send_message(message.channel, 'Stop ! Sore wa ikenai !')
			else:
				await client.send_message(message.channel, 'Redirect on !')
				transfert.update({message.channel: to_chan})
		return True #Pas la peine de traiter le message après
	else:
		if (message.channel in transfert) and not verified:
			msg = message.channel.name + ':' + message.author.mention + '>' + message.content
			await client.delete_message(message)
			await client.send_message(transfert[message.channel], msg)
			return True #Le message à été rediriger, pas besoin de le traiter
	return False


async def love_function(message):
	if len(message.content) > 6:
		subject = message.content[6:]
		ran_int = randint(0,101)

		love_embed = discord.Embed(color=0xFF69B4)
		love_embed.title = "*L* *O* *V* *E*  MAKER"
		msg_str = "{}\% connection between {} and {}\n".format(ran_int, message.author.mention, subject)
		love_embed.description = msg_str
		if ran_int > 85:
			love_embed.add_field(name="Quote", value="'{} is my wife...' - {}\n".format(subject, message.author.mention))
		await client.send_message(message.channel, embed=love_embed)
	else:
		with open('content/letslovelain.jpg', 'rb') as f:
			await client.send_file(message.channel, f, filename="letslovelaine.jpg", content='Unspecified argument *l* *o* *v* *e*\nhttps://fauux.neocities.org/Love.html')


async def get_ohayo(message):
	ran_int = randint(1,17)
	with open('ohayo/{}.png'.format(str(ran_int).zfill(4)), 'rb') as f:
		await client.send_file(message.channel, f, filename="ohayo.png", content='')

async def save_ohayo(message):
	pprint(message)
	pprint(message.embeds)
	pprint(message.attachments)










## MUSIC CONTROL


async def music_control(message, voice):
	#discord.opus.load_opus('/usr/local/lib/python3.5/dist-packages/opuslib')
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
				songs.pop(voice, None)
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
		for i in range(0,2):
			msgs.append(await client.send_message(message.channel, "{}. {}".format(i + 1, "http://www.youtube.com/watch?v=" + search_results[i])))
		msg = await client.send_message(message.channel, "Vote here :")
		msgs.append(msg)
		await client.add_reaction(msg, '1⃣')
		await client.add_reaction(msg, '2⃣')
		# await client.add_reaction(msg, '3⃣')
		# await client.add_reaction(msg, '4⃣')
		await client.add_reaction(msg, '🚫')
		song_found = -1
		while song_found == -1:
			ms = await client.wait_for_reaction(message=msg)
			if ms.user == message.author:
				if ms.reaction.emoji == '1⃣':
					song_found = 0
				if ms.reaction.emoji == '2⃣':
					song_found = 1
				# if ms.reaction.emoji == '3⃣':
				# 	song_found = 2
				# if ms.reaction.emoji == '4⃣':
				# 	song_found = 3
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




async def playlist_control(message, voice, verified):
	#discord.opus.load_opus('/usr/local/lib/python3.5/dist-packages/opuslib')
	split = message.content.split()
	conn_string = "host='localhost' dbname='Mitsuru' user='"+setting.postgresuser+"' password='"+setting.postgrespassword+"'"
	conn = psycopg2.connect(conn_string)
	cursor = conn.cursor()

	try:
		subject = split[1]
		if subject.startswith('li'):
			cursor.execute("SELECT * FROM playlist")
			records = cursor.fetchall()
			playlist_embed = discord.Embed(color=0x1a7ad1)
			playlist_embed.title = "playlists"
			for record in records:
				playlist_embed.add_field(name=record[1], value=record[2], inline=True)

			playlist_embed.set_thumbnail(url="https://cdn.discordapp.com/channel-icons/343544131928326145/f38749e25ee9abf6b0599292f5c3b908.png")
			await client.send_message(message.channel, embed=playlist_embed)
		elif subject.startswith('c'):
			p_name = split[2]
			genres = ', '.join([x for x in split[3:]])
			if genres is None or genres == '':
				genres = 'no genres'
			cursor.execute("""SELECT * FROM playlist WHERE nom = %s""", (p_name,))
			select = cursor.fetchone()
			if select is None:
				#insert
				cursor.execute("""INSERT INTO playlist(nom, genre) VALUES (%s, %s)""", (p_name, genres))
			else:
				#update
				cursor.execute("""UPDATE playlist SET genre = %s WHERE nom  = %s""", (genres, p_name))
			conn.commit()
			await client.send_message(message.channel, "Yo, you added that *like a* ***boss***")
		elif subject.startswith('a'):
			p_name = split[2]
			url = split[3]
			cursor.execute("""SELECT * FROM playlist WHERE nom = %s""", (p_name,))
			select = cursor.fetchone()
			if select is None:
				raise Exception("hey dude, playlist isn\'t here")
			else:
				#insert song
				video_title = "no name found"
				with youtube_dl.YoutubeDL({}) as ydl:
					info_dict = ydl.extract_info(url, download=False)
					video_title = info_dict.get('title', "no name found")
				cursor.execute("""INSERT INTO song(playlist, url, song_name) VALUES (%s, %s, %s)""", (select[0], url, video_title))
			conn.commit()
			await client.send_message(message.channel, "Yo, you added that *like a* ***boss***")
		elif subject.startswith('ls'):
			p_name = split[2]
			cursor.execute("""SELECT * FROM playlist WHERE nom = %s""", (p_name,))
			select = cursor.fetchone()
			if select is None:
				raise Exception("hey dude, playlist isn\'t here")
			#insert song
			cursor.execute("""SELECT * FROM song WHERE playlist = %s""", (select[0],))
			songs_db = cursor.fetchall()
			songs_str = "\n ".join([x[1] + " " + x[2] for x in songs_db])
			playlist_embed = discord.Embed(color=0x1a7ad1)
			playlist_embed.title = "songs"
			playlist_embed.description = songs_str
			await client.send_message(message.channel, embed=playlist_embed)
		elif subject.startswith('rename'):
			if verified:
				p_name = split[2]
				new_p_name = split[3]
				cursor.execute("""SELECT * FROM playlist WHERE nom = %s""", (p_name,))
				select = cursor.fetchone()
				if select is None:
					raise Exception("hey dude, playlist isn\'t here")
				else:
					cursor.execute("""UPDATE playlist SET nom = %s WHERE id  = %s""", (new_p_name, select[0]))
				conn.commit()
				await client.send_message(message.channel, "hey man, sad, but done")
		elif subject.startswith('rr'):
			if verified:
				p_name = split[2]
				cursor.execute("""SELECT * FROM playlist WHERE nom = %s""", (p_name,))
				select = cursor.fetchone()
				if select is None:
					raise Exception("hey dude, playlist isn\'t here")
				else:
					cursor.execute("""DELETE FROM song WHERE playlist = %s""", (select[0], ))
					cursor.execute("""DELETE FROM playlist WHERE id = %s""", (select[0], ))
				conn.commit()
				await client.send_message(message.channel, "hey man, sad, but done")
		elif subject.startswith("start"):
			p_name = split[2]
			cursor.execute("""SELECT * FROM playlist WHERE nom = %s""", (p_name,))
			select = cursor.fetchone()
			if select is None:
				raise Exception("hey dude, playlist isn\'t here")
			#insert song
			cursor.execute("""SELECT url FROM song WHERE playlist = %s""", (select[0],))
			songs_db = cursor.fetchall()
			random.shuffle(songs_db)
			if voice is None:
				voice = await client.join_voice_channel(message.author.voice.voice_channel)
			if voice in songs:
				song_queue = songs[voice]
			else:
				song_queue = deque()
				songs.update({voice: song_queue})
			for song in songs_db[1:]:
				song_queue.append(song[0])
			await play_song(voice, songs_db[0][0], message.channel)


	except IndexError:
		await client.send_message(message.channel, "Not enough arguments. Give me somethin', man !")
	except Exception as err:
		await client.send_message(message.channel, "Somethin' occured, man !\n`"+repr(err)+"`")
	conn.close()


client.run(setting.discord_token)
#client.run(setting.discordemail, setting.discordpassword)moi
