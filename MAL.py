import html
from datetime import datetime
from typing import List, Tuple

from pprint import pprint
import aiohttp
from lxml import etree



async def search_all_anime(search_query):
    """
    A function to get data for all search results from a query
    :param str search_query: is what'll be queried for the search results
    :return: List of anime objects
    :rtype: List
    """
    #
    with aiohttp.ClientSession(auth=aiohttp.BasicAuth(login='SuperstarMitsuru', password='SuperStarMitsur'), headers={"User-Agent": "SuperstarMitsuru"}) as session:
        async with session.get("https://myanimelist.net/api/anime/search.xml", params={"q": search_query}) as response:
            # Raise an error if we get the wrong response code
            if response.status != 200:
                pprint(session)
                pprint(response)
                return

            response_data = await response.read()
            pprint(response_data)
            entries = etree.fromstring(response_data)
            animes = []
            for entry in entries:
                try:
                    animes.append(
                        {
                            "id" : entry.find("id").text,
                            "titles" :  {
                                "jp" : entry.find("title").text,
                                "english" : entry.find("english").text,
                                "synonyms" : entry.find("synonyms").text.split(";")
                            },
                            "episode_count" : entry.find("episodes").text,
                            "dates" : {
                                "start" : entry.find("start_date").text,
                                "end" : entry.find("end_date").text
                            },
                            "type" : entry.find("type").text,
                            "status" : entry.find("status").text,
                            "synopsis" : html.unescape(entry.find("synopsis").text.replace("<br />", "").replace("[i]", "").replace("[/i]", "")),
                            "cover" : entry.find("image").text
                        }
                    )
                except AttributeError:
                    continue
            return animes
