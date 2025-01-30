import inspect
import types
import os
import sys
from typing import List, get_type_hints
from dataclasses import dataclass
from ..console import Sequences
from .. import clipboard


# default command
# multi flag values List like: --para 123 --param 222 --param 5444
# flag boolean with negation: --no-flag
# flags with --flag=value --> split in --flag value
# password prompt
# confirm option
# default value from envvar

# global vars
order = 0

# decorator 
def command(title: str, index: int = 0, alias: list[str] = None, examples: list[str] = None):
    def decorator(func):
        global order
        order += 1
        setattr(func, "title", title) 
        setattr(func, "order", order) 
        setattr(func, "index", index) 
        setattr(func, "alias", alias) 
        setattr(func, "examples", examples) 
        return func
    return decorator

# Argument
class Argument:
    def __init__(self, title: str = "", subtitle: str = ""):
        self.title = title
        self.subtitle = subtitle

# Flag
class Flag:
    def __init__(self, char: chr, title: str = "", subtitle: str = ""):
        self.chr = char
        self.title = title
        self.subtitle = subtitle



# data classes
@dataclass
class CommandArgument:
    name: str
    title: str
    subtitle:str
    required: bool
    type: str
    default: any

@dataclass
class CommandFlag:
    name: str
    title: str
    subtitle: str
    required: bool
    type: str
    default: any
    char: chr

@dataclass
class Command:
    name: List[str]
    alias: List[str]
    examples: List[str]
    title: str
    arguments: List[CommandArgument]
    flags: List[CommandFlag]
    instance: object
    func: any
    order:int
    registerOrder:int
    index: int

# data classes
@dataclass
class ReplHistoryLine:
    line: str
    result: str


# class
class CommandsManager:

    def __init__(self, title=None, indent = 0):
        # ctor
        self._title = title
        self._indent = indent
        self._name = ""
        self._argv = []
        self._commands = []
        self._registerOrder = 0
        self.exitCode = 0

    # methods
    def register(self, instance = None, prefix: str = ""):
        # register main decorated functions or decorated function from instance
        if instance is None:
            for name, obj in inspect.getmembers(__import__('__main__')):
                if inspect.isfunction(obj) and name.startswith(prefix) and hasattr(obj, "title"):
                    self.registerFunction(None, obj, prefix)
        else:
            for name, obj in inspect.getmembers(type(instance), predicate=inspect.isfunction):
                if inspect.isfunction(obj) and name.startswith(prefix) and hasattr(obj, "title"):
                    self.registerFunction(instance, obj, prefix)
        self._registerOrder += 1

    def registerFunction(self, instance, func, prefix: str = ""):
        # create a command fron function
        func_name = func.__name__
        command_name = func_name[len(prefix):].split("_")
        command_title = getattr(func, "title")
        command_order = getattr(func, "order")
        command_index = getattr(func, "index")
        command_alias = getattr(func, "alias")
        command_examples = getattr(func, "examples")
        command_registerOrder = self._registerOrder
        # arguments
        command_arguments = []        
        for param_name, param in inspect.signature(func).parameters.items():
            # filter
            if param_name == "self":
                continue
            elif hasattr(param.annotation, "__metadata__"):
                metadata = param.annotation.__metadata__[0]
                if isinstance(metadata, Flag):
                    continue
            # name
            argument_name = param_name
            # title
            argument_title = ""
            argument_subtitle = ""
            if hasattr(param.annotation, "__metadata__"):
                metadata = param.annotation.__metadata__[0]
                argument_title = metadata.title
                argument_subtitle = metadata.subtitle
            # required
            argument_required = (param.default == inspect.Parameter.empty)
            #  type
            argument_type = None
            if hasattr(param.annotation, "__metadata__"):
                argument_type = param.annotation.__origin__.__name__
            # argument default
            argument_default = None
            if param.default != inspect.Parameter.empty:
                argument_default = param.default
            # crea CommandArgument
            argument = CommandArgument(argument_name, argument_title, argument_subtitle, argument_required, argument_type, argument_default)
            command_arguments.append(argument)
        # flags
        command_flags = []        
        for param_name, param in inspect.signature(func).parameters.items():
            # filter
            if param_name == "self":
                continue
            elif hasattr(param.annotation, "__metadata__"):
                metadata = param.annotation.__metadata__[0]
                if not isinstance(metadata, Flag):
                    continue
            else:
                continue
            # name
            flag_name = param_name                
            # title
            flag_title = ""
            flag_subtitle = ""
            if hasattr(param.annotation, "__metadata__"):
                metadata = param.annotation.__metadata__[0]
                flag_title = metadata.title
                flag_subtitle = metadata.subtitle
            # char
            flag_char = ""
            if hasattr(param.annotation, "__metadata__"):
                metadata = param.annotation.__metadata__[0]
                flag_char = metadata.chr
            # required
            flag_required = (param.default == inspect.Parameter.empty)
            #  type
            flag_type = None
            if hasattr(param.annotation, "__metadata__"):
                flag_type = param.annotation.__origin__.__name__
            # argument default
            flag_default = None
            if param.default != inspect.Parameter.empty:
                flag_default = param.default
            # crea CommandFlag
            flag = CommandFlag(flag_name, flag_title, flag_subtitle, flag_required, flag_type, flag_default, flag_char)
            command_flags.append(flag)
            
        # create Command
        command = Command(name=command_name, title=command_title, examples=command_examples, arguments=command_arguments, flags= command_flags, instance=instance, func=func, order=command_order, registerOrder=command_registerOrder, index=command_index, alias=command_alias)
        # create unexisting "parent" Commands
        aux_name = []
        for part_name in command.name[:-1]:
            aux_name.append(part_name)
            if not aux_name in [aux_command.name for aux_command in self._commands]:
                virtual_command = Command(name=aux_name, title="", examples=[], arguments=[], flags=[], instance=None, func=None, order=command_order, registerOrder=command_registerOrder, index=command_index, alias=None)
                self._commands.append(virtual_command)
        # add to the list of commands
        self._commands.append(command)

    def sort(self):
        # sort commands in register order
        self._commands.sort(key=lambda x: (x.registerOrder, x.order))
        # assign order index
        command_ant = None
        index = 0
        for command in self._commands:
            if command.func == None:
                continue
            if command.index != 0:
                index = command.index
            elif command_ant != None and command_ant.name[0] != command.name[0]:
                index  = int((index + 10) / 10) * 10
            else: 
                index += 1
            command.index = index
            command_ant = command        
    
        self._commands.sort(key=lambda x: x.index)

    def executeMenu(self):
        # sort
        self.sort()
        # title
        if self._title != None and self._title != "":
            print(self._title)
            print("*********")
        # menu
        indent = self._indent * "    "
        while True:
            # show menu
            print(indent + "Select an option:")
            print(indent + "=================")
            command_ant = None
            for command in self._commands:
                if command.func == None:
                    continue
                if command_ant == None and command.index > 1:
                    print(indent + f"   : ")
                if command_ant != None and (command_ant.name[0] != command.name[0] or command_ant.index < command.index - 1):
                    print(indent + f"   : ")
                print(indent + f"{command.index:2} : {command.title}")
                command_ant = command
            print(indent + f"   : ")
            # read option
            command_to_execute = None
            while command_to_execute == None:
                opcion = ""
                try:
                    opcion = input(f" ? : ")
                except KeyboardInterrupt:
                    print("^C")
                    return
                if opcion == "":
                    return 0
                try:
                    opcion_index =int(opcion)
                    for command in self._commands:
                        if command.index == opcion_index and command.func != None:
                            command_to_execute = command
                            break
                except:
                    pass
                if command_to_execute == None:
                    print(indent + f"{Sequences.FG_RED}     index not valid: {opcion}{Sequences.RESET}")
            # prepare args
            print()
            exec_args = {}
            errors = False
            if len(command_to_execute.arguments) > 0:
                for definition in command_to_execute.arguments + command_to_execute.flags:
                    attributes = []
                    if definition.default != None:
                        attributes.append(f"default is '{definition.default}'")
                    if definition.required:
                        attributes.append(f"*")
                    value = ""
                    try:
                        value = input(f"     {definition.title}{"" if len(attributes) == 0 else f" ({" ".join(attributes)})"}: ").strip()
                    except KeyboardInterrupt:
                        print("^C")
                        errors = True
                        break
                    # value by default
                    if not value and definition.default != None:
                        value = definition.default
                    # validates
                    if definition.required:
                        if value == "":
                            print(indent + f"{Sequences.FG_RED}     Error: argument required: '{definition.title}'{Sequences.RESET}")
                            errors = True
                            break
                    # converts
                    try:
                        if definition.type == "int":
                            value = int(value)
                        elif definition.type == "float":
                            value = float(value)
                        elif definition.type == "bool":
                            value = bool(value)
                        elif definition.type == "List":
                            value = value.split(",")
                    except:
                        print(indent + f"{Sequences.FG_RED}     Error: unable to convert argument '{definition.name}' to '{definition.type}': {value}{Sequences.RESET}")
                        errors = True
                        break
                    # set
                    exec_args[definition.name] = value; 
            # exec
            if not errors:
                # set gray
                # print(exec_args)
                print(f"{Sequences.FG_BRIGHT_BLACK}", end = "", flush = True)
                # invoke
                try:
                    if not command_to_execute.instance is None:
                        func_bounded = types.MethodType(command_to_execute.func, command_to_execute.instance)
                        result = func_bounded(**exec_args)
                    else:
                        result = command_to_execute.func(**exec_args)
                finally:
                    # reset
                    print(Sequences.RESET, end= "", flush= True)
            # empty line
            print()

    def executeRepl(self, handler, prompt = "? "):
        # repl
        history = []
        while True:
            # read input
            line = ""
            try:
                line = input(Sequences.FG_GREEN + prompt + Sequences.RESET).strip()
            except KeyboardInterrupt:
                print("^C")
                return
            # empty line
            if line == "":
                continue
            # command
            if line.startswith("."):
                line = line[1:]
                if line.lower() == "quit":
                    break
                elif line.lower() == "history":
                    for historyItem in history:
                        print(f"{historyItem.line}: {historyItem.result}")
                elif line.lower() == "help":
                    print(f"  .help")
                    print(f"  .history")
                    print(f"  .quit")
                    if len(self._commands) > 0:
                        print(f"  ---")
                        for command in self._commands:
                            args= []
                            for argument in command.arguments:
                                args.append(f"--{argument.name}")
                                args.append(f"{Sequences.FG_BRIGHT_BLACK}<{argument.name if argument.title == "" else argument.title}>{Sequences.RESET}")
                            print(f"  .{" ".join(command.name):10} {" ".join(args)} {Sequences.FG_BRIGHT_BLACK}# {command.title}{Sequences.RESET}")
                else:
                    command = line.split()
                    command.insert(0, "")
                    self.execute(command)
                continue
            # set gray
            print(f"{Sequences.FG_BRIGHT_BLACK}", end = "", flush = True)
            # eval
            try:
                result = handler(line, history)
            except Exception as e:
                print(f"{Sequences.FG_RED}Error: {e}{Sequences.RESET}") 
                continue
            finally:
                print(Sequences.RESET, end= "", flush= True)
            # add to historic
            history.append(ReplHistoryLine(line=line, result=str(result)))
            # print result
            print(result) 
            # copy to clip board
            clipboard.copy(result)

    def executeHelp(self, name: str, recursive: bool = False):
        # help
        indent_subcommands = 25
        indent_flags = 25
        indent_arguments = 25
        command = None
        commands = list(self._commands)
        commands.sort(key=lambda x: x.name)
        subcommands = []
        if name==[]:
            # root subcommands
            for aux in self._commands:
                if not recursive:
                    if len(aux.name)==1:
                        subcommands.append(aux)
                elif recursive:
                    if aux.func != None:
                        subcommands.append(aux)
        else:
            # subcommands
            for aux in self._commands:
                if aux.name == name:
                    command = aux
                elif not recursive:
                    if aux.name[:len(name)] == name:
                        subcommands.append(aux)
                elif recursive:
                    if aux.name[:len(name)] == name:
                        if aux.func != None:
                            subcommands.append(aux)
        # error
        if name != []:
            if command == None:
                print(f"{self._name}: error: '{' '.join(name)}' is not a command. See '{self._name} --help'.")
                print()
                return -1
            
        # usage
        usage = f"Usage: {self._name}" 
        if len(name) > 0 and len(self._commands) != 1:
            usage += f" {' '.join(name)}" 
        
        if len(subcommands)>0:
            usage += " COMMAND"
        if command != None:
            for argument in command.arguments:
                usage += " "    
                if not argument.required:
                    usage +="["    
                usage += argument.name
                if not argument.required:
                    usage +="]"    
        print()
        print(usage)

        # title
        if command == None:
            if self._title != None:
                print()
                print(self._title)
        else:
            if command.title != None and len(command.title) > 0:
                print()
                print(command.title)

        # subcommands
        if len(subcommands) > 0:
            print()
            print("Commands:")
            for subcommand in subcommands:
                subcommand_name = subcommand.name
                if command != None:
                    subcommand_name = subcommand_name[len(command.name):]
                if subcommand.alias != None:
                    subcommand_name = subcommand.alias
                print(f"  {' '.join(subcommand_name).ljust(indent_subcommands)} {subcommand.title}")
            
        # arguments
        if command != None and len(command.arguments) > 0 :
            print()
            print("Arguments:")
            for argument in command.arguments:
                line = "  "
                if not argument.required:
                    line += "["    
                line += argument.name
                if not argument.required:
                    line +="]"    
                # metadata
                metadata = []
                if argument.type != None:
                    metadata.append(argument.type)
                if argument.required:
                    metadata.append("required")
                else:
                    metadata.append("optional")
                    metadata.append(f"default:{argument.default}")
                line2 = f"{argument.title}"
                line2 += " (" + ", ".join(metadata) + ")"
                # print
                print(f"{line.ljust(indent_arguments)} {line2}")

        # options
        if command != None:
            if len(command.flags) > 0:
                print()
                print("Options:")
                for flag in command.flags:
                    # flag names
                    flag_names = [f"-{flag.char}", f"--{flag.name}"]
                    line = f"  {', '.join(flag_names)} " 
                    # placeholder
                    if flag.type != "bool":
                        line += f"<{flag.subtitle or flag.name}>"
                    # metadata
                    metadata = []
                    if flag.type != None:
                        metadata.append(flag.type)
                    if flag.required:
                        metadata.append("required")
                    else:
                        metadata.append("optional")
                        metadata.append(f"default: {flag.default}")
                    # print
                    line2 = f"{flag.title}"
                    line2 += " (" + ", ".join(metadata) + ")"
                    if len(line) > indent_flags:
                        print(line)
                        print(" "*indent_flags + f"{line2}")
                    else:
                        print(f"{line.ljust(indent_flags)} {line2}")
                
        # examples
        if command != None:
            if command.examples != None and len(command.examples) > 0:
                print()
                print("Examples:")
                for example in command.examples:
                    print(f"  {example}")
        # footer
        if len(name) == 0 and len(subcommands) > 0:
            print()
            print(f"Run '{self._name} COMMAND --help' for more information on a command.")

    def execute(self, argv = None, repl = None):
        # init 
        if argv == None:
            argv = []
        if len(argv) > 0:
            self._name = os.path.basename(argv[0])
            self._argv = argv
        else:
            self._name = ""
            self._argv = []

        # if single command exists, then assume its the main command
        if len(self._commands) == 1:
            self._argv = [self._argv[0]] + self._commands[0].name + self._argv[1:]

        # executes the command, by analizing argv
        if "--help" in self._argv:
            command = self._argv[1:]
            command.remove("--help")
            return self.executeHelp(command, recursive=True)
        elif "-h" in self._argv:
            command = self._argv[1:]
            command.remove("-h")
            return self.executeHelp(command, recursive=False)        
        
        # exec Repl
        if repl != None and len(self._argv)==1:
            return self.executeRepl(repl)
        
        # exec Menu
        if repl == None and len(self._argv)==1:
            return self.executeMenu()
        
        # exec Command
        command_to_execute = None
        for command in reversed(self._commands):
            command_name = command.alias if command.alias else command.name
            if len(command_name) <= len(self._argv) - 1:
                if command_name == self._argv[1:len(command_name)+1]:
                    command_to_execute = command
                    break
            if command_to_execute:
                break

        # if no command found, show error message
        if command_to_execute == None:
            print(f"{self._name}: error: command not found", file=sys.stderr)
            return -1
        
        # command found, but is virtual (does not have func), show help message
        if command_to_execute.func == None:
            command = self._argv[1:]
            if "--help" in command:
                command.remove("--help")
            if "--h" in command:
                command.remove("--h")
            command = command[len(command_to_execute.name):]
            
            if len(command) == 0: 
                return self.executeHelp(command_to_execute.name)
            else:
                print(f"{self._name}: error: invalid arguments: ", command, file=sys.stderr)
                return -1
        
        # read params
        command_args = self._argv[len(command_to_execute.name)+1:]
        command_args_dict = {}
        command_args_errors = []
        for flag in command_to_execute.flags:
            index = -1
            if "--" + flag.name in command_args:
                index = command_args.index("--" + flag.name)
            elif "-" + flag.char in command_args:
                index = command_args.index("-" + flag.char)
            if index == -1:
                if flag.required:
                    command_args_errors.append(f"flag missing: -{flag.char}, --{flag.name}")
                else:
                    command_args_dict[flag.name] = flag.default
            elif flag.type == "bool":
                command_args_dict[flag.name] = True
                command_args.pop(index)
            elif index + 1 == len(command_args):
                command_args_errors.append(f"flag value missing: -{flag.char}, --{flag.name}")
            else:
                flag_value = command_args[index + 1]
                command_args_dict[flag.name] = flag_value
                command_args.pop(index + 1)
                command_args.pop(index)
                try:
                    if flag.type == "int":
                        flag_value = int(flag_value)
                    elif flag.type == "float":
                        flag_value = float(flag_value)
                    elif flag.type == "bool":
                        flag_value = bool(flag_value)
                    elif flag.type == "List":
                        flag_value = flag_value.split(",")
                except:
                    command_args_errors.append(f"unable to convert flag '-{flag.char}, --{flag.name}' to '{flag.type}': {flag_value}")
        for argument in command_to_execute.arguments:
            argument_value = None
            if len(command_args) == 0:
                if argument.required:
                    command_args_errors.append(f"argument expected: '{argument.name}")
                    continue
                else:
                    argument_value  = argument.default
            else:
                argument_value = command_args.pop(0)
            try:
                if argument.type == "int":
                    argument_value = int(argument_value)
                elif argument.type == "float":
                    argument_value = float(argument_value)
                elif argument.type == "bool":
                    argument_value = bool(argument_value)
                elif argument.type == "List":
                    argument_value = argument_value.split(",")
            except:
                command_args_errors.append(f"unable to convert argument '{argument.name}: {argument_value}")
            command_args_dict[argument.name] = argument_value
        if len(command_args) > 0:
            for command_arg in command_args:
                command_args_errors.append(f"invalid argument: {command_arg}")
        if len(command_args_errors) > 0:
            for error in command_args_errors:
                print(f"{self._name}: error:", error, file=sys.stderr)
            return -1
        
        # invoke
        # print(command_args_dict)
        if not command_to_execute.instance is None:
            func_bounded = types.MethodType(command_to_execute.func, command_to_execute.instance)
            return func_bounded(**command_args_dict)
        else:
            return command_to_execute.func(**command_args_dict)

        
    
    
    

