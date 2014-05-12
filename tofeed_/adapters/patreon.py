ROUTE = 'patreon'

from datetime import datetime
import urllib2

import bs4

import tofeed_.adapters
import tofeed_.utils.spoon as spoon
import tofeed_.formats.rss
import tofeed_.utils


class ActivityFeed(tofeed_.adapters.Adapter):
    ROUTE = 'activities'
    PRIMARY = True
    URL_TEMPLATE = 'http://www.patreon.com/%s&ty=a'
    DATE_FORMAT = '%B %d, %Y %H:%M:%S'

    def __init__(self, username, max_title_length=100, **kwargs):
        tofeed_.adapters.Adapter.__init__(self, **kwargs)
        self.url = self.URL_TEMPLATE % username
        self.max_title_length = int(max_title_length)

    @staticmethod
    def _parse_content(soup, element):
        share_content = element.find('div', {'class': 'shareContent'})
        spoon.convert_newlines(soup, share_content)
        return share_content

    @staticmethod
    def _parse_author(element):
        author = ''.join(element.find('p', {'class': 'info'}).stripped_strings)
        return author

    def _parse_date(self, element):
        date_string = element.find('div', {'class': 'dateBox'}).string.strip()
        date = datetime.strptime(date_string, self.DATE_FORMAT)
        return date

    def _parse_image(self, element):
        image_popup = element.find('a', {'class': 'imagePopup'})
        spoon.absolutize_references(self.url, image_popup, recursive=False)
        return image_popup

    def _parse_link(self, element):
        anchor = element.find('a', rel='shares')
        spoon.absolutize_references(self.url, anchor, recursive=False)
        return anchor['href']

    def _parse_note(self, soup, note_soup):
        author = self._parse_author(note_soup)
        content = self._parse_content(soup, note_soup)
        date = self._parse_date(note_soup)
        link = self._parse_link(note_soup)
        return link, content, author, date

    def _parse_photo(self, soup, photo_soup):
        author = self._parse_author(photo_soup)
        content = self._parse_content(soup, photo_soup)
        image = self._parse_image(photo_soup)
        date = self._parse_date(photo_soup)
        link = self._parse_link(photo_soup)
        return link, content, image, author, date

    def _parse_mylink(self, soup, mylink_soup):
        author = self._parse_author(mylink_soup)

        title_anchor = mylink_soup.find('p', {'class': 'title'}).a
        title = title_anchor.string.strip()

        spoon.absolutize_references(self.url, title_anchor, recursive=False)
        link = title_anchor['href']

        image = self._parse_image(mylink_soup)

        # Apparently newlines in this section are not even included, so there's
        # no need to convert newlines
        link_description = mylink_soup.find('p', {'class': 'linkDesc'})
        content = self._parse_content(soup, mylink_soup)
        date = self._parse_date(mylink_soup)
        return title, link, image, link_description, content, author, date

    def to_feed(self):
        response = urllib2.urlopen(self.url)
        soup = bs4.BeautifulSoup(response)

        title = soup.title.string
        now = datetime.now()
        feed = tofeed_.formats.rss.Channel(title, self.url, title, pub_date=now, last_build_date=now)

        for activity in soup.find('div', id='boxGrid')('div', recursive=False):
            prv = activity.get('prv')
            if prv is None or prv in ['1', '100']:
                continue

            if 'note' in activity['class']:
                link, content, author, date = self._parse_note(soup, activity)

                # TODO: Possibly stop modifying the soup in the parsing methods
                # and do it here, this way I wouldn't need to grab the content
                # string this way again.
                content_string = ' '.join(content.stripped_strings)

                if self.max_title_length >= len(content_string):
                    title = content_string
                else:
                    title = tofeed_.utils.shorten_to_title(content_string, self.max_title_length)

                feed.add(title, link, unicode(content), author=author, pub_date=date)

            elif 'photo' in activity['class']:
                link, content, image, author, date = self._parse_photo(soup, activity)

                # TODO: Possibly stop modifying the soup in the parsing methods
                # and do it here, this way I wouldn't need to grab the content
                # string this way again.
                content_string = ' '.join(content.stripped_strings)

                if self.max_title_length >= len(content_string):
                    title = content_string
                else:
                    title = tofeed_.utils.shorten_to_title(content_string, self.max_title_length)

                content.insert(0, image)
                feed.add(title, link, unicode(content), author=author, pub_date=date)

            elif 'mylink' in activity['class']:
                title, link, image, link_description, content, author, date = self._parse_mylink(soup, activity)
                content.insert(0, link_description)
                content.insert(0, image)
                feed.add(title, link, unicode(content), author=author, pub_date=date)

        return feed.generate()
