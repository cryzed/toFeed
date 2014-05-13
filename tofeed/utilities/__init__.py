def shorten_to_title(string, length, separator=' ', appendix='...'):
    """
    Shortens the content to a human readable title. The function searches for
    the last occurrence of separator within the range of the content limited by
    length and appends the appendix.
    """
    return string[:length].rpartition(separator)[0] + appendix
