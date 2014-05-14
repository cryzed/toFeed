ROUTE = 'patreon'

from datetime import datetime
import urllib2

import bs4

import tofeed.adapters
import tofeed.formats.rss
import tofeed.utilities
import tofeed.utilities.spoon as spoon


class ActivityFeed(tofeed.adapters.Adapter):
    ROUTE = 'activities'
    PRIMARY = True
    
    URL_TEMPLATE = 'http://www.patreon.com/%s&ty=a'
    DATE_FORMAT = '%B %d, %Y %H:%M:%S'

    def __init__(self, username, max_title_length=100, **kwargs):
        tofeed.adapters.Adapter.__init__(self, **kwargs)
        self.url = self.URL_TEMPLATE % username
        self.max_title_length = int(max_title_length)

    @staticmethod
    def _parse_content(element):
        share_content = element.find('div', {'class': 'shareContent'})
        spoon.convert_newlines(share_content)
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

    def _parse_note(self, note_soup):
        author = self._parse_author(note_soup)
        content = self._parse_content(note_soup)
        date = self._parse_date(note_soup)
        link = self._parse_link(note_soup)
        return None, link, (content,), author, date

    def _parse_photo(self, photo_soup):
        author = self._parse_author(photo_soup)
        content = self._parse_content(photo_soup)
        image = self._parse_image(photo_soup)
        date = self._parse_date(photo_soup)
        link = self._parse_link(photo_soup)
        return None, link, (image, content), author, date

    def _parse_mylink(self, mylink_soup):
        author = self._parse_author(mylink_soup)

        title_anchor = mylink_soup.find('p', {'class': 'title'}).a
        title = title_anchor.string.strip()

        spoon.absolutize_references(self.url, title_anchor, recursive=False)
        link = title_anchor['href']

        image = self._parse_image(mylink_soup)

        # Apparently newlines in this section are not even included, so there's
        # no need to convert newlines
        link_description = mylink_soup.find('p', {'class': 'linkDesc'})
        content = self._parse_content(mylink_soup)
        date = self._parse_date(mylink_soup)
        return title, link, (image, link_description, content), author, date

    def _parse_activity(self, activity_soup):
        if 'note' in activity_soup['class']:
            return self._parse_note(activity_soup)

        if 'photo' in activity_soup['class']:
            return self._parse_photo(activity_soup)

        if 'mylink' in activity_soup['class']:
            return self._parse_mylink(activity_soup)

    def to_feed(self):
        response = urllib2.urlopen(self.url)
        soup = bs4.BeautifulSoup(response, 'html.parser')

        title = soup.title.string
        now = datetime.now()
        feed = tofeed.formats.rss.Channel(title, self.url, title, pub_date=now, last_build_date=now)

        # Don't recursively search for all divs, we only want the ones one level
        # lower.
        for activity in soup.find('div', id='boxGrid')('div', recursive=False):
            # Ignore for patreon members only activities
            prv = activity.get('prv')
            if prv is None or prv in ['1', '100']:
                continue

            title, link, contents, author, date = self._parse_activity(activity)
            main_element = contents[-1]
            if 'note' in activity['class'] or 'photo' in activity['class']:
                content_string = ' '.join(main_element.stripped_strings)
                if self.max_title_length >= len(content_string):
                    title = content_string
                else:
                    title = tofeed.utilities.shorten_to_title(content_string, self.max_title_length)

            for index, content in enumerate(contents):
                # When the root element is encountered stop.
                if index == len(contents) - 1:
                    break
                main_element.insert(index, content)

            feed.add(title, link, unicode(content), author=author, pub_date=date)
        return feed.generate()
