# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# StreamOnDemand-PureITA / XBMC Plugin
# Canale doumentari_dsda
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

__channel__ = "documentari_dsda"
host = "https://documentari-streaming-da.com"
headers = [['Referer', host]]


def mainlist(item):
    logger.info("streamondemand-pureita [doumentari_dsda mainlist]")

    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Documentari[COLOR orange] - Novita'[/COLOR]",
                     action="peliculas_tv",
                     url="%s/?searchtype=movie&post_type=movie&sl=lasts&s=" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/popcorn_new.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Documentari[COLOR orange] - Categorie[/COLOR]",
                     action="genere",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genres_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Documentari[COLOR orange] - Le Serie[/COLOR]",
                     action="peliculas_tv",
                     url="%s/?searchtype=movie&post_type=movie&sl=lasts&cat=series&s=" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/documentari3_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Documentari[COLOR orange] - Le Raccolte[/COLOR]",
                     action="peliculas_tv",
                     url="%s/?searchtype=movie&post_type=movie&sl=lasts&cat=groups&s=" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/documentari3_P.png"),

                Item(channel=__channel__,
                     title="[COLOR orange]Cerca...[/COLOR]",
                     action="search",
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png")]

    return itemlist

# ==============================================================================================================================================================================

def search(item, texto):
    logger.info("[streamondemand-pureita doumentari_dsda] " + item.url + " search " + texto)
    item.url = host + "/?searchtype=movie&post_type=movie&s=" + texto
    try:
        return peliculas_search(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


# ==============================================================================================================================================================================

def peliculas_search(item):
    logger.info("streamondemand-pureita [doumentari_dsda peliculas_tv]")
    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data
	
    patron = '<img[^>]+src="([^"]+)" class="img[^>]+>\s*<a class[^>]+>\s*[^>]+>[^=]+>\s*[^>]+>\s*[^>]+>\s*'
    patron += '[^>]+>[^>]+>\s*<div class="movie-name">\s*<h4 class[^>]+><a href="([^"]+)">([^<]+)<\/a>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedthumbnail, scrapedurl, scrapedtitle  in matches:
        scrapedtitle = scrapedtitle.replace("Serie Documentari", "")
        scrapedtitle=scrapedtitle.replace("streaming", "").replace("streami", "")
        scrapedplot = ""
        itemlist.append(
            Item(channel=__channel__,
                 action="episodios",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 plot=scrapedplot,
                 show=scrapedtitle))

    # Extrae el paginador
    next_page = scrapertools.find_single_match(data, "<li><span aria-current='page' class='page-numbers current'>\d+</span></li>\s*<li><a class='page-numbers' href='([^']+)'>\d+</a>")
    next_page=next_page.replace("&#038;", "&")
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_tv",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=next_page,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png"))

    return itemlist		

# ==============================================================================================================================================================================		

def genere(item):
    logger.info("streamondemand-pureita [doumentari_dsda genere]")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data

    # Extrae las entradas (carpetas)
    patron = '<li class=" menu-item menu-item-type-post_type menu-item-object-page has-menu-child"><a href=".*?categoria-([^\/]+)\/">([^<]+)<\/a><\/li>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle in matches:
        url=("%s/?searchtype=movie&post_type=movie&sl=lasts&cat=%s&s=" % (host, scrapedurl))
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_tv",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=url,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/genre_P.png",
                 folder=True))

    return itemlist

# ==============================================================================================================================================================================

def peliculas_tv(item):
    logger.info("streamondemand-pureita [doumentari_dsda peliculas_tv]")
    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data
	
    patron = '<img[^>]+src="([^"]+)" class="img[^>]+>\s*<a class[^>]+>\s*'
    patron += '[^>]+>[^=]+>\s*[^>]+>[^>]+>[^>]+><a href="([^"]+)">([^<]+)<\/a>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedthumbnail, scrapedurl, scrapedtitle  in matches:
        scrapedtitle = scrapedtitle.replace("Serie Documentari", "")
        scrapedtitle=scrapedtitle.replace("streaming", "").replace("streami", "")
        scrapedplot = ""
        itemlist.append(
            Item(channel=__channel__,
                 action="episodios",
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 plot=scrapedplot,
                 show=scrapedtitle))

    # Extrae el paginador
    next_page = scrapertools.find_single_match(data, "<li><span aria-current='page' class='page-numbers current'>\d+</span></li>\s*<li><a class='page-numbers' href='([^']+)'>\d+</a>")
    next_page=next_page.replace("&#038;", "&")
    if next_page != "":
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_tv",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=next_page,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/next_1.png"))

    return itemlist

# ==============================================================================================================================================================================

def episodios(item):
    logger.info("streamondemand-pureita [doumentari_dsda episodios]")
    itemlist = []

    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data
	

    patron = 'style="color[^>]+>([^<]+)<(?:/b><br|)(?:/a>.*?</strong|)>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedtitle in matches:
        if "&#" in scrapedtitle:
           scrapetitle=scrapertools.find_single_match(data, 'style="color[^>]+>([^&]+)[^<]+</')
        if "(" in scrapedtitle:
           scrapetitle=scrapertools.find_single_match(data, 'style="color[^>]+>([^(]+)[^<]+</')
        if not "&#" in scrapedtitle and not "(" in scrapedtitle:
           scrapetitle=scrapedtitle

        scrapedtitle=scrapedtitle.replace("streaming", "").replace("streami", "").replace("_", " ")
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=item.url,
                 thumbnail=item.thumbnail,
                 fulltitle=item.fulltitle + " - " + scrapedtitle,
                 extra=scrapedtitle,
                 plot=item.plot,
                 show=item.show + " - " + scrapedtitle))
				 
    patron = '<p><em><strong>([^<]+)</strong></em></p>\s*<p><strong>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedtitle in matches:
        if "(" in scrapedtitle:
           scrapetitle=scrapertools.find_single_match(data, 'style="color[^>]+>([^(]+)[^<]+<\/b><br>')
        else:
           scrapetitle=scrapedtitle

        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="findvideos",
                 title=scrapedtitle,
                 url=item.url,
                 thumbnail=item.thumbnail,
                 fulltitle=scrapetitle,
                 plot=item.plot,
                 show=scrapedtitle), tipo='serie'))
				 

    return itemlist

# ==============================================================================================================================================================================	

def findvideos(item):
    logger.info("[streamondemand-pureita doumentari_dsda] peliculas_date")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url, headers=headers).data
    bloque = scrapertools.get_match(data, '%s(.*?)br><br>' % item.extra)
				 				 
    patron = 'href="([^"]+)" [^>]+>(?:<b>|)([^<]+)</'

    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle  in matches:
        if not "href" in bloque:
          continue
        scrapedtitle=scrapedtitle.replace("streamin.to", "Streamango")
        scrapedtitle=scrapedtitle.replace("other", "Rapidvideo")		
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 contentType="serie",
                 fulltitle=item.fulltitle,
                 show=scrapedtitle,
                 title="[[COLOR orange]" + scrapedtitle.capitalize() + "[/COLOR]] - " + item.title,
                 url=scrapedurl.strip(),
                 thumbnail=item.thumbnail,
                 plot="[COLOR orange][B]" + item.title + "[/B][/COLOR] " + item.plot,
                 folder=True))
				 

				 				 
    patron = '<p><strong><span style="[^"]+"><a style="color: #0000ff;" href="([^"]+)" target="_blank">([^<]+)</a>'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle  in matches:

        scrapedtitle=scrapedtitle.replace("streamin.to", "Streamango")
        scrapedtitle=scrapedtitle.replace("other", "Rapidvideo")		
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 contentType="serie",
                 fulltitle=item.fulltitle,
                 show=scrapedtitle,
                 title="[[COLOR orange]" + scrapedtitle.capitalize() + "[/COLOR]] - " + item.title,
                 url=scrapedurl.strip(),
                 thumbnail=item.thumbnail,
                 plot="[COLOR orange][B]" + item.title + "[/B][/COLOR] " + item.plot,
                 folder=True))

    return itemlist

# ==================================================================================================================================================
	
def play(item):
    logger.info("streamondemand-pureita doumentari_dsda]  findvideos]")
    data = item.url

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = "".join(['[COLOR orange]' + videoitem.title + '[/COLOR] ',  item.fulltitle ])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist



