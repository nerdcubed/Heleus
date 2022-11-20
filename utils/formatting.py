import unicodedata


def strip_zerowidth(text: str) -> str:
    """Strips known zero-width characters from text.
    Parameters
    ----------
    text : str
        The text to be stripped.
    Returns
    -------
    str
        The stripped text.
    """
    for c in [u'\ufeff', u'\u200d', u'\u200c', u'\u200b']:
        text = text.replace(c, '')
    return text


def strip_zalgo(text: str) -> str:
    """Strips zalgo from text strings.
    Parameters
    ----------
    text : str
        The text to be stripped.
    Returns
    -------
    str
        The stripped text.
    """
    return ''.join(
        [
            c
            for c in unicodedata.normalize('NFD', text)
            if unicodedata.category(c) not in ['Mn', 'Me']
        ]
    )
