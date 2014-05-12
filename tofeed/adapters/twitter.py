ROUTE = 'twitter'

import datetime
import json
import urllib2

import bs4

import tofeed.adapters
import tofeed.formats.rss
import tofeed.utils.spoon as spoon


class Primitive(tofeed.adapters.Adapter):
    ROUTE = 'primitive'
    URL_TEMPLATE = 'https://twitter.com/%s'
    STATUSES_URL_TEMPLATE = 'https://twitter.com/%s/statuses/%s'

    def __init__(self, username, **kwargs):
        tofeed.adapters.Adapter.__init__(self, **kwargs)
        self.url = self.URL_TEMPLATE % username

    def to_feed(self):
        response = urllib2.urlopen(self.url)
        soup = bs4.BeautifulSoup(response)

        title = soup.title.string
        link = self.url
        description = soup.find('p', {'class': 'bio'}).string

        now = datetime.datetime.now()
        feed = tofeed.formats.rss.Channel(title, link, description, pub_date=now, last_build_date=now)

        for tweet in soup('li', {'data-item-type': 'tweet'}):
            account_group = list(tweet.find('a', {'class': 'account-group'}).stripped_strings)
            author = account_group[0] + ' ' + ''.join(account_group[1:])
            username = account_group[-1]

            timestamp = int(tweet.find('span', {'class': '_timestamp'})['data-time-ms'])
            pub_date = datetime.datetime.fromtimestamp(timestamp / 1000)

            tweet_text = tweet.find('p', {'class': 'tweet-text'})
            spoon.absolutize_references(self.url, tweet_text)

            for a in tweet_text('a'):
                spoon.collapse_tag(soup, a)

            title = ' '.join(tweet_text.stripped_strings)
            description = unicode(tweet_text)

            media = tweet.find('a', {'class': 'media'})
            if media:
                thumbnail = tweet.find('div', {'class': 'js-media-img-placeholder'})['data-img-src']
                description += '<a href="%s"><img src="%s"/></a>' % (media['href'], thumbnail)
            link = self.STATUSES_URL_TEMPLATE % (username, tweet.div['data-tweet-id'])

            feed.add(title, link, description, author=author, guid=link, pub_date=pub_date)

        return feed.generate()


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
            name, _, nickname = list(tweet.find('div', {'class': 'p-author'}).stripped_strings)

            element = tweet.find('div', {'class': 'e-entry-content'})

            # Normalize links to build the title properly, but don't collapse
            # the possibly contained image.
            for a in element('a', {'class': lambda klass: klass in ['profile', 'hashtag']}):
                spoon.collapse_tag(soup, a)

            title = ' '.join(element.p.stripped_strings)
            description = unicode(element)

            feed.add(title, permalink, description, author='%s @%s' % (name, nickname), guid=permalink, pub_date=pub_date)

        return feed.generate()
