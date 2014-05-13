"""
Helper classes for BeautifulSoup objects.
"""

import bs4
import urlparse

import tofeed.utilities


def collapse_tag(tag, joiner=''):
    """
    Replaces the tag's children with their strings, concatenated with the
    joiner.
    """
    string = ''.join(tag.strings)
    collapsed = tofeed.utilities.new_tag(tag.name)
    collapsed.attrs = tag.attrs
    collapsed.string = string
    tag.replace_with(collapsed)


def absolutize_references(base_url, soup, attributes=['href', 'src'], recursive=True):
    """
    Turns links found within the attributes absolute by using the base_url.
    """

    # Include the root element of the soup itself
    for element in [soup] + soup(recursive=recursive):
        for attribute in attributes:
            if element.has_attr(attribute):
                element[attribute] = urlparse.urljoin(base_url, element[attribute])


def _copy_tag(tag):
    """
    Creates a copy of the tag. Needed when trying to insert the same tag
    multiple times in different locations.
    """
    copy = tofeed.utilities.new_tag(tag.name, **tag.attrs)
    map(copy.append, tag.contents)
    return copy


def replace_string_with_tag(tag, string, replacement, recursive=True):
    """
    Replaces all occurrences of string within the tag's strings with the
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
                    contents.append(tofeed.utilities.new_string(part))

                    # Don't append the replacement after the last part
                    if index == length - 1:
                        break
                    contents.append(_copy_tag(replacement))
            else:
                contents.append(content)

                # If recursive, process discovered tags
                if recursive:
                    not_processed.append(content)

        tag.clear()
        map(tag.append, contents)


def convert_newlines(tag, recursive=True):
    """
    Replaces newline characters found in the tag's strings break line tags.
    """
    br_tag = tofeed.utilities.new_tag('br')
    replace_string_with_tag(tag, '\n', br_tag, recursive)