import datetime
import urllib2

import bs4

from toFeed.formats import rss
from toFeed.adapters import Adapter
import toFeed.utils
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

            content = activity.find('div', {'class': 'shareContent'})
            title = ' '.join(content.stripped_strings)
            if len(title) > self.max_title_length:
                title = toFeed.utils.shorten_title(title, self.max_title_length)

            spoon.convert_newlines(soup, content)
            description = unicode(content)

            link = None
            spoon.absolutize_references(self.url, activity)
            if 'note' in activity['class']:
                link = activity.find('a', {'class': 'noteLink'})['href']
            elif 'photo' in activity['class']:
                content = activity.find('a', {'class': 'imagePopup'})
                link = content['href']
                description = unicode(content) + '<br/>' + description

            # This should throw an error as soon as the possible activity feed
            # content changes significantly.
            assert link

            author = list(activity.find('p', {'class': 'info'}).stripped_strings)[0]
            feed.add(title, link, description, author=author, guid=link, pub_date=pub_date)

        return feed.generate()
