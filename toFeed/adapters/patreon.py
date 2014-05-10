import datetime
import urllib2
import urlparse

import bs4

from toFeed.formats import rss
from toFeed.adapters import Adapter

ROUTE = 'patreon'


class ActivityFeed(Adapter):
    ROUTE = 'activities'
    PRIMARY = True
    URL_TEMPLATE = 'http://www.patreon.com/%s&ty=a'
    DATETIME_FORMAT = '%B %d, %Y %H:%M:%S'

    def __init__(self, username, max_title_length=100, **kwargs):
        Adapter.__init__(self, **kwargs)
        self.url = ActivityFeed.URL_TEMPLATE % username
        self.max_title_length = max_title_length

    def to_feed(self):
        response = urllib2.urlopen(self.url)
        soup = bs4.BeautifulSoup(response)

        title = soup.title.string
        now = datetime.datetime.now()
        feed = rss.Channel(title, self.url, title, pub_date=now, last_build_date=now)

        for activity in soup('div', {'class': 'box'})[1:]:
            # Ignore non-public member-only activity entries
            if activity['prv'] in ['1', '100']:
                continue

            pub_date = datetime.datetime.strptime(
                list(activity.find('p', {'class': 'dateBox'}).stripped_strings)[0],
                ActivityFeed.DATETIME_FORMAT)

            element = activity.find('div', {'class': 'shareContent'})
            title = ' '.join(list(element.stripped_strings))
            if len(title) > self.max_title_length:
                title = title[:self.max_title_length] + ' ...'

            # Convert newline characters found in the content to <br/> tags,
            # allowing various RSS readers to display the post correctly.
            contents = []
            br_tag = soup.new_tag('br')
            for content in element.contents:
                if isinstance(content, basestring):
                    for line in content.split('\n'):
                        contents.append(soup.new_string(line))
                        contents.append(br_tag)
                else:
                    contents.append(content)
            element.contents = contents
            description = unicode(element)

            link = None
            if 'note' in activity['class']:
                link = urlparse.urljoin(self.url, activity.find('a', {'class': 'noteLink'})['href'])

            elif 'photo' in activity['class']:
                element = activity.find('a', {'class': 'imagePopup'})

                # Make URLs absolute
                link = urlparse.urljoin(self.url, element['href'])
                element['href'] = link

                # Fix "src"-attribute of the contained img-tag
                image = element.find('img')
                image['src'] = 'http:' + image['src']

                description = unicode(element) + '<br/>' + description

            author = list(activity.find('p', {'class': 'info'}).stripped_strings)[0]
            feed.add(title, link, description, author=author, guid=link, pub_date=pub_date)

        return feed.generate()
