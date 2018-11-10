# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# StreamOnDemand-PureITA / XBMC Plugin
# Canale filmstreaming01
# http://www.mimediacenter.info/foro/viewtopic.php?f=36&t=7808
# ------------------------------------------------------------

import re
import urlparse

from core import httptools
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod

__channel__ = "filmstreaming01"
host = "https://filmstreaming01.com"
headers = [['Referer', host]]


def mainlist(item):
    logger.info("streamondemand-pureita [filmstreaming01 mainlist]")

    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Film[COLOR orange] - Novita'[/COLOR]",
                     action="peliculas",
                     url=host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_new.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film[COLOR orange] - Ultimi Aggiornati[/COLOR]",
                     action="peliculas_new",
                     url=host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movie_new_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film[COLOR orange] - Lista[/COLOR]",
                     action="peliculas",
                     url=host + "/lista-film/",
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/all_movies_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film[COLOR orange] - Categorie[/COLOR]",
                     action="genere",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genres_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film[COLOR orange] - Anno[/COLOR]",
                     action="genere_year",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movie_year_P.png"),
                Item(channel=__channel__,
                     title="[COLOR orange]Cerca...[/COLOR]",
                     action="search",
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png")]

    return itemlist

# ==============================================================================================================================================================================

def search(item, texto):
    logger.info("[streamondemand-pureita filmstreaming01] " + item.url + " search " + texto)

    item.url = host + "/?s=" + texto

    try:
        return peliculas(item)

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

# ==============================================================================================================================================================================		

def genere(item):
    logger.info("streamondemand-pureita [filmstreaming01 genere]")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patron = '<li class="cat-item cat-item-\d+"><a href="([^"]+)" >([^<]+)</a> <span>([^<]+)</span>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, nvideos in matches:
        nvideos=" ([COLOR yellow]" + nvideos + " Video[/COLOR])"
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]" + nvideos,
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genre_P.png",
                 folder=True))

    return itemlist

# ==============================================================================================================================================================================

def genere_year(item):
    logger.info("streamondemand-pureita [filmstreaming01 genere_year]")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patron = '<li><a href="([^"]+)">([^<]+)</a></li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:

        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/movie_year_P.png",
                 folder=True))

    return itemlist

# ==============================================================================================================================================================================

def peliculas(item):
    logger.info("streamondemand-pureita [filmstreaming01 peliculas]")
    itemlist = []

    # Descarga la pagina 
    data = scrapertools.cache_page(item.url)
	
    patron = '<a href="([^"]+)">\s*<div class="image">\s*<img src="([^"]+)" alt="([^"]+)" width[^>]+>\s*<span class="player">'
    patron += '</span>\s*<span class="imdb"><b>[^>]+></b></b>([^<]+)</span>\s*[^>]+>\s*[^>]+>\s*[^>]+>\s*'
    patron += '<a href="[^"]+">\s*[^>]+>[^<]+</span>\s*<span class="ttx">(?:[^,]+|)(?:streaming|)([^<]+)<'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle, votes, scrapedplot in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        votes=votes.replace(",", ".")
        votes=" ([COLOR yellow]" + votes.strip() + "[/COLOR])"
		
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]" + votes,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 plot="[COLOR orange]" + scrapedtitle + "[/COLOR] " + scrapedplot,
                 show=scrapedtitle))

    # Extrae el paginador
    next_page = scrapertools.find_single_match(data, '<div class="pag_b"><a href="([^"]+)" >Next</a></div>')
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=next_page,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png"))

    return itemlist

# ==============================================================================================================================================================================

def peliculas_new(item):
    logger.info("streamondemand-pureita [filmstreaming01 peliculas_new]")
    itemlist = []

    # Descarga la pagina 
    data = scrapertools.cache_page(item.url)
	
    patron = '<a href="([^"]+)"><img src="([^"]+)" alt="([^<]+)" width[^>]+></a>\s*'
    patron += '<span class="imdb"><b class="icon-star"></b>([^<]+)</span>\s*</div>\s*'
    patron += '<span class="ttps">[^<]+</span>\s*<span class="ytps">([^<]+)</span>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle, votes, year in matches:
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle).strip()
        votes=votes.replace(",", ".")
        votes=" ([COLOR yellow]" + votes.strip() + "[/COLOR])"
        year=" ([COLOR yellow]" + year + "[/COLOR])"

        scrapedplot=""
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]" + year + votes,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 plot=scrapedplot,
                 show=scrapedtitle), tipo='movie'))

    return itemlist

# ==============================================================================================================================================================================
		
def findvideos(item):
    logger.info("streamondemand-pureita [filmstreaming01  findvideos]")
    data = scrapertools.cache_page(item.url)

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        servername = re.sub(r'[-\[\]\s]+', '', videoitem.title)
        videoitem.title = "".join(['[COLOR azure][[COLOR orange]' + servername.capitalize()+ '[/COLOR]] - ' +item.title, '[/COLOR]'])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist



