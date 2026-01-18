import unicodedata

from disnake import ApplicationCommandType
from disnake.ext import commands
from disnake.utils import format_dt


def strip_zerowidth(text: str) -> str:
    """Strips known zero-width characters from text.
    Parameters
    ----------
    text : str
        The text to be stripped.
    Returns
    -------
    str
        The stripped text."""
    for c in ["\ufeff", "\u200d", "\u200c", "\u200b"]:
        text = text.replace(c, "")
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
    return "".join(
        [
            c
            for c in unicodedata.normalize("NFD", text)
            if unicodedata.category(c) not in ["Mn", "Me"]
        ]
    )


def format_time(time):
    return f"{format_dt(time)}\n({format_dt(time, 'R')})"


def block_quote(string: str):
    return "> " + string.replace("\n", "\n> ")


def strfdelta(delta):
    s = []
    if delta.days:
        ds = "%i day" % delta.days
        if delta.days > 1:
            ds += "s"
        s.append(ds)
    hrs, rem = divmod(delta.seconds, 60 * 60)
    if hrs:
        hs = "%i hr" % hrs
        if hrs > 1:
            hs += "s"
        s.append(hs)
    mins, secs = divmod(rem, 60)
    if mins:
        s.append("%i min" % mins)
    if secs:
        s.append("%i sec" % secs)
    return " ".join(s)


class CommandFormatter:
    def __init__(self, heleus: commands.Bot):
        self.heleus = heleus

    def format(self, name: str):
        parent = name.split(" ")[0]
        command = self.heleus.get_global_command_named(
            parent, ApplicationCommandType.chat_input
        )
        if not command:
            return f"`/{name}`"
        if command.application_id != self.heleus.application_id:
            return f"`/{name}`"
        if command:
            return f"</{name}:{command.id}>"
