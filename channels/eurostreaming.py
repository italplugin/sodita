# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# PureITA.- XBMC Plugin
# Canale  eurostreaming.club
# http://www.mimediacenter.info/foro/viewtopic.php?f=36&t=7808
# ------------------------------------------------------------
import re
import urlparse

from core import config
from core import logger
from core import scrapertools
from core import servertools
from core.item import Item
from core.tmdb import infoSod


__channel__ = "eurostreaming"
__category__ = "F,S,A"
__type__ = "generic"
__title__ = "eurostreaming"
__language__ = "IT"

DEBUG = config.get_setting("debug")

host = "https://eurostreaming.news"


def isGeneric():
    return True


def mainlist(item):
    logger.info("streamondemand.eurostreaming mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Serie TV -  [COLOR orange]Aggiornate[/COLOR]",
                     action="serietv",
                     extra='serie',
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_series_P.png"),
               Item(channel=__channel__,
                     title="[COLOR azure]Serie TV -  [COLOR orange]Archivio[/COLOR]",
                     action="serietv",
                     extra='serie',
                     url="%s/category/serie-tv-archive/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/tv_series_P.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Anime / Cartoni[/COLOR]",
                     action="serietv",
                     extra='serie',
                     url="%s/category/anime-cartoni-animati/" % host,
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/animation_P.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     action="search",
                     extra='serie',
                     thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/search_P.png")]

    return itemlist

def serietv(item):
    logger.info("streamondemand.eurostreaming peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patron = '<div class="post-thumb">\s*'
    patron += '<a href="?([^>"]+)"?.*?title="?([^>"]+)"?.*?<img.*?src="([^>"]+)'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        scrapedplot = ""
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle.replace("Streaming", ""))
        if scrapedtitle.startswith("Link to "):
            scrapedtitle = scrapedtitle[8:]
        num = scrapertools.find_single_match(scrapedurl, '(-\d+/)')
        if num:
            scrapedurl = scrapedurl.replace(num, "-episodi/")
        if (DEBUG): logger.info(
            "title=[" + scrapedtitle + "], url=[" + scrapedurl + "], thumbnail=[" + scrapedthumbnail + "]")
        itemlist.append(infoSod(
            Item(channel=__channel__,
                 action="episodios",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title=scrapedtitle,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 extra=item.extra,
                 folder=True), tipo='tv'))

    # Extrae el paginador
    patronvideos = '<a class="next page-numbers" href="([^"]+)">Avanti &raquo;</a>'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="HomePage",
                 title="[COLOR yellow]Torna Home[/COLOR]",
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/return_home_P.png",
                 folder=True)),
        itemlist.append(
            Item(channel=__channel__,
                 action="serietv",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/orione7/Pelis_images/master/channels_icon_pureita/successivo_P.png",
                 extra=item.extra,
                 folder=True))

    return itemlist


def HomePage(item):
    import xbmc
    xbmc.executebuiltin("ReplaceWindow(10024,plugin://plugin.video.streamondemand-pureita-master)")


def search(item, texto):
    logger.info("[eurostreaming.py] " + item.url + " search " + texto)
    item.url = "%s/?s=%s" % (host, texto)
    try:
        return serietv(item)
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def episodios(item):
    def load_episodios():
        for data in match.split('<br/>'):
            ## Extrae las entradas
            end = data.find('<a ')
            if end > 0:
                scrapedtitle = scrapertools.find_single_match(data[:end], '\d+[^\d]+\d+')
                scrapedtitle = scrapedtitle.replace('×', 'x')
                itemlist.append(
                    Item(channel=__channel__,
                         action="findvideos",
                         title=scrapedtitle + " (" + lang_title + ")",
                         url=data,
                         thumbnail=item.thumbnail,
                         extra=item.extra,
                         fulltitle=scrapedtitle + " (" + lang_title + ")" + ' - ' + item.show,
                         show=item.show))

    logger.info("[eurostreaming.py] episodios")

    itemlist = []

    ## Descarga la página
    data = scrapertools.cache_page(item.url)

    patron = r"onclick=\"top.location=atob\('([^']+)'\)\""
    b64_link = scrapertools.find_single_match(data, patron)
    if b64_link != '':
        import base64
        data = scrapertools.cache_page(base64.b64decode(b64_link))

    patron = r'<a href="(%s/\?p=\d+)">' % host
    link = scrapertools.find_single_match(data, patron)
    if link != '':
        data = scrapertools.cache_page(link)

    data = scrapertools.decodeHtmlentities(data)

    patron = '</span>([^<]+)</div><div class="su-spoiler-content su-clearfix" style="display:none">(.+?)</div></div>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for lang_title, match in matches:
        lang_title = 'SUB ITA' if 'SUB' in lang_title.upper() else 'ITA'
        load_episodios()

    patron = '<li><span style="[^"]+"><a onclick="[^"]+" href="[^"]+">([^<]+)</a>(?:</span>\s*<span style="[^"]+"><strong>([^<]+)</strong>)?</span>(.*?)</div>\s*</li>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for lang_title1, lang_title2, match in matches:
        lang_title = 'SUB ITA' if 'SUB' in (lang_title1 + lang_title2).upper() else 'ITA'
        load_episodios()

    if config.get_library_support() and len(itemlist) != 0:
        itemlist.append(
            Item(channel=__channel__,
                 title=item.title,
                 url=item.url,
                 action="add_serie_to_library",
                 extra="episodios" + "###" + item.extra,
                 show=item.show))
        itemlist.append(
            Item(channel=item.channel,
                 title="Scarica tutti gli episodi della serie",
                 url=item.url,
                 action="download_all_episodes",
                 extra="episodios" + "###" + item.extra,
                 show=item.show))

    return itemlist


def findvideos1(item):
    logger.info("[eurostreaming.py] findvideos")

    ## Descarga la página
    data = item.url if item.extra == 'serie' else scrapertools.cache_page(item.url)

    itemlist = servertools.find_video_items(data=data)
    for videoitem in itemlist:
        videoitem.title = item.title + videoitem.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist

# ==================================================================================================================================================

def findvideos88(item):
    logger.info("icarus.eurostreaming findvideos")
    itemlist = []

    # Carica la pagina 
    data = item.url

    matches = re.findall(r'<a href="([^"]+)[^>]*>[^<]+</a>', data, re.DOTALL)

    while 'linkup' in item.url:
        item.url = httptools.downloadpage(item.url, only_headers=True, follow_redirects=False).headers.get("location")
        data = item.url

    itemlist = servertools.find_video_items(data=str(data))

    for videoitem in itemlist:
        videoitem.title = item.title + videoitem.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = item.channel
        videoitem.contentType = item.contentType

    return itemlist
def findvideos(item):
    logger.info("[streamondemand-pureita altadefinizione_due ] findvideos")
    itemlist = []
    # Descarga la pagina 
    data = httptools.downloadpage(item.url, headers=headers).data
    # Estrae i contenuti 
    patron = '<a href="([^"]+)[^>]*>[^<]+</a>'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for scrapedurl in matches:
     while 'linkup' in item.url:
        item.url = httptools.downloadpage(item.url, only_headers=True, follow_redirects=False).headers.get("location")       
        data = item.url
    for videoitem in servertools.find_video_items(data=data):
        videoitem.title = "[COLOR orange]" + videoitem.title + "[/COLOR]"
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.show = item.show
        videoitem.plot = item.plot
        videoitem.channel = __channel__
        itemlist.append(videoitem)
    return itemlist
def findvideos2(item):
    logger.info("streamondemand-pureita.filmstreamingita peliculas")
    itemlist = []

    data = httptools.downloadpage(item.url, headers=headers).data 
    blocco = scrapertools.get_match(data, r'Streaming<\/strong><\/p>\s*<p>(.*?)\s*<\/br>')
    patron = r'<a href="([^"]+)" target="_blank[^>]+>([^<]+)'

    matches = re.compile(patron, re.DOTALL).findall(blocco)

    for scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapedtitle.replace("’", "'")
        scrapedthumbnail = ""
        scrapedplot = ""

        scrapedplot = ""
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 contentType="movie",
                 title="[[COLOR orange]" + scrapedtitle + "[/COLOR]] - " + item.title,
                 fulltitle=item.fulltitle,
                 url=scrapedurl,
                 extra="movie",
                 plot=item.plot,
                 show=item.show,
                 thumbnail=item.thumbnail,
                 folder=True))

    return itemlist

# ==================================================================================================================================================
	
def play(item):
    itemlist=[]

    data = item.url
    while 'vcrypt' in item.url:
        item.url = httptools.downloadpage(item.url, only_headers=True, follow_redirects=False).headers.get("location")
        data = item.url

    logger.debug(data)

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.title = item.title
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist
	
# ==============================================================================================================================================================================