from dprojectstools.console import Sequences

# cache
cache = dict()

# hightlight (simple and fast scanning)
def hightlight_json(line: str) -> str:
    # cache
    if line in cache:
        return cache[line]
    # process
    result = []
    c_ant = " "
    comment_started = False
    inside_string = False
    next_is_escaped = False
    dots_comman_detected = False

    
    default_fg_color = Sequences.FG_WHITE
    for c in line:
        # pre process
        if c == "\\":
            next_is_escaped = True
        elif c == "\"":
            if dots_comman_detected:
                result.append(Sequences.FG_BRIGHT_YELLOW)
            else:
                if not inside_string:                
                    result.append(Sequences.FG_CYAN)
        elif (c == "{" or c == "}") and not inside_string:
            result.append(Sequences.FG_BRIGHT_YELLOW)
        elif (c == "/") and not inside_string:
            result.append(Sequences.FG_GREEN)
        elif (c == "\n") and not inside_string:
            result.append(default_fg_color)
        elif (c == ":" or c == ",") and not inside_string:
            dots_comman_detected = True
        # process
        c_ant = c
        result.append(c)
        # post process
        if next_is_escaped:
            next_is_escaped = False
        elif c == "\"":
            if not inside_string:
                inside_string = True
            else:
                result.append(default_fg_color)
                inside_string = False
        elif (c == "{" or c == "}") and not inside_string:
            result.append(default_fg_color)
        
    # return
    line_result = "".join(result)
    cache[line] = line_result
    return line_result
