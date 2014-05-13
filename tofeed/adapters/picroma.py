ROUTE = 'picroma'

import datetime
import urllib2

import bs4

import tofeed.adapters
import tofeed.formats.rss
import tofeed.utilities.spoon as spoon


class Blog(tofeed.adapters.Adapter):
    PRIMARY = True
    ROUTE = 'blog'
    URL = 'https://picroma.com/'
    DATETIME_FORMAT = '%m/%d/%Y %H:%M:%S %p'

    def __init__(self, **kwargs):
        tofeed.adapters.Adapter.__init__(self, **kwargs)

    def to_feed(self):
        response = urllib2.urlopen(self.URL)
        soup = bs4.BeautifulSoup(response)

        now = datetime.datetime.now()
        title = soup.title.string
        feed = tofeed.formats.rss.Channel(title, self.URL, title, pub_date=now, last_build_date=now)

        for post in soup('div', {'class': 'blogPost'}):
            author, pub_date = list(post.find('div', {'class': 'username'}).stripped_strings)[0].split(',')
            author = author.split('Posted by')[1].strip()
            pub_date = datetime.datetime.strptime(pub_date.strip(), self.DATETIME_FORMAT)

            element = post.find('div', {'class': 'title'}).find('a', recursive=False)
            spoon.absolutize_references(self.URL, element)
            title = element.text
            link = element['href']

            description = unicode(post.find('div', {'class': 'content'}))
            feed.add(title, link, description, author=author, guid=link, pub_date=pub_date)

        return feed.generate()
