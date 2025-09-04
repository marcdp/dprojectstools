from dataclasses import dataclass
from ..commands import command, Argument, Flag, CommandsManager
from typing import Annotated, List
from lxml import etree
import base64
import subprocess
import time
import re
import os
import glob
import sys
import tempfile

# dataclass
@dataclass
class SvgIcon:
    name: str
    src: str
    fixedcode: str = ""
    finalcode: int = 0
    color: str = ""
    unicode: int = 0
    useSourceSvg: bool= False
    transform: str = None
    description: str = None
    css: str = None

# class
class Fonticons:

    # methods
    @command()
    def generate(self, 
        # input
        path: Annotated[str,  Argument("PATH")]
    ):
        #absolutize
        if not os.path.isabs(path):
            path = os.path.join(os.getcwd(), path)
        # read file
        lines = []
        with open(path, "r", encoding="utf-8") as file:
            lines = file.readlines()
        # process
        icons = list()
        icon_names = []
        variables = dict()
        for line in lines:
            # skip comments
            if line.startswith("#"):
                continue
            # if 
            if "${" in line:
                i = line.index("${")
                j = line.index("}", i)
                if j != -1:
                    var_name = line[i+2:j]
                    var_value = variables.get(var_name)
                    line = line[:i] + var_value + line[j+1:]
            # strip
            line = re.sub(r'\t+', ' ', line).replace("\n", "")
            while "  " in line:
                line = line.replace("  ", " ")
            if line == "":
                continue
            # split
            command_parts = (line + "   ").split(" ")
            command = command_parts[0]
            arg1 = command_parts[1]
            arg2 = command_parts[2]
            # print
            if command == "":
                pass
            elif command == "set":
                if "=" in arg1:
                    var_name = arg1[:arg1.index("=")]
                    var_value = arg1[arg1.index("=")+1:]
                    if var_value.startswith("./"):
                        var_value = os.path.join(os.path.dirname(path), var_value[2:]).replace("/", os.sep)
                    variables[var_name] = var_value
            elif command == "add":
                # add
                name = arg1
                src = ""
                fixedcode = ""
                color = ""
                useSourceSvg = False
                css = ""
                unicode = 0
                transform = ""
                description = ""
                for part in arg2.split(";"):
                    if "=" in part:
                        part_name = part.split("=")[0]
                        part_value = part.split("=")[1]
                        if part_name == "src":
                            if not os.path.isabs(part_value):
                                part_value = os.path.join(os.path.dirname(path), part_value)
                            src = part_value
                        elif part_name == "fixedcode":
                            fixedcode = part_value
                        elif part_name == "color":
                            color = part_value
                        elif part_name == "useSourceSvg":
                            useSourceSvg = (part_value.lower() == "true")
                        elif part_name == "css":
                            css = part_value
                        elif part_name == "transform":
                            transform = part_value
                        elif part_name == "description":
                            description = part_value
                        elif part_name == "unicode":
                            if "&#x" in part_value:
                                unicode = int(part_value.replace("&#x", ""), 16)
                            else:
                                unicode = int(part_value)
                        else:
                            print("error: invalid argument:", part_name)
                            return -1
                if not name in icon_names:
                    icon = SvgIcon(name=name, src=src, fixedcode=fixedcode, color=color, useSourceSvg=useSourceSvg, css=css, transform=transform, unicode=unicode, description=description)
                    icons.append(icon)
                    icon_names.append(name)
            elif command == "addFolder":
                # addFolder
                src = ""
                for part in arg1.split(";"):
                    if "=" in part:
                        part_name = part.split("=")[0]
                        part_value = part.split("=")[1]
                        if part_name == "src":
                            if not os.path.isabs(part_value):
                                part_value = os.path.join(os.path.dirname(path), part_value)
                            src = part_value
                        else:
                            print("error: invalid argument:", part_name)
                            return -1
                for name in os.listdir(src):
                    if ".svg" in name:
                        icon_name = name.replace(".svg","")
                        if not icon_name in icon_names:
                            icon = SvgIcon(name = icon_name, src=os.path.join(src, name))
                            icons.append(icon)
                            icon_names.append(icon_name)
            elif command == "createFontSpriteAndCss":
                # generate 
                self.generate_fonts(variables, icons, path)
                self.generate_css(variables, icons, path)
                
            elif command == "createHtml":
                # create html
                pass

            else:
                print(f"error: invalid command '{command}'")
                return -1
            
        #print(icons)
        return 0         

    def generate_fonts(self, variables, icons, path):
        py = []
        py.append("import fontforge")
        py.append("import psMat")
        py.append("import math")
        py.append("")
        # load fonts
        fontIndex = 0
        for icon in icons:
            if icon.src.endswith(".ttf"):
                py.append(f"font{fontIndex} = fontforge.open(\"{icon.src.replace("\\","/")}\")")
        py.append("")
        # compute index
        font_index_code = int("e000", 16)
        font_used_codes = []
        for icon in icons:
            if icon.fixedcode != "":
                icon.finalcode = int(icon.fixedcode.replace("&#x", ""), 16)
                font_used_codes.append(icon.finalcode)
        for icon in icons:
            if icon.finalcode == 0:
                while font_index_code in font_used_codes:
                    font_index_code += 1
                icon.finalcode = font_index_code
                font_used_codes.append(font_index_code)            
        # icons
        py.append("newfont = fontforge.font()")
        py.append("newfont.encoding = \"Unicode\" ")
        py.append("newfont.ascent = font0.ascent")
        py.append("newfont.descent = font0.descent")
        # icons
        for icon in icons:
            if icon.useSourceSvg:
                pass
            elif icon.src.endswith(".svg"):
                py.append(f"glyphA = newfont.createMappedChar({icon.finalcode})")
                py.append(f"glyphA.importOutlines(\"{icon.src.replace("\\","/")}\")")
            elif icon.src.endswith(".ttf"):
                py.append(f"font0.selection.select({icon.unicode})")
                py.append(f"font0.copy()")
                py.append(f"newfont.selection.select({icon.finalcode})")
                py.append(f"newfont.paste()")
        py.append("")
        # generate
        py.append(f"newfont.generate(\"{path.replace("\\","/").replace(".def",".otf")}\")")
        py.append(f"newfont.generate(\"{path.replace("\\","/").replace(".def",".ttf")}\")")
        py.append(f"newfont.generate(\"{path.replace("\\","/").replace(".def",".woff")}\")")
        # save code to temp file
        code = "\n".join(py)
        temp_file_name = ""
        with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', suffix='.py') as temp_file:
            temp_file.write(code)
            temp_file_name = temp_file.name
        # execute temp file
        subprocess.run(f"fontforge.exe -script \"{temp_file_name}\"", check=True)
        # remove old files
        os.remove(temp_file.name)
    
    def generate_css(self, variables, icons, path):
        pass
        prefix = variables.get("cssPrefix")
        name = os.path.basename(path).replace(".def","")
        ticks = time.time()
        css = []
        css.append(f"@font-face {{font-family:'icons';font-display:block;src:url('./icons.woff?v={ticks}') format('woff'), url('./icons.ttf?v={ticks}') format('truetype'); font-weight:normal; font-style:normal;}}")
        css.append(f"SPAN.{prefix} {{display:inline-block; font-style:normal; font-family:icons; text-rendering:auto; -webkit-font-smoothing:antialiased; -moz-osx-font-smoothing:grayscale;}}")
        css.append(f"SPAN.{prefix}-fw {{width:1rem; height:1rem; text-align:center;}}")
        css.append(f"SPAN.{prefix}-nm {{margin-right:0em!important;}}")
        css.append(f"SPAN.{prefix}-x2 {{font-size:2em}}")
        css.append(f"SPAN.{prefix}-x3 {{font-size:3em}}")
        css.append(f"SPAN.{prefix}-x4 {{font-size:4em}}")
        css.append(f"SPAN.{prefix}-x5 {{font-size:5em}}")
        css.append(f"SPAN.{prefix}-rotate-90 {{transform:rotate(90deg); -webkit-transform:rotate(90deg); -moz-transform:rotate(90deg); -ms-transform:rotate(90deg);}}")
        css.append(f"SPAN.{prefix}-rotate-180 {{transform:rotate(180deg); -webkit-transform:rotate(180deg); -moz-transform:rotate(180deg); -ms-transform:rotate(180deg);}}")
        css.append(f"SPAN.{prefix}-rotate-270 {{transform:rotate(270deg); -webkit-transform:rotate(270deg); -moz-transform:rotate(270deg); -ms-transform:rotate(270deg);}}")
        css.append(f"SPAN.{prefix}-rotate--90 {{transform:rotate(-90deg); -webkit-transform:rotate(-90deg); -moz-transform:rotate(-90deg); -ms-transform:rotate(-90deg);}}")
        css.append(f"SPAN.{prefix}-rotate--180 {{transform:rotate(-180deg); -webkit-transform:rotate(-180deg); -moz-transform:rotate(-180deg); -ms-transform:rotate(-180deg);}}")
        css.append(f"SPAN.{prefix}-rotate--270 {{transform:rotate(-270deg); -webkit-transform:rotate(-270deg); -moz-transform:rotate(-270deg); -ms-transform:rotate(-270deg);}}")
        css.append(f"SPAN.{prefix}-flip-vertical {{transform:scaleY(-1); -webkit-transform:scaleY(-1); -moz-transform:scaleY(-1); -ms-transform:scaleY(-1);}}")
        css.append(f"SPAN.{prefix}-flip-horizontal {{transform:scaleX(-1); -webkit-transform:scaleX(-1); -moz-transform:scaleX(-1); -ms-transform:scaleX(-1);}}")
        css.append(f"SPAN.{prefix}-spin {{animation:spin 4s infinite linear; -webkit-animation:spin 4s infinite linear; -moz-animation:spin 4s infinite linear; -ms-animation:spin 4s infinite linear;}}")
        css.append("@-webkit-keyframes spin {0%{-webkit-transform: rotate(0deg);}100% {-webkit-transform: rotate(360deg);}}")
        css.append("@-moz-keyframes spin {0%{-moz-transform: rotate(0deg);}100% {-moz-transform: rotate(360deg);}}")
        css.append("@-ms-keyframes spin {0%{-ms-transform: rotate(0deg);}100% {-ms-transform: rotate(360deg);}}")
        # icons
        for icon in icons:
            if icon.useSourceSvg:
                with open(icon.src, 'r') as file:
                    svg = file.read()
                    svg = svg[svg.index("<svg"):].replace("\r\n","").replace("\r","").replace("\n","")
                    xml_tree = etree.fromstring(svg)
                    viewBox = xml_tree.get("viewBox").split(" ")
                    width = viewBox[2]
                    height = viewBox[3]
                    data = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
                    css.append(f"SPAN.{prefix}-{icon.name} {{min-width:{width};min-height:{height};background:url('data:image/svg+xml;base64,{data}') no-repeat left top; background-size:cover;}}")
            else:
                css.append(f"SPAN.{prefix}-{icon.name}::before {{content:\"\\{format(icon.finalcode, 'x')}\";}}")
        # save css
        with open(path.replace("\\","/").replace(".def",".css"), "w") as file:
            file.write("\n".join(css))
        # html
        html = []
        html.append("<html>")
        html.append("<head>")
        html.append(f"<link rel='stylesheet' href='{os.path.basename(path).replace(".def",".css")}' type='text/css' media='all' />")
        html.append("</head>")
        html.append("<body>")
        html.append("<div style='display:flex; flex-wrap:wrap;'>")
        for icon in icons:
            html.append(f"<div style='font-size:1.5em;width:1.5em;height:1.5em; border:1px red solid; display:inline-flex; align-items:center; justify-content:center;' title='{icon.name}'>")
            html.append(f"<span class='icon icon-{icon.name}'></span>")
            html.append("</div>")
        html.append("</div>")
        html.append("</body>")
        html.append("</html>")
        # save html
        with open(path.replace("\\","/").replace(".def",".html"), "w") as file:
            file.write("\n".join(html))

        
# main
def main():
    commandsManager = CommandsManager()
    commandsManager.register(instance = Fonticons())
    commandsManager.execute(sys.argv) 
if __name__ == "__main__":
    main()

