ROUTE = 'twitter'

import datetime
import json
import urllib2

import bs4

import tofeed.adapters
import tofeed.formats.rss
import tofeed.utilities.spoon as spoon


class TimelineWidget(tofeed.adapters.Adapter):
    PRIMARY = True
    ROUTE = 'timelineWidget'
    URL_TEMPLATE = 'http://cdn.syndication.twimg.com/widgets/timelines/%s'
    DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S+0000'

    def __init__(self, data_widget_id, **kwargs):
        tofeed.adapters.Adapter.__init__(self, **kwargs)
        self.url = self.URL_TEMPLATE % data_widget_id

    def to_feed(self):
        response = urllib2.urlopen(self.url)
        data = json.load(response)
        soup = bs4.BeautifulSoup(data['body'])

        element = soup.find('a', {'class': 'customisable-highlight'})
        title = element['title']
        link = element['href']

        now = datetime.datetime.now()
        feed = tofeed.formats.rss.Channel(title, link, title, pub_date=now, last_build_date=now)

        for tweet in soup('li', {'class': 'tweet'}):
            permalink = tweet.find('a', {'class': 'permalink'})['href']
            pub_date = datetime.datetime.strptime(tweet.find('time')['datetime'], self.DATETIME_FORMAT)
            name, _, screen_name = list(tweet.find('a', {'class': 'profile'}).stripped_strings)
            content = tweet.find('div', {'class': 'e-entry-content'})

            # Strip out markup
            map(spoon.collapse_tag, content('a', {'class': lambda klass: klass in ['profile', 'hashtag', 'link']}))
            title = ' '.join(content.p.stripped_strings)
            description = unicode(content)

            feed.add(title, permalink, description, author='%s @%s' % (name, screen_name), guid=permalink, pub_date=pub_date)
        return feed.generate()
