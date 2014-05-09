import datetime
import urlparse
import urllib2

import bs4

from toFeed.formats import rss


class ActivityFeed(object):
    URL_TEMPLATE = 'http://www.patreon.com/user?u=%s&ty=a'
    DATETIME_FORMAT = '%B %d, %Y %H:%M:%S'

    def __init__(self, user_id, max_title_length=100):
        self.url = ActivityFeed.URL_TEMPLATE % user_id
        self.max_title_length = max_title_length

    def to_feed(self):
        response = urllib2.urlopen(self.url)
        soup = bs4.BeautifulSoup(response)

        title = soup.title.string
        now = datetime.datetime.now()
        feed = rss.Channel(title, self.url, title, pub_date=now, last_build_date=now)

        for activity in soup('div', {'class': 'box'})[1:]:
            if activity['prv'] in ['1', '100']:
                continue

            pub_date = datetime.datetime.strptime(
                list(activity.find('p', {'class': 'dateBox'}).stripped_strings)[0],
                ActivityFeed.DATETIME_FORMAT)

            element = activity.find('div', {'class': 'shareContent'})
            title = ' '.join(list(element.stripped_strings))
            if len(title) > self.max_title_length:
                title = title[:self.max_title_length] + ' ...'

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
            description = str(element)

            link = None
            if 'note' in activity['class']:
                link = urlparse.urljoin(self.url, activity.find('a', {'class': 'noteLink'})['href'])

            elif 'photo' in activity['class']:
                element = activity.find('a', {'class': 'imagePopup'})
                link = urlparse.urljoin(self.url, element['href'])
                element['href'] = link

                image = element.find('img')
                image['src'] = 'http:' + image['src']

                description = str(element) + '<br/>' + description

            author = list(activity.find('p', {'class': 'info'}).stripped_strings)[0]
            feed.add(title, link, description, author=author, guid=link, pub_date=pub_date)

        return feed.generate()
