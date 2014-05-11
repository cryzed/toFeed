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
    for element in [soup] + soup():
        for attribute in attributes:
            if element.has_attr(attribute):
                element[attribute] = urlparse.urljoin(base_url, element[attribute])


def _copy_tag(soup, tag):
    """
    Creates a "copy" of the given tag. If one tries to insert the same tag
    reference all over the soup horrible things happen.
    """
    new_tag = soup.new_tag(tag.name, **tag.attrs)
    new_tag.contents = tag.contents
    return new_tag


# I'm aware there are many methods to do this, but I'm not sure if they are any
# faster.
def replace_string_with_tag(soup, tag, string, replacement):
    """
    Searches for the given string within the soup and if found replaces it with
    the tag-element.
    """

    offset = 0
    for index, content in enumerate(tag.contents[:]):
        if isinstance(content, basestring):
            for part in content.split(string):
                tag.insert(index + offset, _copy_tag(soup, replacement))
                tag.insert(index + offset, soup.new_string(part))
                tag.extract()
                offset += 2

    # Extract original contents
    for content in tag.contents[index + offset:]:
        content.extract()


def convert_newlines(soup, tag):
    """
    Converts newline characters found in the tag's strings into <br/> tags.
    """
    br_tag = soup.new_tag('br')
    replace_string_with_tag(soup, tag, '\n', br_tag)
