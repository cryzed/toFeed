def shorten_to_title(title, length, separator=' ', appendix='...'):
    """
    Tries to split the given title in a human readable way. It searches for the
    last occurrence of a space within the title limited by the given length and
    splits it there.
    """
    return title[:length].rpartition(separator)[0] + appendix
