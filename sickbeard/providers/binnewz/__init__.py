# -*- coding: latin-1 -*-
# Author: Guillaume Serre <guillaume.serre@gmail.com>
# URL: http://code.google.com/p/sickbeard/
#
# This file is part of Sick Beard.
#
# Sick Beard is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sick Beard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sick Beard.  If not, see <http://www.gnu.org/licenses/>.

import os
import re
import urllib
import urllib2

from StringIO import StringIO
import gzip
import cookielib
import time

from binsearch import BinSearch
from nzbclub import NZBClub
from nzbindex import NZBIndex
from bs4 import BeautifulSoup
from sickbeard import logger, classes, show_name_helpers, db, helpers
from sickrage.providers.nzb.NZBProvider import NZBProvider
from sickbeard.common import Quality
from nzbdownloader import NZBDownloader
from nzbdownloader import NZBPostURLSearchResult
from sickrage.helper.encoding import ek
from sickrage.helper.exceptions import ex
import sickbeard


class BinNewzProvider(NZBProvider):
    allowedGroups = {
        'abmulti': 'alt.binaries.multimedia',
        'ab.moovee': 'alt.binaries.moovee',
        'abtvseries': 'alt.binaries.tvseries',
        'abtv': 'alt.binaries.tv',
        'a.b.teevee': 'alt.binaries.teevee',
        'abstvdivxf': 'alt.binaries.series.tv.divx.french',
        'abhdtvx264fr': 'alt.binaries.hdtv.x264.french',
        'abmom': 'alt.binaries.mom',
        'abhdtv': 'alt.binaries.hdtv',
        'abboneless': 'alt.binaries.boneless',
        'abhdtvf': 'alt.binaries.hdtv.french',
        'abhdtvx264': 'alt.binaries.hdtv.x264',
        'absuperman': 'alt.binaries.superman',
        'abechangeweb': 'alt.binaries.echange-web',
        'abmdfvost': 'alt.binaries.movies.divx.french.vost',
        'abdvdr': 'alt.binaries.dvdr',
        'abmzeromov': 'alt.binaries.movies.zeromovies',
        'abcfaf': 'alt.binaries.cartoons.french.animes-fansub',
        'abcfrench': 'alt.binaries.cartoons.french',
        'abgougouland': 'alt.binaries.gougouland',
        'abroger': 'alt.binaries.roger',
        'abtatu': 'alt.binaries.tatu',
        'abstvf': 'alt.binaries.series.tv.french',
        'abmdfreposts': 'alt.binaries.movies.divx.french.reposts',
        'abmdf': 'alt.binaries.movies.french',
        'abhdtvfrepost': 'alt.binaries.hdtv.french.repost',
        'abmmkv': 'alt.binaries.movies.mkv',
        'abf-tv': 'alt.binaries.french-tv',
        'abmdfo': 'alt.binaries.movies.divx.french.old',
        'abmf': 'alt.binaries.movies.french',
        'ab.movies': 'alt.binaries.movies',
        'a.b.french': 'alt.binaries.french',
        'a.b.3d': 'alt.binaries.3d',
        'ab.dvdrip': 'alt.binaries.dvdrip',
        'ab.welovelori': 'alt.binaries.welovelori',
        'abblu-ray': 'alt.binaries.blu-ray',
        'ab.bloaf': 'alt.binaries.bloaf',
        'ab.hdtv.german': 'alt.binaries.hdtv.german',
        'abmd': 'alt.binaries.movies.divx',
        'ab.ath': 'alt.binaries.ath',
        'a.b.town': 'alt.binaries.town',
        'a.b.u-4all': 'alt.binaries.u-4all',
        'ab.amazing': 'alt.binaries.amazing',
        'ab.astronomy': 'alt.binaries.astronomy',
        'ab.nospam.cheer': 'alt.binaries.nospam.cheerleaders',
        'ab.worms': 'alt.binaries.worms',
        'abcores': 'alt.binaries.cores',
        'abdvdclassics': 'alt.binaries.dvd.classics',
        'abdvdf': 'alt.binaries.dvd.french',
        'abdvds': 'alt.binaries.dvds',
        'abmdfrance': 'alt.binaries.movies.divx.france',
        'abmisc': 'alt.binaries.misc',
        'abnl': 'alt.binaries.nl',
        'abx': 'alt.binaries.x',
        'abdivxf': 'alt.binaries.divx.french'
    }

    qualityCategories = {
        3: ['24', '7', '56'],
        500: ['44', '53', '59']
    }

    qualityMinSize = {
        (Quality.SDTV, Quality.SDDVD): 130,
        Quality.HDTV: 500,
        (Quality.HDWEBDL, Quality.HDBLURAY, Quality.FULLHDBLURAY, Quality.FULLHDTV, Quality.FULLHDWEBDL): 600
    }

    url = "http://www.binnews.in/"
    supportsBacklog = True
    nzbDownloaders = [BinSearch(), NZBIndex(), NZBClub()] #[BinSearch(), NZBIndex(), NZBClub()]

    def __init__(self):
        NZBProvider.__init__(self, "BinnewZ")

    #def is_enabled(self):
    #    return sickbeard.BINNEWZ

    def _get_season_search_strings(self, episode):
        showNam = show_name_helpers.allPossibleShowNames(episode.show)
        showNames = list(set(showNam))
        result = []
        global searchstringlist
        searchstringlist=[]
        for showName in showNames:
            result.append(showName + ".saison %2d" % episode.season)
        return result

    def _get_episode_search_strings(self, episode, add_string=''):
        strings = []
        showNam = show_name_helpers.allPossibleShowNames(episode.show)
        showNames = list(set(showNam))
        global searchstringlist
        searchstringlist=[]
        for showName in showNames:
            strings.append("%s S%02dE%02d" % (showName, episode.scene_season, episode.scene_episode))
            strings.append("%s S%02dE%d" % (showName, episode.scene_season, episode.scene_episode))
            strings.append("%s S%dE%02d" % (showName, episode.scene_season, episode.scene_episode))
            strings.append("%s %dx%d" % (showName, episode.scene_season, episode.scene_episode))
            strings.append("%s S%02d E%02d" % (showName, episode.scene_season, episode.scene_episode))
            strings.append("%s S%02d E%d" % (showName, episode.scene_season, episode.scene_episode))
            strings.append("%s S%d E%02d" % (showName, episode.scene_season, episode.scene_episode))
            strings.append("%s S%02dEp%02d" % (showName, episode.scene_season, episode.scene_episode))
            strings.append("%s S%02dEp%d" % (showName, episode.scene_season, episode.scene_episode))
            strings.append("%s S%dEp%02d" % (showName, episode.scene_season, episode.scene_episode))
            strings.append("%s S%02d Ep%02d" % (showName, episode.scene_season, episode.scene_episode))
            strings.append("%s S%02d Ep%d" % (showName, episode.scene_season, episode.scene_episode))
            strings.append("%s S%d Ep%02d" % (showName, episode.scene_season, episode.scene_episode))
            strings.append("%s S%02d Ep %02d" % (showName, episode.scene_season, episode.scene_episode))
            strings.append("%s S%02d Ep %d" % (showName, episode.scene_season, episode.scene_episode))
            strings.append("%s S%d Ep %02d" % (showName, episode.scene_season, episode.scene_episode))
        return strings

    def _get_title_and_url(self, item):
        cleanTitle = re.sub(r'(\s*\[[\w\s]+\-\w+\])', "", item.title)
        return cleanTitle, item.refererURL

    def get_quality(self, item, anime=False):
        return item.quality

    def buildUrl(self, searchString, quality):
        if quality in self.qualityCategories:
            data = {'chkInit': '1', 'edTitre': searchString, 'chkTitre': 'on', 'chkFichier': 'on', 'chkCat': 'on',
                    'cats[]': self.qualityCategories[quality], 'edAge': '', 'edYear': ''}
        else:
            data = {'b_submit': 'BinnewZ', 'cats[]': 'all', 'edSearchAll': searchString, 'sections[]': 'all'}
        return data

    def search(self, search_params, age=0, ep_obj=None):
        if search_params is None:
            return []
        logger.log("BinNewz : Searching for " + search_params, logger.DEBUG)
        data = self.buildUrl(search_params.replace('!',''), ep_obj.show.quality)
        try:
            soup = BeautifulSoup(urllib2.urlopen("http://www.binnews.in/_bin/search2.php",
                                                 urllib.urlencode(data, True)), "html5lib")
        except Exception, e:
            logger.log(u"Error trying to load BinNewz response: " + e, logger.ERROR)
            return []

        results = []
        tables = soup.findAll("table", id="tabliste")
        for table in tables:
            if len(results)>5:
                break
            rows = table.findAll("tr")
            for row in rows:

                cells = row.select("> td")
                if len(cells) < 11:
                    continue

                name = cells[2].text.strip()
                language = cells[3].find("img").get("src")

                if not "_fr" in language and not "_frq" in language:
                    continue

                detectedlang=''

                if "_fr" in language:
                    detectedlang=' truefrench '
                else:
                    detectedlang=' french '

                # blacklist_groups = [ "alt.binaries.multimedia" ]
                blacklist_groups = []

                newgroupLink = cells[4].find("a")
                newsgroup = None
                if newgroupLink.contents:
                    newsgroup = newgroupLink.contents[0]
                    if newsgroup in self.allowedGroups:
                        newsgroup = self.allowedGroups[newsgroup]
                    else:
                        logger.log(u"Unknown binnewz newsgroup: " + newsgroup, logger.ERROR)
                        continue
                    if newsgroup in blacklist_groups:
                        logger.log(u"Ignoring result, newsgroup is blacklisted: " + newsgroup, logger.WARNING)
                        continue

                filename = cells[5].contents[0]

                acceptedQualities = Quality.splitQuality(ep_obj.show.quality)[0]
                quality = Quality.nameQuality(filename)
                if quality == Quality.UNKNOWN:
                    quality = self.getReleaseQuality(name)
                if quality not in acceptedQualities:
                    continue
                if filename in searchstringlist:
                    continue

                minSize = self.qualityMinSize[quality] if quality in self.qualityMinSize else 100
                searchItems = []
                #multiEpisodes = False

                rangeMatcher = re.search("(?i).*(?<![\s\.\-_])[\s\.\-_]+s?(?:aison)?[\s\.\-_]*\d{1,2}[\s\.\-_]?(?:x|dvd|[eéEÉ](?:p|pisodes?)?)[\s\.\-_]*(\d{1,2})(?:(?:[\s\.\-_]*(?:[aàAÀ,/\-\.\s\&_]|et|and|to|x)[\s\.\-_]*(?:x|dvd|[eéEÉ](?:p|pisodes?)?)?[\s\.\-_]*([0-9]{1,2})))+.*", name)
                if rangeMatcher:
                    rangeStart = int(rangeMatcher.group(1))
                    rangeEnd = int(rangeMatcher.group(2))
                    if filename.find("*") != -1:
                        for i in range(rangeStart, rangeEnd + 1):
                            searchItem = filename.replace("**", str(i))
                            searchItem = searchItem.replace("*", str(i))
                            searchItems.append(searchItem)
                    #else:
                    #    multiEpisodes = True

                if len(searchItems) == 0:
                    searchItems.append(filename)

                for searchItem in searchItems:
                    for downloader in self.nzbDownloaders:
                        searchstringlist.append(searchItem)
                        logger.log("Searching for download : " + name + ", search string = " + searchItem + " on " +
                                   downloader.__class__.__name__)
                        try:
                            binsearch_result = downloader.search(searchItem, minSize, newsgroup)
                            if binsearch_result:
                                binsearch_result.title = search_params
                                binsearch_result.quality = quality
                                #nzbdata = binsearch_result.getNZB()
                                results.append(binsearch_result)
                                logger.log("Found : " + searchItem + " on " + downloader.__class__.__name__)
                                break
                        except Exception, e:
                            logger.log("Searching from " + downloader.__class__.__name__ + " failed : " + str(e),
                                       logger.ERROR)

        return results

    def _get_result(self, episodes):
        """
        Returns a result of the correct type for this provider
        """
        #result = classes.NZBDataSearchResult(episodes) #!
        result = classes.NZBSearchResult(episodes)
        result.provider = self

        return result

    def getReleaseQuality(self, releaseName):
        name = releaseName.lower()
        checkName = lambda elemlist, func: func([re.search(x, name, re.I) for x in elemlist])

        if checkName(["dvdrip"], all):
            return Quality.SDDVD
        elif checkName(["720p", "hdtv"], all):
            return Quality.HDTV
        elif checkName(["1080p", "hdtv"], all):
            return Quality.FULLHDTV
        elif checkName(["720p", "webrip"], all):
            return Quality.HDWEBDL
        elif checkName(["1080p", "webrip"], all):
            return Quality.FULLHDWEBDL
        elif checkName(["720p", "blu ray"], all):
            return Quality.HDBLURAY
        elif checkName(["1080p", "blu ray"], all):
            return Quality.FULLHDBLURAY
        elif checkName(["dvdrip"], all):
            return Quality.SDDVD
        elif checkName(["tvrip"], all):
            return Quality.SDTV
        else:
            return Quality.SDTV

    #def _make_url(self, result):
    #    return super._make_url(result)

    def download_result(self, result):
        nzbdata = ''
        if 'binsearch' in result.url:
            data = {
                'action': 'nzb',
                'nzb_id': 'on'
            }
        else:
            data = {
                    'url' : '/'
            }
        try:
            data_tmp = urllib.urlencode(data)
            request = urllib2.Request(result.url, data_tmp )
            request.add_header('Accept-encoding', 'gzip')
            request.add_header('Referer', result.url)
            request.add_header('Accept-Encoding', 'gzip')
            request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.57 Safari/537.17')

            response = NZBDownloader().open(request)
            if response.info().get('Content-Encoding') == 'gzip':
                buf = StringIO( response.read())
                f = gzip.GzipFile(fileobj=buf)
                nzbdata = f.read()
            else:
                nzbdata = response.read()

            #nzbdata = urllib2.urlopen(request).read()
        except Exception, e:
            logger.log('Failed downloading from %s: %s', (self.getName(),str(e)), logger.ERROR)
            return False

        # get the final file path to the nzb
        fileName = ek(os.path.join, sickbeard.NZB_DIR, result.name + ".nzb")

        logger.log(u"Saving NZB to " + fileName)

        # save the data to disk
        try:
            with ek(open, fileName, 'w') as fileOut:
                fileOut.write(nzbdata)

            helpers.chmodAsParent(fileName)

        except EnvironmentError as e:
            logger.log(u"Error trying to save NZB to black hole: " + ex(e), logger.ERROR)
            return False

        return True

provider = BinNewzProvider()
