"""
Spoon
~~~~~

Helper functions for BeautifulSoup objects.
"""

import bs4
import urlparse


_soup = bs4.BeautifulSoup()

#: Shortcut for :func:`BeautifulSoup.new_tag`. This allows using the bound methods
#: of the BeautifulSoup class without having to instantiate it manually.
new_tag = _soup.new_tag

#: Shortcut for :func:`BeautifulSoup.new_string`. This allows using the bound methods
#: of the BeautifulSoup class without having to instantiate it manually.
new_string = _soup.new_string


def collapse_tag(tag):
    """
    Replaces the tag's descendents with their strings.

    :param bs4.element.Tag tag: The tag to collapse.
    """
    string = ''.join(tag.strings)
    collapsed = new_tag(tag.name)
    collapsed.attrs = tag.attrs
    collapsed.string = string
    tag.replace_with(collapsed)


def absolutize_references(base_url, tag, attributes=['href', 'src'], recursive=True):
    """
    Turns references found within the tag's attributes absolute.

    :param str base_url: The base URL used to absolutize the references
    :param bs4.element.Tag tag: The tag to absolutize references in
    :param list attributes: The attributes containing the URLs that should be
        made absolute
    :param bool recursive: If ``True`` the tag and all its sub tags will be
        searched, else only the tag and its direct descendents will be
        searched.
    """

    # Include the tag itself
    for element in [tag] + tag(recursive=recursive):
        for attribute in attributes:
            if element.has_attr(attribute):
                element[attribute] = urlparse.urljoin(base_url, element[attribute])


def _copy_tag(tag):
    """
    Creates a copy of the tag. Needed when trying to insert the same tag
    multiple times in different locations.
    """
    copy = new_tag(tag.name, **tag.attrs)
    map(copy.append, tag.contents)
    return copy


def replace_string_with_tag(tag, string, replacement, recursive=True):
    """
    Replaces all occurrences of string within the tag's strings with the
    replacement tag.

    :param bs4.element.Tag tag: The tag to replace strings in
    :param str string: The string to replace
    :param str bs4.element.Tag replacement: The tag replacing the string
    :param bool recursive:
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
                    contents.append(new_string(part))

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
    Replaces newline characters found in the tag's strings with line break tags.

    :param bs4.element.Tag tag: The tag to convert newline characters in.
    :param bool recursive: If ``True`` the tag and all its sub tags will be
        searched, else only the tag and its direct descendents will be
        searched.
    """
    br_tag = new_tag('br')
    replace_string_with_tag(tag, '\n', br_tag, recursive)
