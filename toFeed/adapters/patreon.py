import datetime
import urllib2

import bs4

import toFeed.utils
from toFeed.formats import rss
from toFeed.adapters import Adapter
from toFeed.utils import spoon

ROUTE = 'patreon'


class ActivityFeed(Adapter):
    ROUTE = 'activities'
    PRIMARY = True
    URL_TEMPLATE = 'http://www.patreon.com/%s&ty=a'
    DATETIME_FORMAT = '%B %d, %Y %H:%M:%S'

    def __init__(self, username, max_title_length=100, **kwargs):
        Adapter.__init__(self, **kwargs)
        self.url = self.URL_TEMPLATE % username
        self.max_title_length = int(max_title_length)

    def to_feed(self):
        response = urllib2.urlopen(self.url)
        soup = bs4.BeautifulSoup(response)

        title = soup.title.string
        now = datetime.datetime.now()
        feed = rss.Channel(title, self.url, title, pub_date=now, last_build_date=now)

        for activity in soup('div', {'class': 'box'})[1:]:
            # Ignore non-public member-only activity entries for now
            if activity['prv'] in ['1', '100']:
                continue

            pub_date = datetime.datetime.strptime(
                list(activity.find('p', {'class': 'dateBox'}).stripped_strings)[0],
                self.DATETIME_FORMAT)

            link = None
            content = None
            description = None
            if 'note' in activity['class']:
                element = activity.find('a', {'class': 'noteLink'})
                spoon.absolutize_references(self.url, element)
                link = element['href']
                content = activity.find('div', {'class': 'shareContent'})
                spoon.absolutize_references(self.url, content)
                spoon.convert_newlines(soup, content)
                description = unicode(content)

            elif 'photo' in activity['class']:
                content = activity.find('div', {'class': 'shareContent'})
                photo = activity.find('a', {'class': 'imagePopup'})
                spoon.absolutize_references(self.url, content)
                spoon.absolutize_references(self.url, photo)
                spoon.convert_newlines(soup, content)
                link = photo['href']
                description = unicode(photo) + '<br/>' + unicode(content)

            elif 'mylink' in activity['class']:
                link_description = activity.find('p', {'class': 'linkDesc'})
                photo = activity.find('a', {'class': 'imagePopup'})
                content = activity.find('div', {'class': 'shareContent'})
                spoon.absolutize_references(self.url, link_description)
                spoon.absolutize_references(self.url, photo)
                spoon.convert_newlines(soup, content)
                link = photo['href']
                description = unicode(photo) + '<br/>' + unicode(link_description) + '<br/>' + unicode(content)

            # This should throw an error as soon as the possible activity feed
            # content changes significantly.
            assert link and content and description

            if 'mylink' in activity['class']:
                title = ''.join(activity.find('p', {'class': 'title'}).stripped_strings)
            else:
                title = ' '.join(content.stripped_strings)

            if len(title) > self.max_title_length:
                title = toFeed.utils.shorten_title(title, self.max_title_length)

            author = list(activity.find('p', {'class': 'info'}).stripped_strings)[0]
            feed.add(title, link, description, author=author, guid=link, pub_date=pub_date)

        return feed.generate()
