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
    c_ant = " "
    comment_started = False
    varname_started = False
    varvalue_started = False
    secret_started = False
    default_fg_color = Sequences.FG_WHITE
    for c in line:
        # pre process
        if c == "#":
            if not comment_started:
                comment_started = True
                result.append(Sequences.FG_GREEN)
        elif c == "\n":
            comment_started = False
            varvalue_started = False
            secret_started = False
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
        c_ant = c
        result.append(c)
        # post process
        if c == "=":
            if not varvalue_started:
                varvalue_started = True
                result.append(Sequences.FG_WHITE)
        elif c == ":":
            if not secret_started:
                secret_started = True
                result.append(Sequences.FG_BRIGHT_MAGENTA)
    # return
    line_result = "".join(result)
    cache[line] = line_result
    return line_result
