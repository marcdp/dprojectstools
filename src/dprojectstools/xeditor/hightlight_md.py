import re

from dprojectstools.console import Sequences

# cache
cache = dict()

_URL_RE = re.compile(r"(?:https?://|www\.)[^\s<>()\[\]{}'\"`*]+")


def _colorize_url(url, url_color, separator_color, restored_style):
    result = [url_color]
    for char in url:
        if char in ":/?&=":
            result.extend((separator_color, char, url_color))
        else:
            result.append(char)
    result.append(restored_style)
    return "".join(result)

# hightlight (simple and fast scanning)
def hightlight_md(line: str) -> str:
    # cache
    if line in cache:
        return cache[line]
    # process
    result = []
    title_started = False
    list_item_started = False
    anchor_started = False
    bold_started = False
    bold_delimiter = None
    italic_started = False
    italic_delimiter = None
    single_quote_count = 0
    single_quote_started = False

    default_color = Sequences.FG_WHITE
    default_style = Sequences.RESET + default_color
    title_color = Sequences.fg_color_fromrgb("#79C0FF")
    block_color = Sequences.fg_color_fromrgb("#7BE387")
    inline_block_color = Sequences.fg_color_fromrgb("#A5D6FF")
    single_quote_color = Sequences.fg_color_fromrgb("#F2C38F")
    bold_color = Sequences.fg_color_fromrgb("#C9D1D9") + Sequences.BOLD
    italic_color = Sequences.fg_color_fromrgb("#C9D1D9") + Sequences.ITALIC
    encrypted_color = Sequences.fg_color_fromrgb("#FF6B6B")
    list_item_color =   Sequences.fg_color_fromrgb("#FFA657")
    separator_color = Sequences.fg_color_fromrgb("#79C0FF")
    url_color = Sequences.fg_color_fromrgb("#79C0FF") + Sequences.UNDERLINE
    url_parts_separators_color = Sequences.fg_color_fromrgb("#569CFF")

    if line.startswith(">"):
        line_result = []
        last = 0
        for match in _URL_RE.finditer(line):
            url_end = match.end()
            while url_end > match.start() and line[url_end - 1] in ".,;:!?":
                url_end -= 1
            if url_end == match.start():
                continue
            line_result.extend(
                (
                    line[last:match.start()],
                    _colorize_url(
                        line[match.start():url_end],
                        url_color,
                        url_parts_separators_color,
                        Sequences.RESET + block_color,
                    ),
                )
            )
            last = url_end
        line_result.extend((line[last:], default_style))
        line_result = block_color + "".join(line_result)
        cache[line] = line_result
        return line_result

    if line.strip() == "---":
        line_result = separator_color + line + default_style
        cache[line] = line_result
        return line_result

    list_marker_start = len(line) - len(line.lstrip())
    list_marker_end = list_marker_start
    if (
        line[list_marker_start:list_marker_start + 1] in ("*", "-")
        and list_marker_start + 1 < len(line)
        and line[list_marker_start + 1].isspace()
    ):
        list_marker_end = list_marker_start + 1
    else:
        while list_marker_end < len(line) and line[list_marker_end].isdigit():
            list_marker_end += 1
        if not (
            list_marker_end > list_marker_start
            and line[list_marker_end:list_marker_end + 1] == "."
            and list_marker_end + 1 < len(line)
            and line[list_marker_end + 1].isspace()
        ):
            list_marker_end = list_marker_start
        else:
            list_marker_end += 1

    i = 0
    while i < len(line):
        c = line[i]
        # pre process
        if i == list_marker_start and list_marker_end > list_marker_start:
            result.extend(
                (list_item_color, line[list_marker_start:list_marker_end], default_style)
            )
            i = list_marker_end
            continue
        url_match = None if single_quote_started else _URL_RE.match(line, i)
        if url_match is not None:
            url_end = url_match.end()
            while url_end > i and line[url_end - 1] in ".,;:!?":
                url_end -= 1
            if url_end > i:
                if title_started:
                    restored_style = Sequences.RESET + title_color
                elif anchor_started:
                    restored_style = Sequences.RESET + inline_block_color
                elif bold_started:
                    restored_style = Sequences.RESET + bold_color
                elif italic_started:
                    restored_style = Sequences.RESET + italic_color
                else:
                    restored_style = default_style
                result.append(
                    _colorize_url(
                        line[i:url_end],
                        url_color,
                        url_parts_separators_color,
                        restored_style,
                    )
                )
                i = url_end
                continue
        braced_encrypted = line.startswith("${enc:", i)
        plain_encrypted = line.startswith("enc:", i)
        if braced_encrypted or plain_encrypted:
            marker = "${enc:" if braced_encrypted else "enc:"
            result.append(marker)
            i += len(marker)
            result.append(encrypted_color)
            while i < len(line):
                if braced_encrypted and line[i] == "}":
                    break
                if line[i].isspace() or line[i] == "#":
                    break
                result.append(line[i])
                i += 1
            if single_quote_started:
                result.append(inline_block_color)
            elif anchor_started:
                result.append(inline_block_color)
            elif title_started:
                result.append(title_color)
            elif bold_started:
                result.append(bold_color)
            elif italic_started:
                result.append(italic_color)
            else:
                result.append(default_color)
            if braced_encrypted and i < len(line) and line[i] == "}":
                result.append("}")
                i += 1
            continue
        elif c == "#":
            if not title_started:
                title_started = True
                result.append(title_color)
        elif c == "\n":
            title_started = False
            anchor_started = False
            bold_started = False
            bold_delimiter = None
            italic_started = False
            italic_delimiter = None
            single_quote_started = False
            result.append(default_style)
        elif c == ">":
            if not title_started and not anchor_started and not bold_started and not italic_started and not single_quote_started:
                result.append(block_color)
                list_item_started = True
        elif c == "]" and not bold_started:
            if not title_started:
                result.append(default_color)
                anchor_started = False
        elif c in "*_" and not single_quote_started:
            delimiter = c * 2 if line.startswith(c * 2, i) else c
            if delimiter == italic_delimiter and italic_started:
                result.extend((delimiter, default_style))
                italic_started = False
                italic_delimiter = None
                i += 1
                continue
            if delimiter == bold_delimiter and bold_started:
                result.extend((delimiter, default_style))
                bold_started = False
                bold_delimiter = None
                i += len(delimiter)
                continue

            closes_at = line.find(delimiter, i + len(delimiter))
            underscore_boundary = (
                c != "_"
                or (
                    (
                        i == 0
                        or (not line[i - 1].isalnum() and line[i - 1] != "_")
                    )
                    and (
                        closes_at == -1
                        or closes_at + len(delimiter) == len(line)
                        or (
                            not line[closes_at + len(delimiter)].isalnum()
                            and line[closes_at + len(delimiter)] != "_"
                        )
                    )
                )
            )
            if (
                not bold_started
                and not italic_started
                and closes_at > i + len(delimiter)
                and underscore_boundary
            ):
                if len(delimiter) == 1:
                    italic_started = True
                    italic_delimiter = delimiter
                    result.extend((italic_color, delimiter))
                    i += 1
                else:
                    bold_started = True
                    bold_delimiter = delimiter
                    result.extend((bold_color, delimiter))
                    i += 2
                continue
        elif c == "`":
            if single_quote_started:
                single_quote_count -= 1
                if single_quote_count == 0:
                    single_quote_started = False
            else:
                single_quote_count += 1
                if single_quote_count == 1:
                    single_quote_started = True
                    result.append(single_quote_color)
        else:
            pass
        # process
        result.append(c)
        # post process
        if list_item_started:
            result.append(default_color)
            list_item_started = False
        elif c == "[" and not bold_started:
            if not title_started:
                result.append(inline_block_color)
                anchor_started = True
        elif c == "`":
            if single_quote_count == 0:
                result.append(default_color)

        i += 1
        
    # return
    line_result = "".join(result)
    cache[line] = line_result
    return line_result
