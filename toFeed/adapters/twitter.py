import datetime
import json
import urllib2

import bs4

from toFeed.formats import rss
from toFeed.adapters import Adapter

ROUTE = 'twitter'


class TimelineWidget(Adapter):
    ROUTE = 'timelineWidget'
    PRIMARY = True
    URL_TEMPLATE = 'http://cdn.syndication.twimg.com/widgets/timelines/%s'
    DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S+0000'

    def __init__(self, data_widget_id, **kwargs):
        Adapter.__init__(self, **kwargs)
        self.url = self.URL_TEMPLATE % data_widget_id

    def to_feed(self):
        response = urllib2.urlopen(self.url)
        data = json.load(response)
        soup = bs4.BeautifulSoup(data['body'])

        element = soup.find('a', {'class': 'customisable-highlight'})
        title = element['title']
        link = element['href']

        now = datetime.datetime.now()
        feed = rss.Channel(title, link, title, pub_date=now, last_build_date=now)

        for tweet in soup('li', {'class': 'tweet'}):
            permalink = tweet.find('a', {'class': 'permalink'})['href']
            pub_date = datetime.datetime.strptime(tweet.find('time')['datetime'], self.DATETIME_FORMAT)
            name, _, nickname = list(tweet.find('div', {'class': 'p-author'}).stripped_strings)

            element = tweet.find('div', {'class': 'e-entry-content'})
            title = ' '.join(element.p.stripped_strings)
            description = unicode(element)

            feed.add(title, permalink, description, author='%s @%s' % (name, nickname), guid=permalink, pub_date=pub_date)

        return feed.generate()
