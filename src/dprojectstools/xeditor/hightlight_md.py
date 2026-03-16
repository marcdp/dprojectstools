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
    c_ant = " "
    title_started = False
    list_item_started = False
    anchor_started = False
    asterisc_count = 0
    bold_started = False
    italic_started = False
    single_quote_count = 0
    single_quote_started = False

    
    default_fg_color = Sequences.FG_WHITE
    for c in line:
        # pre process
        if c == "#":
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
        c_ant = c
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

        
    # return
    line_result = "".join(result)
    cache[line] = line_result
    return line_result
