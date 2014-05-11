"""
Helper classes for BeautifulSoup objects.
"""


import urlparse


def collapse_tag(soup, tag, joiner=''):
    """
    Replaces all children with the concatenation, using the given joiner, of
    their strings. For example:

    <a href="..." some-attribute="hello"><s>@</s><b>username</b></a>
    would turn into:
    <a href="..." some-attribute="hello">@username</a>
    """

    string = ''.join(tag.strings)
    collapsed = soup.new_tag(tag.name)
    collapsed.attrs = tag.attrs
    collapsed.string = string
    tag.replace_with(collapsed)


def absolutize_references(base_url, soup, attributes=['href', 'img']):
    """
    Searches every element of the given soup and if a matching attribute is
    found, makes the reference absolute.
    """

    for element in soup():
        for attribute in attributes:
            if element.has_attr(attribute):
                element[attribute] = urlparse.urljoin(base_url, element[attribute])


def replace_string_with_tag(soup, tag, string, replacement):
    """
    Searches for the given string within the soup and if found replaces it with
    the tag-element.
    """
    contents = []
    for element in tag.contents:
        if isinstance(element, basestring):
            for part in element.split(string):
                contents.append(soup.new_string(part))
                contents.append(replacement)
        else:
            contents.append(element)
    tag.contents = contents


def convert_newlines(soup, tag):
    """
    Converts newline characters found in the tag's strings into <br/> tags.
    """
    br_tag = soup.new_tag('br')
    replace_string_with_tag(soup, tag, '\n', br_tag)
