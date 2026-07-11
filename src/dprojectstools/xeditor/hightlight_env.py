import re

from dprojectstools.console import Sequences

# cache
cache = dict()

_NUMBER_RE = re.compile(
    r"[+-]?(?:"
    r"0[xX][0-9a-fA-F_]+|0[oO][0-7_]+|0[bB][01_]+|"
    r"(?:[0-9][0-9_]*\.[0-9_]*|\.[0-9][0-9_]*)"
    r"(?:[eE][+-]?[0-9][0-9_]*)?|"
    r"[0-9][0-9_]*(?:[eE][+-]?[0-9][0-9_]*)?"
    r")"
)

# hightlight (simple and fast scanning)
def hightlight_env(line: str) -> str:
    # cache
    if line in cache:
        return cache[line]
    # process
    result = []
    comment_started = False
    varname_started = False
    varvalue_started = False
    default_color = Sequences.fg_color_fromrgb("#A5D6FF")
    key_color = Sequences.fg_color_fromrgb("#7EE787")
    string_color = Sequences.fg_color_fromrgb("#A5D6FF")
    boolean_color = Sequences.fg_color_fromrgb("#569CD6")
    numeric_color = Sequences.fg_color_fromrgb("#B5CEA8")
    comments_color = Sequences.fg_color_fromrgb("#8B949E")
    encrypted_color = Sequences.fg_color_fromrgb("#FF6B6B")
    null_color = Sequences.fg_color_fromrgb("#569CD6")
    url_parts_separators_color = Sequences.fg_color_fromrgb("#569CFF")

    value_start = len(line)
    value_end = len(line)
    scalar_color = None
    equals = line.find("=")
    if equals != -1:
        value_start = equals + 1
        while value_start < len(line) and line[value_start].isspace():
            value_start += 1
        value_end = line.find("#", value_start)
        if value_end == -1:
            value_end = len(line)
        while value_end > value_start and line[value_end - 1].isspace():
            value_end -= 1
        value = line[value_start:value_end]
        if value in ("false", "true"):
            scalar_color = boolean_color
        elif value == "null":
            scalar_color = null_color
        elif _NUMBER_RE.fullmatch(value) is not None:
            scalar_color = numeric_color
        value_is_url = "://" in value or ":?" in value
    else:
        value_is_url = False

    i = 0
    while i < len(line):
        c = line[i]
        # pre process
        if scalar_color is not None and i == value_start:
            result.extend((scalar_color, line[value_start:value_end], default_color))
            i = value_end
            continue
        braced_encrypted = line.startswith("${enc:", i)
        plain_encrypted = line.startswith("enc:", i)
        if not comment_started and (braced_encrypted or plain_encrypted):
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
            result.append(default_color)
            if braced_encrypted and i < len(line) and line[i] == "}":
                result.append("}")
                i += 1
            continue
        elif c == "#":
            if not comment_started:
                comment_started = True
                result.append(comments_color)
        elif c == "\n":
            comment_started = False
            varvalue_started = False
            result.append(default_color)
        elif c.isalnum():
            if comment_started:
                pass
            elif varvalue_started:
                pass
            elif not varname_started:
                varname_started = True
                result.append(key_color)
        elif c == "=":
            result.append(default_color)
        # process
        if value_is_url and value_start <= i < value_end and c in ":/?&=":
            result.append(url_parts_separators_color)
        result.append(c)
        # post process
        if value_is_url and value_start <= i < value_end and c in ":/?&=":
            result.append(string_color)
        if c == "=":
            if not varvalue_started:
                varvalue_started = True
                result.append(string_color)
        i += 1
    # return
    line_result = "".join(result)
    cache[line] = line_result
    return line_result
