def shorten_title(title, length, seperator=' ', appendix='...'):
    """
    Tries to split the given title in a human readable way. It searches for the
    last occurence of a space within the title limited by the given length and
    splits it there.
    """
    return title[:length].rpartition(seperator)[0] + appendix
