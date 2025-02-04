from lxml import etree

def get_xpath_value(path:str, xpath:str) -> str:
    tree = etree.parse(path)
    root = tree.getroot()
    ser_name = root.xpath(xpath)[0]
    print(ser_name)
    pass

def get_xpath_attribute_value(path:str, xpath:str, attribute: str):
    tree = etree.parse(path)
    root = tree.getroot()
    node = root.xpath(xpath)[0]
    return node.attrib[attribute]

def set_xpath_attribute_value(path:str, xpath:str, attribute: str, value: str):
    tree = etree.parse(path)
    root = tree.getroot()
    node = root.xpath(xpath)[0]
    node.attrib[attribute] = value
    tree.write(path, pretty_print=True, xml_declaration=True, encoding="UTF-8")



