"""
Helper classes for BeautifulSoup objects.
"""

import bs4
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


def absolutize_references(base_url, soup, attributes=['href', 'img'], recursive=True):
    """
    Searches every element of the given soup and if a matching attribute is
    found, makes the reference absolute.
    """
    for element in [soup] + soup(recursive=recursive):
        for attribute in attributes:
            if element.has_attr(attribute):
                element[attribute] = urlparse.urljoin(base_url, element[attribute])


def _copy_tag(soup, tag):
    """
    Creates a copy of the given tag. This is needed to avoid confusing the
    BeautifulSoup structure and running into strange errors.
    """
    copy = soup.new_tag(tag.name, **tag.attrs)
    for content in tag.contents:
        copy.append(content)
    return copy


def replace_string_with_tag(soup, tag, string, replacement):
    """
    Replaces all occurrences of the string in the given tag's strings with the
    replacement.
    """
    not_processed = [tag]
    while not_processed:
        tag = not_processed.pop()
        contents = []

        for content in tag.contents:
            if isinstance(content, bs4.NavigableString):
                parts = content.split(string)
                length = len(parts)
                for index, part in enumerate(parts):
                    contents.append(soup.new_string(part))

                    # Don't append the replacement after the last part
                    if index == length - 1:
                        break
                    contents.append(_copy_tag(soup, replacement))
            else:
                contents.append(content)
                not_processed.append(content)

        tag.clear()
        for content in contents:
            tag.append(content)


def convert_newlines(soup, tag):
    """
    Converts newline characters found in the tag's strings into <br/> tags.
    """
    br_tag = soup.new_tag('br')
    replace_string_with_tag(soup, tag, '\n', br_tag)
