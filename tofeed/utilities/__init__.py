def shorten_to_title(string, length, separator=' ', appendix='...'):
    """
    Shortens the string to a human readable title. The function searches for
    the last occurrence of separator within the range of the content limited by
    length and appends the appendix.

    :param str string: The string to create the title out of
    :param int length: The approximate length of the title. The length is only
        approximate to this value, because it's possible that the next separator
        encountered may lie further ahead.
    :param str separator: The character that separates words in the text.
        Usually of course a space, this should only have to be changed in very
        rare cases.
    :param str appendix: The string to append to the end of the title.
    """
    return string[:length].rpartition(separator)[0] + appendix
