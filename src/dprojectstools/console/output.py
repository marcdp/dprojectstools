import sys
import yaml
from dataclasses import asdict, is_dataclass
from .sequences import *
from pathlib import Path

# print utils
def print_info(message: str = "") -> None:
    GRAY = "\033[90m"
    RESET = "\033[0m"
    if sys.stdout.isatty():
        print(f"{GRAY}{message}{RESET}", file=sys.stdout, flush=True)
    else:
        print(message, file=sys.stdout, flush=True)

def print_warning(message: str = "") -> None:
    YELLOW = "\033[33m"
    RESET = "\033[0m"
    if sys.stdout.isatty():
        print(f"{YELLOW}{message}{RESET}", file=sys.stderr, flush=True)
    else:
        print(message, file=sys.stdout, flush=True)

def print_error(message: str = "") -> None:
    RED = "\033[31m"
    RESET = "\033[0m"
    if sys.stdout.isatty():
        print(f"{RED}{message}{RESET}", file=sys.stderr, flush=True)
    else:
        print(message, file=sys.stderr, flush=True)

def print_table(items, fields) -> str:
    def resolve_value(item, field_path):
        value = item
        for part in field_path.split("."):
            if isinstance(value, dict):
                value = value.get(part, "")
            else:
                value = getattr(value, part, "")
        return value
    def normalize_value(value):
        if isinstance(value, list):
            return ", ".join(str(x) for x in value)
        return str(value)

    headers = [field.split(".")[-1].upper() for field in fields]

    rows = []
    for item in items:
        row = []
        for field in fields:
            value = resolve_value(item, field)
            row.append(normalize_value(value))
        rows.append(row)

    widths = []
    for i, header in enumerate(headers):
        width = len(header)
        for row in rows:
            width = max(width, len(row[i]))
        widths.append(width)

    header_line = "  ".join(headers[i].ljust(widths[i]) for i in range(len(headers)))
    sep_line = "  ".join("-" * widths[i] for i in range(len(headers)))
    body_lines = [
        "  ".join(row[i].ljust(widths[i]) for i in range(len(fields)))
        for row in rows
    ]
    print("\n".join([header_line, sep_line] + body_lines))


# yaml utils
def to_yaml_safe(value):
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {k: to_yaml_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [to_yaml_safe(v) for v in value]
    if isinstance(value, tuple):
        return [to_yaml_safe(v) for v in value]
    return value

class IndentYamlDumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)
        
def print_yaml( value: object, indent: int = 2) -> None:
    if is_dataclass(value):
        value = asdict(value)
    value = to_yaml_safe(value)
    print_info(yaml.dump(value,
        Dumper=IndentYamlDumper,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        indent=indent))
