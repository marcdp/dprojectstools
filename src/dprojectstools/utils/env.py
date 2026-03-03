def needs_quotes(value: str) -> bool:
    return (
        value.strip() != value or
        any(c in value for c in ' #=$"\'\\\n\r\t')
    )

def quote_env_value(value: str) -> str:
    escaped = (
        value
        .replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
    )
    return f'"{escaped}"'

def format_env_line(key, value):
    if value is None:
        value = ""
    if needs_quotes(value):
        value = quote_env_value(value)
    return f"{key}={value}"