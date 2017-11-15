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
import AniListAPI


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
