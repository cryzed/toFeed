"""
RSS
~~~
"""

import datetime
import xml.sax.saxutils

import jinja2


JINJA2_EXTENSIONS = ['tofeed.libraries.jinja2htmlcompress.HTMLCompress']
CHANNEL_TEMPLATE = '''<rss version="2.0">
    <channel>
        <title>{{ title }}</title>
        <link>{{ link }}</link>
        <description>{{ description }}</description>
        {% if language %}<language>{{ language }}</language>{% endif %}
        {% if copyright %}<copyright>{{ copyright }}</copyright>{% endif %}
        {% if managing_editor %}<managingEditor>{{ managing_editor }}</managingEditor>{% endif %}
        {% if webmaster %}<webMaster>{{ webmaster }}</webMaster>{% endif %}
        {% if pub_date %}<pubDate>{{ pub_date }}</pubDate>{% endif %}
        {% if last_build_date %}<lastBuildDate>{{ last_build_date }}</lastBuildDate>{% endif %}
        {% if categories %}
        {% for category in categories %}
        <category>{{ category }}</category>
        {% endfor %}
        {% endif %}
        {% if generator %}<generator>{{ generator }}</generator>{% endif %}
        {% if docs %}<docs>{{ docs }}</docs>{% endif %}
        {% if cloud %}<cloud>{{ cloud }}</cloud>{% endif %}
        {% if ttl %}<ttl>{{ ttl }}</ttl>{% endif %}
        {% if image %}<image>{{ image }}</image>{% endif %}
        {% if rating %}<rating>{{ rating }}</rating>{% endif %}
        {% if text_input %}<textInput>{{ text_input }}</textInput>{% endif %}
        {% if skip_hours %}<skipHours>{{ skip_hours }}</skipHours>{% endif %}
        {% if skip_days %}<skipDays>{{ skip_days }}</skipDays>{% endif %}
        {% for item in items %}
        {{ item.generate() }}
        {% endfor %}
   </channel>
</rss>'''

ITEM_TEMPLATE = '''<item>
    <title>{{ title }}</title>
    <link>{{ link }}</link>
    <description>{{ description }}</description>
    {% if author %}<author>{{ author }}</author>{% endif %}
    {% if categories %}
    {% for category in categories %}
    <category>{{ category }}</category>
    {% endfor %}
    {% endif %}
    {% if comments %}<comments>{{ comments }}</comments>{% endif %}
    {% if enclosure %}<enclosure>{{ enclosure }}</enclosure>{% endif %}
    {% if guid %}<guid>{{ guid }}</guid>{% endif %}
    {% if pub_date %}<pubDate>{{ pub_date }}</pubDate>{% endif %}
    {% if source %}<source>{{ source }}</source>{% endif %}
</item>'''


def _escape_xml(string_):
    if not string_:
        return

    return xml.sax.saxutils.escape(string_)


def _format_rfc_822(datetime_object):
    return datetime_object.strftime('%a, %d %b %Y %H:%M:%S %Z').strip()


class Channel(object):
    REQUIRED_ELEMENTS = ['title', 'link', 'description']
    OPTIONAL_ELEMENTS = [
        'language', 'copyright', 'managing_editor', 'webmaster', 'pub_date',
        'last_build_date', 'categories', 'generator', 'docs', 'cloud', 'ttl',
        'image', 'rating', 'text_input', 'skip_hours', 'skip_days']
    ELEMENTS = REQUIRED_ELEMENTS + OPTIONAL_ELEMENTS

    def __init__(self, title, link, description, items=[], **kwargs):
        self.title = title
        self.link = link
        self.description = description

        for element in 'pub_date', 'last_build_date':
            value = kwargs.get(element)
            if isinstance(value, datetime.datetime):
                kwargs[element] = _format_rfc_822(value)

        for element in self.OPTIONAL_ELEMENTS:
            setattr(self, element, kwargs.get(element))

        self.items = set(items)

    def add(self, *args, **kwargs):
        if len(args) == 1 and not kwargs and isinstance(args[0], Item):
            self.items.add(args[0])
        else:
            self.items.add(Item(*args, **kwargs))

    def generate(self):
        elements = self.ELEMENTS[:]

        data = {'items': self.items}
        if self.categories:
            elements.remove('categories')
            data['categories'] = [_escape_xml(category) for category in self.categories]

        for element in elements:
            data[element] = _escape_xml(getattr(self, element))

        return jinja2.Template(CHANNEL_TEMPLATE, extensions=JINJA2_EXTENSIONS).render(data)


class Item(object):
    REQUIRED_ELEMENTS = ['title', 'link', 'description']
    OPTIONAL_ELEMENTS = ['author', 'categories', 'comments', 'enclosure',
                         'guid', 'pub_date', 'source']
    ELEMENTS = REQUIRED_ELEMENTS + OPTIONAL_ELEMENTS

    def __init__(self, title, link, description, **kwargs):
        self.title = title
        self.link = link
        self.description = description

        pub_date = kwargs.get('pub_date')
        if pub_date:
            kwargs['pub_date'] = _format_rfc_822(pub_date)

        for element in self.OPTIONAL_ELEMENTS:
            setattr(self, element, kwargs.get(element))

    def generate(self):
        elements = self.ELEMENTS[:]

        data = {}
        if self.categories:
            elements.remove('categories')
            data['categories'] = [_escape_xml(category) for category in self.categories]

        for element in elements:
            data[element] = _escape_xml(getattr(self, element))

        return jinja2.Template(ITEM_TEMPLATE, extensions=JINJA2_EXTENSIONS).render(data)
