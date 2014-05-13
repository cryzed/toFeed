import bs4

_soup = bs4.BeautifulSoup()


#: Shortcut for BeautifulSoup().new_tag. This allows using the bound methods
#: of the BeautifulSoup class without having to instantiate it manually.
new_tag = _soup.new_tag

#: Shortcut for BeautifulSoup().new_string. This allows using the bound methods
#: of the BeautifulSoup class without having to instantiate it manually.
new_string = _soup.new_string


def shorten_to_title(content, length, separator=' ', appendix='...'):
    """
    Shortens the content to a human readable title. The function searches for
    the last occurrence of separator within the range of the content limited by
    length and appends the appendix.
    """
    return content[:length].rpartition(separator)[0] + appendix
