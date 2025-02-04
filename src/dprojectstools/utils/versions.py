
def get_version_from_file(path: str) -> str:
    result = None
    code = ""
    with open(path, 'r') as file:
        code = file.read()
    # AssemblyInfo.vb
    if path.endswith(".vb"):
        key = "<Assembly: AssemblyVersion(\""
        i = code.index(key)
        if i != -1:
            i += len(key)
            j = code.index(")", i)
            if j != -1:
                result = code[i:j].replace('"','')
    # return result
    return result
