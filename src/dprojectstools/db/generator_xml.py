from xml.etree import ElementTree
from xml.dom import minidom
from xml.sax.saxutils import escape
from .db_schema import OnDelete, OnUpdate

def sanitize_xml_tree(elem):
    # Escape text
    if elem.text:
        elem.text = escape(elem.text)
    if elem.tail:
        elem.tail = escape(elem.tail)
    # Escape attributes
    # elem.attrib = {k: escape(v) for k, v in elem.attrib.items()}
    elem.attrib = {
        k: escape(str(v)) if v is not None else ""
        for k, v in elem.attrib.items()
    }

    # Recurse
    for child in elem:
        sanitize_xml_tree(child)

class GeneratorXml:

    def __init__(self, schema):
        self._separator = ";"
        self._schema = schema

    def create(schema):
        return GeneratorXml(schema)

    def generate(self):
        xml_database = ElementTree.Element("database")
        if self._schema.description != None and len(self._schema.description) > 0:
            xml_database.set("description", self._schema.description)
        if self._schema.collation != None and len(self._schema.collation) > 0:
            xml_database.set("collation", self._schema.collation)        
        # tables
        tables_xml = ElementTree.SubElement(xml_database, "tables")
        for table in self._schema.tables:
            table_xml = ElementTree.SubElement(tables_xml, "table")
            table_xml.set("name", table.name)
            if table.description != None and len(table.description) > 0:
                table_xml.set("description", table.description)
            # columns
            columns_xml = ElementTree.SubElement(table_xml, "columns")
            for column in table.columns:
                column_xml = ElementTree.SubElement(columns_xml, "column")
                column_xml.set("name", column.name)
                if column.description != None and len(column.description) > 0:
                    column_xml.set("description", column.description)
                column_xml.set("dataType", column.data_type.name.lower())
                if isinstance(column.size, int) and column.size > 0:
                    column_xml.set("size", str(column.size))
                if column.null:
                    column_xml.set("null", "true")
                if column.default != None:
                    column_xml.set("default", str(column.default))
                if column.is_autoincrement:
                    column_xml.set("isAutoincrement", "true")
                if isinstance(column.precision, int) and column.precision > 0:
                    column_xml.set("precision", str(column.precision))
                if isinstance(column.scale, int) and column.scale > 0:
                    column_xml.set("scale", str(column.scale))
                if column.collation != None and len(column.collation) > 0 and column.collation != self._schema.collation:
                    column_xml.set("collation", column.collation)
            # pk
            if table.primary_key != None:
                primaryKey_xml = ElementTree.SubElement(table_xml, "primaryKey")        
                primaryKey_xml.set("name", table.primary_key.name)
                primaryKey_xml.set("columns", ",".join(table.primary_key.columns))
            # fk
            foreignKeys_xml = ElementTree.SubElement(table_xml, "foreignKeys")        
            for foreign_key in table.foreign_keys:
                foreignKey_xml = ElementTree.SubElement(foreignKeys_xml, "foreignKey")        
                foreignKey_xml.set("name", foreign_key.name)
                foreignKey_xml.set("columns", ",".join(foreign_key.columns))
                foreignKey_xml.set("refTable", foreign_key.ref_table)
                foreignKey_xml.set("refColumns", ",".join(foreign_key.ref_columns))
                if foreign_key.on_delete != OnDelete.NO_ACTION:
                    foreignKey_xml.set("onDelete", str(foreign_key.on_delete.name.replace("_"," ")))
                if foreign_key.on_update != OnUpdate.NO_ACTION:
                    foreignKey_xml.set("onUpdate", str(foreign_key.on_update.name.replace("_"," ")))
            # idx
            indexes_xml = ElementTree.SubElement(table_xml, "indexes")        
            for index in table.indexes:
                index_xml = ElementTree.SubElement(indexes_xml, "index")        
                index_xml.set("name", index.name)
                if index.unique:
                    index_xml.set("unique", "true")
                if index.columns != None:
                    index_xml.set("columns", ",".join(index.columns))
            # records
            records_xml = ElementTree.SubElement(table_xml, "records")        
            for record in table.records:
                record_xml = ElementTree.SubElement(records_xml, "record")        
                for key in record.values.keys:
                    record_xml.set(key, str(record.values[key]))
                
        # views
        views_xml = ElementTree.SubElement(xml_database, "views")
        for view in self._schema.views:
            view_xml = ElementTree.SubElement(views_xml, "view")
            view_xml.set("name", view.name)
            if view.description != None and len(view.description) > 0:
                view_xml.set("description", view.description)
            view_xml.text = view.content
        # procedures
        procedures_xml = ElementTree.SubElement(xml_database, "procedures")
        for procedure in self._schema.procedures:
            procedure_xml = ElementTree.SubElement(procedures_xml, "procedure")
            procedure_xml.set("name", procedure.name)
            if procedure.description != None and len(procedure.description) > 0:
                procedure_xml.set("description", procedure.description)        
            procedure_arguments_xml = ElementTree.SubElement(procedure_xml, "arguments")
            for argument in procedure.arguments:
                procedure_argument_xml = ElementTree.SubElement(procedure_arguments_xml, "argument")
                procedure_argument_xml.set("name", argument.name)
                if argument.description != None and len(argument.description) > 0:
                    procedure_argument_xml.set("description", argument.description)
                procedure_argument_xml.set("dataType", argument.data_type.name.lower())
                if argument.size > 0:
                    procedure_argument_xml.set("size", str(argument.size))
                if argument.precision > 0:
                    procedure_argument_xml.set("precision", str(argument.precision))
                if argument.scale > 0:
                    procedure_argument_xml.set("scale", str(argument.scale))
                if argument.null:
                    procedure_argument_xml.set("null", "true")
                procedure_argument_xml.set("direction", str(argument.direction))
            procedure_content_xml = ElementTree.SubElement(procedure_xml, "content")
            procedure_content_xml.text = procedure.content
        # sequences
        sequences_xml = ElementTree.SubElement(xml_database, "sequences")
        for sequence in self._schema.sequences:
            sequence_xml = ElementTree.SubElement(sequences_xml, "sequence")
            sequence_xml.set("name", sequence.name)
            if sequence.description != None and len(sequence.description) > 0:
                sequence_xml.set("description", sequence.description)
            sequence_xml.set("initValue", str(sequence.init_value))
            sequence_xml.set("incrementBy", str(sequence.increment_by))
        # scripts
        scripts_xml = ElementTree.SubElement(xml_database, "scripts")
        for script in self._schema.scripts:
            script_xml = ElementTree.SubElement(scripts_xml, "script")
            script_xml.set("name", script.name)
            if script.description != None and len(script.description) > 0:
                script_xml.set("description", script.description)
        # sanitize xml
        sanitize_xml_tree(xml_database)
        # xml
        xml = ElementTree.tostring(xml_database, encoding="utf-8", ).decode("utf-8")
        # indent
        parsed_xml = minidom.parseString(xml)
        return parsed_xml.toprettyxml(indent="  ")
