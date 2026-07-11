from dprojectstools.console import Sequences

# cache
cache = dict()

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
    asterisc_count = 0
    bold_started = False
    italic_started = False
    single_quote_count = 0
    single_quote_started = False

    
    default_fg_color = Sequences.FG_WHITE
    if line.startswith(">"):
        line_result = Sequences.FG_GREEN + line + default_fg_color
        cache[line] = line_result
        return line_result

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
                if line[i].isspace() or line[i] == "#":
                    break
                result.append(line[i])
                i += 1
            if single_quote_started:
                result.append(Sequences.FG_YELLOW)
            elif anchor_started:
                result.append(Sequences.FG_YELLOW)
            elif title_started:
                result.append(Sequences.FG_CYAN)
            elif bold_started or italic_started:
                result.append(Sequences.FG_BRIGHT_BLUE)
            else:
                result.append(default_fg_color)
            if braced_encrypted and i < len(line) and line[i] == "}":
                result.append("}")
                i += 1
            continue
        elif c == "#":
            if not title_started:
                title_started = True
                result.append(Sequences.FG_CYAN)
        elif c == "\n":
            title_started = False
            anchor_started = False
            bold_started = False
            italic_started = False
            single_quote_started = False
            result.append(default_fg_color)
        elif c == ">":
            if not title_started and not anchor_started and not bold_started and not italic_started and not single_quote_started:
                result.append(Sequences.FG_GREEN)
                list_item_started = True
        elif c == "]" and not bold_started:
            if not title_started:
                result.append(default_fg_color)
                anchor_started = False
        elif c == "*":
            if bold_started:
                asterisc_count -= 1
                if asterisc_count == 0:
                    bold_started = False
            elif italic_started:
                asterisc_count -= 1
                if asterisc_count == 0:
                    italic_started = False
            else:
                asterisc_count += 1
                if asterisc_count == 1:
                    result.append(Sequences.FG_BRIGHT_BLUE)
        elif c == "`":
            if single_quote_started:
                single_quote_count -= 1
                if single_quote_count == 0:
                    single_quote_started = False
            else:
                single_quote_count += 1
                if single_quote_count == 1:
                    single_quote_started = True
                    result.append(Sequences.FG_YELLOW)
        elif c.isalnum() and asterisc_count == 1:
            italic_started = True            
        elif c.isalnum() and asterisc_count == 2:
            bold_started = True
            italic_started = False
        else:
            pass
        # process
        result.append(c)
        # post process
        if list_item_started:
            result.append(default_fg_color)
            list_item_started = False
        elif c == "[" and not bold_started:
            if not title_started:
                result.append(Sequences.FG_YELLOW)
                anchor_started = True
        elif c == "*":
            if asterisc_count == 0:
                result.append(default_fg_color)            
        elif c == "`":
            if single_quote_count == 0:
                result.append(default_fg_color)            

        i += 1
        
    # return
    line_result = "".join(result)
    cache[line] = line_result
    return line_result
