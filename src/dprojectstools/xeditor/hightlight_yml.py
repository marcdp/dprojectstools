
import re

from dprojectstools.console import Sequences


# Highlighting is performed for every redraw, so keep the result for repeated lines.
cache = dict()

_NUMBER_RE = re.compile(
    r"[+-]?(?:"
    r"0[xX][0-9a-fA-F_]+|0[oO][0-7_]+|0[bB][01_]+|"
    r"(?:[0-9][0-9_]*\.[0-9_]*|\.[0-9][0-9_]*)"
    r"(?:[eE][+-]?[0-9][0-9_]*)?|"
    r"[0-9][0-9_]*(?:[eE][+-]?[0-9][0-9_]*)?"
    r")"
)


def _key_colon(line: str) -> int:
    """Return the mapping colon, ignoring quoted text and comments."""
    quote = None
    escaped = False
    skip_quote_at = -1

    for i, char in enumerate(line):
        if quote == '"':
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quote = None
            continue

        if quote == "'":
            if i == skip_quote_at:
                continue
            # A single quote is escaped in YAML by doubling it.
            if char == "'":
                if i + 1 < len(line) and line[i + 1] == "'":
                    skip_quote_at = i + 1
                    continue
                quote = None
            continue

        if char in "'\"":
            quote = char
        elif char == "#" and (i == 0 or line[i - 1].isspace()):
            break
        elif char == ":" and (
            i + 1 == len(line) or line[i + 1].isspace() or line[i + 1] in "[]{},"
        ):
            return i

    return -1


# Highlight YAML with a small, fast line scanner, like the other editor highlighters.
def hightlight_yml(line: str) -> str:
    if line in cache:
        return cache[line]

    default_color = Sequences.fg_color_fromrgb("#A5D6FF")
    key_color = Sequences.fg_color_fromrgb("#7EE787")
    string_color = Sequences.fg_color_fromrgb("#A5D6FF")
    string_backslash_color = Sequences.fg_color_fromrgb("#CABA7D")
    boolean_color = Sequences.fg_color_fromrgb("#569CD6")
    numeric_color = Sequences.fg_color_fromrgb("#B5CEA8")
    comments_color = Sequences.fg_color_fromrgb("#8B949E")
    encrypted_color = Sequences.fg_color_fromrgb("#FF6B6B")
    list_item_color =   Sequences.fg_color_fromrgb("#BBBEBF")
    bracket_color = Sequences.fg_color_fromrgb("#FFD703")
    separator_color = Sequences.fg_color_fromrgb("#D4D4D4")
    null_color = Sequences.fg_color_fromrgb("#569CD6")
    if line.startswith("---"):
        line_result = separator_color + line + default_color
        cache[line] = line_result
        return line_result

    key_colon = _key_colon(line)
    key_start = 0
    while key_start < len(line) and line[key_start].isspace():
        key_start += 1
    list_item_index = -1
    if (
        line[key_start:key_start + 1] == "-"
        and (key_start + 1 == len(line) or line[key_start + 1].isspace())
    ):
        list_item_index = key_start
        key_start += 1
        while key_start < len(line) and line[key_start].isspace():
            key_start += 1

    result = []
    quote = None
    escaped = False
    i = 0
    while i < len(line):
        char = line[i]
        opened_quote = False

        if quote is None and char == "#" and (i == 0 or line[i - 1].isspace()):
            result.extend((comments_color, line[i:]))
            break

        if quote is None and (key_colon == -1 or i > key_colon) and line.startswith("null", i):
            end = i + len("null")
            starts_scalar = i == 0 or line[i - 1].isspace() or line[i - 1] in "[,{"
            ends_scalar = (
                end == len(line)
                or line[end].isspace()
                or line[end] in ",]}"
            )
            if starts_scalar and ends_scalar:
                result.extend((null_color, "null", default_color))
                i = end
                continue

        boolean = None
        if quote is None and (key_colon == -1 or i > key_colon):
            for candidate in ("false", "true"):
                if not line.startswith(candidate, i):
                    continue
                end = i + len(candidate)
                starts_scalar = i == 0 or line[i - 1].isspace() or line[i - 1] in "[,{"
                ends_scalar = (
                    end == len(line)
                    or line[end].isspace()
                    or line[end] in ",]}"
                )
                if starts_scalar and ends_scalar:
                    boolean = candidate
                    break
        if boolean is not None:
            result.extend((boolean_color, boolean, default_color))
            i += len(boolean)
            continue

        if quote is None and (key_colon == -1 or i > key_colon):
            number_match = _NUMBER_RE.match(line, i)
            if number_match is not None:
                end = number_match.end()
                starts_scalar = i == 0 or line[i - 1].isspace() or line[i - 1] in "[,{"
                ends_scalar = (
                    end == len(line)
                    or line[end].isspace()
                    or line[end] in ",]}"
                )
                if starts_scalar and ends_scalar:
                    result.extend(
                        (numeric_color, number_match.group(), default_color)
                    )
                    i = end
                    continue

        braced_encrypted = line.startswith("${enc:", i)
        plain_encrypted = line.startswith("enc:", i)
        if braced_encrypted or plain_encrypted:
            token_in_key = key_start <= i < key_colon
            marker = "${enc:" if braced_encrypted else "enc:"
            result.extend((marker, encrypted_color))
            i += len(marker)
            while i < len(line):
                if braced_encrypted and line[i] == "}":
                    break
                if quote is not None and line[i] == quote:
                    break
                if quote is None and (
                    line[i].isspace() or line[i] == "#" or line[i] in ",]}"
                ):
                    break
                result.append(line[i])
                i += 1
            if quote is not None:
                result.append(string_color)
            else:
                result.append(key_color if token_in_key else default_color)
            if braced_encrypted and i < len(line) and line[i] == "}":
                result.append("}")
                i += 1
            continue

        if quote is None and i == key_start and key_start < key_colon:
            result.append(key_color)

        if quote is None and i == list_item_index:
            result.append(list_item_color)

        if quote is None and char in "[]":
            result.append(bracket_color)

        if quote == '"' and char == "\\":
            result.extend((string_backslash_color, char))
            if i + 1 < len(line):
                result.append(line[i + 1])
                i += 1
            result.append(string_color)
            i += 1
            continue

        if quote is None and char in "'\"":
            quote = char
            opened_quote = True
            result.append(string_color)

        result.append(char)

        if quote == '"' and not opened_quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quote = None
                result.append(key_color if i < key_colon else default_color)
        elif quote == "'" and char == "'" and not opened_quote:
            if i + 1 < len(line) and line[i + 1] == "'":
                result.append(line[i + 1])
                i += 1
            else:
                quote = None
                result.append(key_color if i < key_colon else default_color)
        elif quote is None and i == key_colon:
            result.append(default_color)
        elif quote is None and i == list_item_index:
            result.append(default_color)
        elif quote is None and char in "[]":
            result.append(default_color)

        i += 1

    line_result = "".join(result)
    cache[line] = line_result
    return line_result
