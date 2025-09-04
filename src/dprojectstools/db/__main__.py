import sys
import os
from dataclasses import dataclass
from typing import Annotated
from dprojectstools.commands import command, Argument, Flag, CommandsManager
from .db_inspector import create_inspector
from .db_schema import Schema
from .generator_sql import GeneratorSql
from .generator_cs import GeneratorCsV1
from .generator_xml import GeneratorXml
from .generator_vb import GeneratorVb

# print xml schema
@command("Prints xml schema of a database", examples=[
    "db xml \"sqlite:///path/to/database.db\"",
    "db xml \"sqlite:///C:\\path\\to\\database.db\"",
    "db xml \"postgresql://scott:tiger@localhost/dbname\"",
    "db xml \"mssql+pyodbc://localhost/my_db?driver=ODBC+Driver+17+for+SQL+Server\""
])
def xml( source: Annotated[str,  Argument("CONNECTION_STRING")]):
    schema = Schema.create(source, create_inspector)
    xml  = GeneratorXml.create(schema).generate()
    print(xml)

@command("Creates database from xml schema file, or from database")
def sql( 
        source: Annotated[str,  Argument("PATH_OR_CONNECTION_STRING")]
    ):
    schema = Schema.create(source, create_inspector)
    sql = GeneratorSql.create(schema).generate()
    print(sql)

@command("Creates database from xml schema file, or from database", examples=[
    "db cs db\\schema.xml \"namespace=MyNamespace\" > src\MyNamespace\DBContext.cs"
])
def cs( 
        source: Annotated[str,  Argument("PATH_OR_CONNECTION_STRING")],
        settings: Annotated[str,  Argument("SETTINGS")] = "",
    ):
    schema = Schema.create(source, create_inspector)
    cs = GeneratorCsV1.create(schema, dict(item.split('=', 1) for item in settings.strip(';').split(';') if '=' in item)).generate()
    print(cs)

# main
def main():
    commandsManager = CommandsManager()
    commandsManager.register(module = sys.modules[__name__])
    commandsManager.execute(sys.argv, default_show_help=True)
if __name__ == "__main__":
    main()






