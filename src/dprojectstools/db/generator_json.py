import json
from xml.etree import ElementTree
from xml.dom import minidom
from xml.sax.saxutils import escape
from .db_schema import OnDelete, OnUpdate
 
def remove_none(obj):
    if isinstance(obj, dict):
        return {
            k: remove_none(v)
            for k, v in obj.items()
            if v is not None
        }
    elif isinstance(obj, list):
        return [
            remove_none(item)
            for item in obj
            if item is not None
        ]
    else:
        return obj
    

class GeneratorJson:

    def __init__(self, schema):
        self._separator = ";"
        self._schema = schema

    def create(schema):
        return GeneratorJson(schema)

    def generate(self):
        xml_database = ElementTree.Element("database")
        result = {
            "name": self._schema.name,
            "description": self._schema.description if self._schema.description else None,
            "collation": self._schema.collation if self._schema.collation else None,
            "tables": [],
            "views": [],
            "procedures": [],
            "sequences": [],
            "scripts": []
        }
        for table in self._schema.tables:
            tableDict = {
                "description": table.description if table.description else None,
                "columns": [],
                "primary_key": {
                    "name": table.primary_key.name,
                    "description": table.primary_key.description if table.primary_key.description else None,
                    "columns": table.primary_key.columns
                } if table.primary_key else None,
                "foreign_keys": [],
                "indexes": [],
                "records": []
            }
            result["tables"].append({table.name: tableDict})
            for column in table.columns:
                columnDict = {
                    "name": column.name,
                    "description": column.description if column.description else None,
                    "data_type": column.data_type.to_str(),
                    "is_autoincrement": True if column.is_autoincrement else None,
                    "null": True if column.null else None,
                    "size": column.size if column.size > 0 else None,
                    "default": column.default if column.default else None,
                    "precision": column.precision if column.precision > 0 else None,
                    "scale": column.scale if column.scale > 0 else None,
                    "collation": column.collation if column.collation else None
                }
                tableDict["columns"].append(columnDict)
            for foreign_key in table.foreign_keys:
                foreignKeyDict = {
                    "name": foreign_key.name,
                    "description": foreign_key.description if foreign_key.description else None,
                    "columns": foreign_key.columns,
                    "ref_table": foreign_key.ref_table,
                    "ref_columns": foreign_key.ref_columns,
                    "on_delete": foreign_key.on_delete.name if foreign_key.on_delete != OnDelete.NO_ACTION else None,
                    "on_update": foreign_key.on_update.name if foreign_key.on_update != OnUpdate.NO_ACTION else None
                }
                tableDict["foreign_keys"].append(foreignKeyDict)
            for index in table.indexes:
                indexDict = {
                    "name": index.name,
                    "description": index.description if index.description else None,
                    "unique": index.unique if index.unique else None,
                    "columns": index.columns
                }
                tableDict["indexes"].append(indexDict)
            for record in table.records:
                recordDict = {
                    "values": record.values
                }
                tableDict["records"].append(recordDict)
        for view in self._schema.views:
            viewDict = {
                "name": view.name,
                "description": view.description if view.description else None,
                "content": view.content
            }
            result["views"].append(viewDict)
        for procedure in self._schema.procedures:
            procedureDict = {
                "name": procedure.name,
                "description": procedure.description if procedure.description else None,
                "arguments": [],
                "content": procedure.content
            }
            result["procedures"].append(procedureDict)
            for argument in procedure.arguments:
                argumentDict = {
                    "name": argument.name,
                    "description": argument.description if argument.description else None,
                    "data_type": argument.data_type.to_str(),
                    "size": argument.size if argument.size > 0 else None,
                    "precision": argument.precision if argument.precision > 0 else None,
                    "scale": argument.scale if argument.scale > 0 else None,
                    "null": True if argument.null else None,
                    "direction": argument.direction
                }
                procedureDict["arguments"].append(argumentDict)
        for sequence in self._schema.sequences:
            sequenceDict = {
                "name": sequence.name,
                "description": sequence.description if sequence.description else None,
                "init_value": sequence.init_value,
                "increment_by": sequence.increment_by
            }
            result["sequences"].append(sequenceDict)
        for script in self._schema.scripts:
            scriptDict = {
                "name": script.name,
                "description": script.description if script.description else None,
                "content": script.content
            }
            result["scripts"].append(scriptDict)        
        clean_obj = remove_none(result)
        return json.dumps(clean_obj, indent=4)
