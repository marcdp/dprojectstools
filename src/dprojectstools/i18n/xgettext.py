from dataclasses import dataclass
from ..commands import command, Argument, Flag, CommandsManager
from typing import Annotated, List
from charset_normalizer import from_path as charset_from_path
from datetime import timezone, datetime
from .translator import Translator
import sys
import os
from pathlib import Path


# class TextEntry
@dataclass
class TextEntry:
    sources: List[str] = None
    comments: str = None
    context: str = None
    tags: List[str] = None
    key: str = None
    value: str = None
    original_value: str = None


# class
class Xgettext:

    # methods
    @command()
    def xgettext(self, 
        # input
        path: Annotated[str,  Argument("PATH")],
        extensions: Annotated[List[str], Flag('e', "File extension", alias="extension")] = ".html,.js,.vb,.aspx,.ashx,.ascx,.csharp,.java,.cpp,.c,.cs",
        function_names: Annotated[List[str], Flag('f', "Function name", alias="function-name")]= None,
        exclusions: Annotated[List[str], Flag('E', "Exclude path",alias="exclude-path")] = None,
        # output
        locales: Annotated[List[str], Flag('l', "Locales",alias="locale")] = "en,es",
        project_name: Annotated[str,  Flag('p', "Project name")] = None,
        project_version: Annotated[str,  Flag('v', "Project version")] = None,
        output: Annotated[str,  Flag('o', "Output path")] = None,
        tags: Annotated[List[str],  Flag('t', "Tag", alias="tag")] = None,
        verbose: Annotated[bool,  Flag('V', "Verbose")] = False
        # tag: None
    ):

        # vars
        self._path = path
        self._extensions = extensions
        self._function_names = function_names
        self._exclusions = exclusions
        self._locales = locales
        self._project_name = project_name
        self._project_version = project_version
        self._tags = tags
        self._verbose = verbose
        # get entries
        entries = self.process()
        # remove duplicates
        keys_aux = []
        for i in range(len(entries) - 1, -1, -1):
            current_entry = entries[i]
            if f"{current_entry.context}::{current_entry.key}" in keys_aux:
                entries.pop(i)
                existing_entry = None
                for j in range(len(entries)):
                    if f"{entries[j].context}::{entries[j].key}" == f"{current_entry.context}::{current_entry.key}":
                        existing_entry = entries[j]
                        break
                if existing_entry is not None:
                    existing_entry.sources.extend(current_entry.sources)
            else:
                keys_aux.append(f"{current_entry.context}::{current_entry.key}")
        for entry in entries:
            entry.sources.sort()
        # compute tags
        for entry in entries:
            entry_tags = []
            for source in entry.sources:
                for tag in self._tags:
                    if "=" in tag:
                        tagName = tag.split("=")[0]
                        tagValue = tag.split("=")[1]
                        if tagName.lower() in source.lower():
                            if tagValue not in entry_tags:
                                entry_tags.append(tagValue)
            entry.tags = sorted(entry_tags)
        # sort
        entries = sorted(entries, key = lambda x: (x.key.casefold(), x.key))
        # //s: (s.lower(), s)
        
        # save POT
        self.save_PO(entries, None, os.path.join(output, project_name + ".pot"))
        
        # delete invalid PO files
        for file in Path(output).glob("*.po"):
            file_locale = file.name[:2]
            if not file_locale in self._locales:
                os.remove(file)

        # generate PO files
        for locale in self._locales:
            self.save_PO(entries, locale, os.path.join(output, project_name + "." + locale + ".po"))

    # utils
    def process(self):
        entries = []
        for filename in Path(self._path).rglob("*"):
            # process exclusions
            validExclusion = True
            for exclusion in self._exclusions:
                if exclusion in str(filename):
                    validExclusion = False
            validExtension = False
            # extensions
            for extension in self._extensions:
                if filename.name.endswith(extension):
                    validExtension = True
            # valid
            if validExclusion and validExtension:
                # charset
                if self._verbose:
                    print(filename)
                charset = charset_from_path(filename)
                encoding = charset.best().encoding
                # read as lines
                lines = ""
                with open(filename, "r", encoding=encoding) as file:
                    lines = file.readlines()
                # extension
                extension = Path(filename).suffix
                # process
                if extension == ".html" or extension == ".xml":
                    entries.extend(self.process_html(filename, lines))
                elif extension == ".cs" or extension == ".vb":
                    entries.extend(self.process_cs_vb_js(filename, lines))
                elif extension == ".aspx" or extension == ".ashx" or extension == ".ascx":
                    entries.extend(self.process_cs_vb_js(filename, lines))
                elif extension == ".js":
                    entries.extend(self.process_cs_vb_js(filename, lines))
                else:
                    raise ValueError("Extension not implemented:", extension)
        # return
        return entries

    def process_cs_vb_js(self, filename, lines):
        entries = []
        iline = 1
        for line in lines:
            for func_name in self._function_names:
                if func_name in line:
                    i = line.find(func_name)
                    while i != -1:
                        is_previous_char_space_dot_tab_or_equal = i > 0 and line[i-1] in [' ', '(', '{', '.', ':', '\t', '=', ',', '+']
                        is_next_char_parenthesis_and_quote = (line.find(func_name + '("', i) == i or line.find(func_name + ' ("', i) == i)
                        is_next_char_parenthesis_and_single_quote = (line.find(func_name + "('", i) == i or line.find(func_name + " ('", i) == i) 
                        if is_previous_char_space_dot_tab_or_equal and (is_next_char_parenthesis_and_quote or is_next_char_parenthesis_and_single_quote):
                            delimiter = '"'
                            if is_next_char_parenthesis_and_quote:
                                delimiter = "\""
                            if is_next_char_parenthesis_and_single_quote:
                                delimiter = "'"
                            j = i + len(func_name) + 1 + 1
                            k = -1
                            skip_next = False
                            for ii in range(j, len(line)):
                                if skip_next:
                                    skip_next = False
                                elif line[ii] == delimiter:
                                    if filename.name.endswith(".vb") and ii < len(line) - 1 and line[ii+1] == delimiter:
                                        skip_next = True
                                    elif ii > 1 and line[ii-1] == "\\" and line[ii-2] != "\\":
                                        skip_next = True
                                    else:
                                        k = ii
                                        break
                            if k != -1:
                                key = line[j:k].replace("\\\"", "\"").replace('""', '"').strip()
                                # print(key, iline)
                                original_value = key
                                comments = ""
                                context = ""
                                tags = ""
                                value = ""
                                if '|' in key:
                                    key = key[:key.index('|')].strip()
                                if '::' in key:
                                    context = key[:key.index('::')]
                                    key = key[key.index('::')+2:]
                                if '::' in original_value:
                                    original_value = original_value[original_value.index('::')+2:]                                
                                if key:
                                    relative_filename = os.path.relpath(filename, self._path).replace("\\", "/")
                                    entries.append(TextEntry([f"{relative_filename}:{iline}"], comments, context, tags, key, value, original_value))
                                    
                        i = line.find(func_name, i + 1)
            iline += 1
        return entries

    def process_html(self, filename, lines):
        entries = []
        return entries

    def process_js(self, filename, lines):
        entries = []
        return entries

    # POT generation
    def save_PO(self, entries, locale, filename):
        result = []
        # cache
        cache = dict()
        if locale != None:
            if os.path.exists(filename):
                with open(filename, "r", encoding="utf-8") as file:
                    context = ""
                    key = ""
                    for line in file.readlines():
                        if line.startswith("msgctxt"):
                            context = line[7:].strip().replace("\"", "")
                        if line.startswith("msgid"):
                            key = line[5:].strip().replace("\\\"","\"").replace("\\'", "'")
                            key = key[1:]
                            key = key[:-1]
                        if line.startswith("msgstr"):
                            value = line[6:].strip()
                            value = value[1:]
                            value = value[:-1]
                            value = value.replace("\\\"","\"").replace("\\\'", "'")
                            cache[context + "::" + key] = value
                            context = ""
                            key = ""
        # main entry
        result.append(f"#: ")
        result.append(f"msgid \"\"")
        result.append(f"msgstr \"\"")
        result.append(f"\"Project-Id-Version: {self._project_name} {self._project_version}\\n\"")
        result.append(f"\"POT-Creation-Date: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")}\\n\"")
        if locale != None:
            result.append(f"\"Language: {locale}\\n\"")
        result.append(f"\"MIME-Version: 1.0\\n\"")
        result.append(f"\"Content-Type: text/plain; charset=UTF-8\\n\"")
        result.append(f"\"Content-Transfer-Encoding: 8bit\\n\"")
        result.append(f"\"X-Generator: i18n-xgettext\\n\"")
        result.append("")
        # tranlator
        translator = Translator()
        # entries
        for entry in entries:
            # id
            # value
            value = entry.value
            # get translate
            if locale != None:
                original_value_list = entry.original_value.split("|")
                locale_index = self._locales.index(locale)
                if locale_index < len(original_value_list):
                    value = original_value_list[locale_index]
                else:
                    value = ""
                #if not entry.context + "::" + entry.key in cache:
                #    print("- NOT FOUND: " + entry.context + "::" + entry.key)
                if entry.context + "::" + entry.key in cache:
                    cached_value = cache.get(entry.context + "::" + entry.key)
                    if cached_value != "":
                        value = cached_value
            # autotranslate
            if locale != None:
                if value == "":
                    if self._locales[0] != locale:
                        print(f"translating to '{locale}': {entry.key}")
                        value = translator.translate(entry.key, self._locales[0], locale)
                        result.append(f"# autotranslated:true")
            # print tags 
            tags = []
            if entry.tags != None:
                for tag in entry.tags:
                    tags.append(tag)
            if len(tags) > 0:
                result.append(f"# tags: {', '.join(tags)}")
            # print sources
            for source in entry.sources:
                result.append(f"#: {source}")
            # print context
            if entry.context != "":
                result.append(f"msgctxt \"{entry.context.replace("'", "\\'").replace("\"", "\\\"")}\"")
            # print id
            result.append(f"msgid \"{entry.key.replace("'", "\\'").replace("\"", "\\\"")}\"")
            # print value
            result.append(f"msgstr \"{value.replace("'", "\\'").replace("\"", "\\\"")}\"")
            result.append("")
        # save
        text = os.linesep.join(result)
        with open(filename, "w", encoding = "utf-8", newline="") as file:
            file.write(text)

# main
def main():
    commandsManager = CommandsManager()
    commandsManager.register(instance = Xgettext())
    commandsManager.execute(sys.argv) 
if __name__ == "__main__":
    main()

