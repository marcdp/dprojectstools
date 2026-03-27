from xml.etree import ElementTree
from xml.dom import minidom
from dataclasses import dataclass
from enum import Enum
from flask import json
from lxml import etree
import os

# model
class DataType(Enum):
    Char = 2
    Varchar = 3
    Nchar = 4
    Nvarchar = 5
    Binary = 6
    Varbinary = 7
    Numeric = 8
    Decimal = 9
    Smallint = 10
    Tinyint = 11
    Int = 12
    Bigint = 13
    Float = 14
    Real = 15
    Double = 16
    Boolean = 17
    Date = 18
    DateTime = 19
    Time = 20
    Timestamp = 21
    Interval = 22
    UniqueIdentifier = 23
    Json = 24
    def from_str(value: str):
        value = value.lower()
        for member in DataType:
            if member.name.lower() == value:
                return member
    def to_str(self):        
        return self.name.lower()

class OnDelete(Enum):
    NO_ACTION = 1
    CASCADE = 2
    SET_NULL = 3
    SET_DEFAULT = 4

class OnUpdate(Enum):
    NO_ACTION = 1
    CASCADE = 2
    SET_NULL = 3
    SET_DEFAULT = 4

@dataclass
class PrimaryKey:
    name: str
    description: str = ""
    columns: list[str] = None

@dataclass
class ForeignKey:
    name: str
    description: str = ""
    columns: list[str] = None
    ref_table: str = ""
    ref_columns: list[str] = None
    on_delete: OnDelete = False
    on_update: OnUpdate = False

@dataclass
class Index:
    name: str
    description: str = ""
    unique: bool = False
    columns: list[str] = None

@dataclass
class Record:
    values: dict
    
@dataclass
class Column:
    name: str
    description: str = ""
    data_type: DataType = DataType.Varchar
    is_autoincrement: bool = False
    null: bool = False
    size: int = 0
    default: any = None
    precision: int = 0
    scale: int = 0
    collation: str = None
    

@dataclass
class Table:
    name: str
    description: str = ""
    columns: list[Column] = None
    primary_key: PrimaryKey = None
    foreign_keys: list[ForeignKey] = None
    indexes: list[Index] = None
    records: list[Record] = None

@dataclass
class Sequence:
    name: str
    description: str = ""
    init_value: int = 0
    increment_by: int = 1

@dataclass
class View:
    name: str
    description: str = ""
    content: str = None

@dataclass
class ProcedureArgument:
    name: str
    description: str = ""
    data_type: DataType = DataType.Varchar
    size: int = 0
    precision: int = 0
    scale: int = 0
    null: bool = False
    direction: str = ""
    
@dataclass
class Procedure:
    name: str
    description: str = ""
    arguments: list[ProcedureArgument] = None
    content: str = None

@dataclass
class Script:
    name: str
    description: str
    content: str

@dataclass
class Schema:

    # fields
    name: str = ""
    description: str = ""
    collation: str = ""
    tables: list[Table] = None
    views: list[View] = None
    procedures: list[Procedure] = None
    sequences: list[Sequence] = None
    scripts: list[Script] = None

    # ctor
    def __init__(self):
        self.tables = []
        self.views = []
        self.procedures = []
        self.sequences = []
        self.scripts = []

    # static methods
    def create(source: str, create_inspector = None):
        if os.path.exists(source):
            with open(source, "r", encoding='utf-8') as file:
                xml = file.read()
                schema = Schema()
                schema.from_xml(xml)
                return schema
        else:
            inspector = create_inspector(source)
            schema = inspector.get_schema()
            return schema

    # methods
    def from_xml(self, xml: str):
        # load xml
        xml_doc = etree.fromstring(xml)
        # load xsd
        xsd_filename = os.path.join(os.path.dirname(__file__), "schema.xsd")
        with open(xsd_filename, 'r') as xsd_f:
            xsd_schema = etree.XMLSchema(etree.parse(xsd_f))
            if not xsd_schema.validate(xml_doc):
                for error in xsd_schema.error_log:
                    print(f"Error: {error.message}, Line: {error.line}, Column: {error.column}")
        # database
        name = xml_doc.get("name")
        description = xml_doc.get("description", "")
        # tables
        self.tables = []
        for table_xml in xml_doc.findall("tables/table"):
            table = Table(table_xml.get("name"))
            table.description = table_xml.get("description", "")
            table.columns = []
            for column_xml in table_xml.findall("columns/column"):
                column = Column(column_xml.get("name"))
                column.description = column_xml.get("description", "")                
                column.data_type = DataType.from_str(column_xml.get("dataType", "VARCHAR"))
                column.is_autoincrement = bool(column_xml.get("isAutoincrement",False))
                column.null = bool(column_xml.get("null",False))
                column.size = int(column_xml.get("size",0))
                column.default = column_xml.get("default", None)
                column.precision = int(column_xml.get("precision",0))
                column.scale = int(column_xml.get("scale",0))
                column.collation = column_xml.get("collation", "")
                table.columns.append(column)
            table.primary_key = None
            for primaryKey_xml in table_xml.findall("primaryKey"):
                table.primary_key = PrimaryKey(primaryKey_xml.get("name"))
                table.primary_key.columns = primaryKey_xml.get("columns", "").split(",")
            table.foreign_keys = []
            for foreignKey_xml in table_xml.findall("foreignKeys/foreignKey"):
                foreing_key = ForeignKey(foreignKey_xml.get("name"))
                foreing_key.columns = foreignKey_xml.get("columns", "").split(",")
                foreing_key.ref_table = foreignKey_xml.get("refTable", "")
                foreing_key.ref_columns = foreignKey_xml.get("refColumns", "").split(",")
                foreing_key.on_delete = OnDelete.NO_ACTION
                if foreignKey_xml.get("onDelete") == "cascade":
                    foreing_key.on_delete = OnDelete.CASCADE
                if foreignKey_xml.get("onDelete") == "setnull":
                    foreing_key.on_delete = OnDelete.SET_NULL
                if foreignKey_xml.get("onDelete") == "setdefault":
                    foreing_key.on_delete = OnDelete.SET_DEFAULT
                foreing_key.on_update = OnUpdate.NO_ACTION
                if foreignKey_xml.get("onUpdate") == "cascade":
                    foreing_key.on_update = OnUpdate.CASCADE
                if foreignKey_xml.get("onUpdate") == "setnull":
                    foreing_key.on_update = OnUpdate.SET_NULL
                if foreignKey_xml.get("onUpdate") == "setdefault":
                    foreing_key.on_update = OnUpdate.SET_DEFAULT
                table.foreign_keys.append(foreing_key)
            table.indexes = []
            for index_xml in table_xml.findall("indexes/index"):
                index = Column(index_xml.get("name"))
                index.unique = bool(index_xml.get("unique",False))
                index.columns = index_xml.get("columns", "").split(",")
                table.indexes.append(index)
            table.records = []
            for record_xml in table_xml.findall("records/record"):
                record = Column(index_xml.get("record"))
                record.values = record_xml.attrib
                table.records.append(record)
            self.tables.append(table)
        # views
        self.views = []
        for view_xml in xml_doc.findall("views/view"):
            view = View(view_xml.get("name"))
            view.description = view_xml.get("description", "")
            view.content = view_xml.text
            self.views.append(view)
        # procedures
        self.procedures = []
        for procedure_xml in xml_doc.findall("procedures/procedure"):
            procedure = Procedure(procedure_xml.get("name"))
            procedure.description = procedure_xml.get("description", "")
            procedure.arguments = []
            for argument_xml in procedure_xml.find("arguments").findall("argument"):
                argument = ProcedureArgument(argument_xml.get("name"))
                argument.description = argument_xml.get("description", "")
                argument.data_type = DataType.from_str(argument_xml.get("dataType", "VARCHAR"))
                argument.size = int(argument_xml.get("size",0))
                argument.precision = int(argument_xml.get("precision",0))
                argument.scale = int(argument_xml.get("scale",0))
                argument.null = bool(argument_xml.get("null",False))
                argument.direction = argument_xml.get("direction", None)
                procedure.arguments.append(argument)

            procedure.content = procedure_xml.text
            self.procedures.append(procedure)
        # sequences
        self.sequences = []
        for sequence_xml in xml_doc.findall("sequences/sequence"):
            sequence = Sequence(sequence_xml.get("name"))
            sequence.desequenceion = sequence_xml.get("desequenceion", "")
            sequence.initValue = sequence_xml.get("initValue", 0)
            sequence.incrementBy = sequence_xml.get("incrementBy", 0)
            self.sequences.append(sequence)
        # scripts
        self.scripts = []
        for script_xml in xml_doc.findall("scripts/script"):
            script = Script(script_xml.get("name"))
            script.description = script_xml.get("description", "")
            script.content = script_xml.text
            self.scripts.append(script)

