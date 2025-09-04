from .db_schema import OnDelete, OnUpdate

class GeneratorSql:

    def __init__(self, schema):
        self._separator = ";"
        self._schema = schema

    def create(schema):
        return GeneratorSql(schema)

    def disable_foreign_keys(self):
        return ""
    
    def enable_foreign_keys(self):
        return ""

    def generate(self):
        sql = []
        for table in self._schema.tables:
            sql.append(self.create_table(table))
        # fks
        sql.append(f"--- fks")
        for table in self._schema.tables:
            for foreign_key in table.foreign_keys:
                line = self.create_table_foreign_key(table, foreign_key)
                sql.append(line)
        # inserts
        sql.append(f"--- inserts")
        for table in self._schema.tables:
            for record in table.records:
                sql.append(self.insert_record(table, record))
        # return
        return "\n".join(sql)
    
    def create_table(self, table):
        sql = []
        sql.append(f"--- table {table.name}")
        sql.append(f"CREATE TABLE {table.name} (")
        column_index = 0
        for column in table.columns:
            line = []
            line.append("  ")
            line.append(column.name)
            if column.precision > 0 or column.scale > 0:
                line.append(f"{column.data_type}({column.precision},{column.scale})")
            elif column.size > 0:
                line.append(f"{column.data_type}({column.size})")
            else:
                line.append(f"{column.data_type}")
            if column.null:
                line.append(f"NULL")
            else:
                line.append(f"NOT NULL")
            if column.default != None:
                line.append(f" DEFAULT {str(column.default)}")
            if column.description != "":
                line.append(f"--- {column.description}")
            sql.append(" ".join(line) + ",")
            column_index += 1
        if table.primary_key != None:
            sql.append(f"   PRIMARY KEY ({",".join(table.primary_key.columns)}), ")
        sql.append(f"){self._separator}")        
        for index in table.indexes:
            sql.append(self.create_table_index(table, index))
        return "\n".join(sql)

    def alter_table(self, table):
        return ""

    def drop_table(self, table):
        return f"DROP TABLE {table.name}{self._separator}"
    
    def create_table_foreign_key(self, table, foreign_key):
        line = f"ALTER TABLE {table.name} ADD CONSTRAINT {foreign_key.name} FOREIGN KEY ({",".join(foreign_key.columns)}) REFERENCES {foreign_key.ref_table} ({",".join(foreign_key.ref_columns)}) "
        if foreign_key.on_delete != OnDelete.NO_ACTION:
            line += "ON DELETE " + foreign_key.on_delete.name.replace("_"," ")
        if foreign_key.on_update != OnUpdate.NO_ACTION:
            line += "ON UPDATE " + foreign_key.on_update.name.replace("_"," ")
        return line + self._separator
    
    def create_table_index(self, table, index):
        return f"CREATE {"UNIQUE" if index.unique else ""} INDEX {index.name} ON {table.name} ({' '.join(index.columns)}){self._separator}"
    
    def insert_record(self, table, record):
        sql = []
        sql.append(f"INSERT INTO {table.name} (")
        index = 0
        for key in record.values:
            if index > 0:
                sql.append(",")
            sql.append(key)
            index += 1
        sql.append(") VALUES (")
        index = 0
        for key in record.values:
            if index > 0:
                sql.append(",")
            value = record.values[key]
            sql.append(self.format_value(value))
            index += 1
        sql.append(f"){self._separator}")
        return " ".join(sql)
    
    def format_value(self, value):
        return "'" + value.replace("'","''") + "'"
    
    def create_view(self, view):
        pass
    def alter_view(self, view):
        pass
    def drop_view(self, view):
        pass

    def create_procedure(self, procedure):
        pass
    def alter_procedure(self, procedure):
        pass
    def drop_procedure(self, procedure):
        pass

    def create_sequence(self, sequence):
        pass
    def alter_sequence(self, sequence):
        pass
    def drop_sequence(self, sequence):
        pass

class GeneratorSqlSqllite(GeneratorSql):

    def disable_foreign_keys(self):
        return "PRAGMA foreign_keys = OFF;"
    
    def enable_foreign_keys(self):
        return "PRAGMA foreign_keys = ON;"
