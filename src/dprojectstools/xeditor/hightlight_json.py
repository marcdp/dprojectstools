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
    comment_started = False
    inside_string = False
    next_is_escaped = False
    dots_comman_detected = False

    
    default_fg_color = Sequences.FG_WHITE
    string_fg_color = default_fg_color
    i = 0
    while i < len(line):
        c = line[i]
        # pre process
        braced_encrypted = line.startswith("${enc:", i)
        plain_encrypted = line.startswith("enc:", i)
        if braced_encrypted or plain_encrypted:
            marker = "${enc:" if braced_encrypted else "enc:"
            result.append(marker)
            i += len(marker)
            result.append(Sequences.FG_BRIGHT_RED)
            while i < len(line):
                if braced_encrypted and line[i] == "}":
                    break
                if inside_string and line[i] == "\"" and not next_is_escaped:
                    break
                if not inside_string and (line[i].isspace() or line[i] in ",]}"):
                    break
                result.append(line[i])
                if line[i] == "\\" and not next_is_escaped:
                    next_is_escaped = True
                else:
                    next_is_escaped = False
                i += 1
            result.append(string_fg_color if inside_string else default_fg_color)
            if braced_encrypted and i < len(line) and line[i] == "}":
                result.append("}")
                i += 1
            continue
        elif c == "\\":
            next_is_escaped = True
        elif c == "\"":
            if dots_comman_detected:
                result.append(Sequences.FG_BRIGHT_YELLOW)
                string_fg_color = Sequences.FG_BRIGHT_YELLOW
            else:
                if not inside_string:                
                    result.append(Sequences.FG_CYAN)
                    string_fg_color = Sequences.FG_CYAN
        elif c in "{}[]" and not inside_string:
            result.append(Sequences.FG_BRIGHT_YELLOW)
        elif (c == "/") and not inside_string:
            result.append(Sequences.FG_GREEN)
        elif (c == "\n") and not inside_string:
            result.append(default_fg_color)
        elif (c == ":" or c == ",") and not inside_string:
            dots_comman_detected = True
        # process
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
        elif c in "{}[]" and not inside_string:
            result.append(default_fg_color)
        i += 1
        
    # return
    line_result = "".join(result)
    cache[line] = line_result
    return line_result
