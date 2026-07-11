from dprojectstools.console import Sequences

# cache
cache = dict()

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
    default_fg_color = Sequences.FG_WHITE
    i = 0
    while i < len(line):
        c = line[i]
        # pre process
        braced_encrypted = line.startswith("${enc:", i)
        plain_encrypted = line.startswith("enc:", i)
        if not comment_started and (braced_encrypted or plain_encrypted):
            marker = "${enc:" if braced_encrypted else "enc:"
            result.append(marker)
            i += len(marker)
            result.append(Sequences.FG_BRIGHT_RED)
            while i < len(line):
                if braced_encrypted and line[i] == "}":
                    break
                if line[i].isspace() or line[i] == "#":
                    break
                result.append(line[i])
                i += 1
            result.append(default_fg_color)
            if braced_encrypted and i < len(line) and line[i] == "}":
                result.append("}")
                i += 1
            continue
        elif c == "#":
            if not comment_started:
                comment_started = True
                result.append(Sequences.FG_GREEN)
        elif c == "\n":
            comment_started = False
            varvalue_started = False
            result.append(default_fg_color)
        elif c.isalnum():
            if comment_started:
                pass
            elif varvalue_started:
                pass
            elif not varname_started:
                varname_started = True
                result.append(Sequences.FG_CYAN)
        elif c == "=":
            result.append(default_fg_color)
        # process
        result.append(c)
        # post process
        if c == "=":
            if not varvalue_started:
                varvalue_started = True
                result.append(Sequences.FG_WHITE)
        i += 1
    # return
    line_result = "".join(result)
    cache[line] = line_result
    return line_result
