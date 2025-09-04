from sqlalchemy import Integer, create_engine, inspect, text, Column as SQLAlchemColumn
from .db_schema import Schema, Table, Column, PrimaryKey, ForeignKey, Index, View, Sequence, Procedure, Script, OnDelete, OnUpdate, DataType, ProcedureArgument

def datatype_name_to_class(column_type_name):
    if column_type_name == "BIGINT":
        return DataType.Bigint
    elif column_type_name == "BINARY":
        return DataType.Binary
    elif column_type_name == "BLOB":
        return DataType.Varbinary
    elif column_type_name == "BOOLEAN" or column_type_name == "BIT":
        return DataType.Boolean
    elif column_type_name == "CHAR":
        return DataType.Char
    elif column_type_name == "CLOB" or column_type_name == "LONG":
        return DataType.Nvarchar
    elif column_type_name == "DATE":
        return DataType.Date
    elif column_type_name == "DATETIME":
        return DataType.DateTime
    elif column_type_name == "DECIMAL":
        return DataType.Decimal
    elif column_type_name == "DOUBLE":
        return DataType.Double
    elif column_type_name == "DOUBLE_PRECISION":
        return DataType.Double
    elif column_type_name == "FLOAT":
        return DataType.Float
    elif column_type_name == "INT":
        return DataType.Int
    elif column_type_name == "JSON":
        return DataType.Json
    elif column_type_name == "INTEGER":
        return DataType.Int
    elif column_type_name == "NCHAR":
        return DataType.Nchar
    elif column_type_name == "NVARCHAR":
        return DataType.Nvarchar
    elif column_type_name == "NUMERIC" or column_type_name == "NUMBER":
        return DataType.Numeric
    elif column_type_name == "REAL":
        return DataType.Real
    elif column_type_name == "SMALLINT":
        return DataType.Smallint
    elif column_type_name == "TEXT":
        return DataType.Nvarchar
    elif column_type_name == "TIME":
        return DataType.Time
    elif column_type_name == "TIMESTAMP":
        return DataType.Timestamp
    elif column_type_name == "UUID":
        return DataType.UniqueIdentifier
    elif column_type_name == "VARBINARY":
        return DataType.Varbinary
    elif column_type_name == "VARCHAR" or column_type_name == "VARCHAR2" or column_type_name == "ROWID":
        return DataType.Varchar
    else:
        raise ValueError(f"Invalid column datatype: {column_type_name}")
    
# methods
class Inspector:
    
    # ctor
    def __init__(self, engine):
        self._engine = engine
        self._inspector = inspect(engine)
        
    # methods
    def get_table_names(self):
        return self._inspector.get_table_names()
    
    def get_table(self, table_name):
        table = Table(table_name)
        table.description = ""
        table.columns = []
        for col in self.get_table_columns(table_name):
            column = Column(col["name"])
            column.description = col["comment"] or ""
            # type
            column_type = col["type"]
            column_type_name = type(column_type).__name__
            if isinstance(column_type, dict):
                column_type_name = column_type["name"]                
            column.data_type = datatype_name_to_class(column_type_name)
            # size
            if hasattr(column_type, "length"):
                column.size = column_type.length
            elif isinstance(column_type, dict) and "length" in column_type:
                column.size = column_type["length"]
            # nullable
            column.null = col["nullable"]
            # default
            column.default = col["default"]
            if isinstance(column.default, str):
                column.default = column.default.replace("\n", "").replace("\r", "")
            # autoincrement
            if "autoincrement" in col:
                column.is_autoincrement = col["autoincrement"]
            # precision
            if hasattr(column_type, "precision"):
                column.precision = column_type.precision
            # scale
            if hasattr(column_type, "scale"):
                column.scale = column_type.scale
            # collation
            if hasattr(column_type, "collation"):
                column.collation = column_type.collation
            table.columns.append(column)            
        # pk
        table.primary_key = None
        pk_constraint = self.get_table_pk(table_name)        
        if pk_constraint != None and pk_constraint["name"] != None:
            table.primary_key = PrimaryKey(pk_constraint["name"])
            table.primary_key.description = ""
            table.primary_key.columns = pk_constraint["constrained_columns"]
        # fk
        table.foreign_keys = []
        for fk in self.get_table_fks(table_name):
            foreign_key = ForeignKey(fk["name"])
            foreign_key.description = ""
            foreign_key.columns = fk["constrained_columns"]
            foreign_key.ref_table = fk["referred_table"]
            foreign_key.ref_columns = fk["referred_columns"]
            foreign_key.on_delete = fk["options"]
            foreign_key.on_delete = OnDelete.NO_ACTION
            if "ondelete" in fk["options"] and fk["options"]["ondelete"] == "CASCADE":
                 foreign_key.on_delete = OnDelete.CASCADE
            elif "ondelete" in fk["options"] and fk["options"]["ondelete"] == "SET DEFAULT":
                 foreign_key.on_delete = OnDelete.SET_DEFAULT
            elif "ondelete" in fk["options"] and fk["options"]["ondelete"] == "SET NULL":
                 foreign_key.on_delete = OnDelete.SET_NULL
            foreign_key.on_update = OnUpdate.NO_ACTION
            if "onupdate" in fk["options"] and fk["options"]["onupdate"] == "CASCADE":
                 foreign_key.on_update = OnUpdate.CASCADE
            elif "onupdate" in fk["options"] and fk["options"]["onupdate"] == "SET DEFAULT":
                 foreign_key.on_update = OnUpdate.SET_DEFAULT
            elif "onupdate" in fk["options"] and fk["options"]["onupdate"] == "SET NULL":
                 foreign_key.on_update = OnUpdate.SET_NULL
            table.foreign_keys.append(foreign_key)
        # indexes
        table.indexes = []
        for idx in self.get_table_indexes(table_name):
            index = Index(idx["name"])
            index.unique = idx["unique"]
            index.columns = idx["column_names"]
            table.indexes.append(index)
        # records
        table.records = []
        # return
        return table
    
    def get_table_columns(self, table_name):
        return self._inspector.get_columns(table_name)

    def get_table_pk(self, table_name):
        return self._inspector.get_pk_constraint(table_name)
    
    def get_table_fks(self, table_name):
        return self._inspector.get_foreign_keys(table_name)

    def get_table_indexes(self, table_name):
        return self._inspector.get_indexes(table_name)

    # views
    def get_view_names(self):
        return self._inspector.get_view_names()
    
    def get_view(self, view_name):
        view = View(view_name)
        view.description = ""
        view.content = self.get_view_definition(view_name)
        return view

    def get_view_definition(self, view_name):
        return self._inspector.get_view_definition(view_name)
    
    # procedures
    def get_procedure_names(self):
        raise NotImplemented()

    def get_procedure(self, procedure_name):
        raise NotImplemented()

    # sequences
    def get_sequence_names(self):
        return self._inspector.get_sequence_names()

    def get_sequence(self, sequence_name):
        raise NotImplemented()

    # schema    
    def get_schema(self):
        database = Schema()
        database.collation = self.get_database_collation()
        # tables
        database.tables = []
        for table_name in self.get_table_names():
            print("table", table_name, "...")
            database.tables.append(self.get_table(table_name))
        # views
        database.views = []
        for view_name in self.get_view_names():
            print("view", view_name, "...")
            database.views.append(self.get_view(view_name))
        # procedures
        database.procedures = []
        for procedure_name in self.get_procedure_names():
            print("procedure", procedure_name, "...")
            database.procedures.append(self.get_procedure(procedure_name))
        # sequences
        database.sequences = []
        for sequence_name in self.get_sequence_names():
            print("sequence", sequence_name, "...")
            database.sequences.append(self.get_sequence(sequence_name))            
        # scripts
        database.scripts = []
        # return
        return database
    
    def execute_scalar(self, sql, params = None):
        with self._engine.connect() as connection:
            result = connection.execute(text(sql), params)
            return result.scalar() 
    def execute_fetchall(self, sql, params = None):
        with self._engine.connect() as connection:
            result = connection.execute(text(sql), params)
            return result.fetchall() 


# sql server
class InspectorSqlServer(Inspector):

    def get_database_collation(self):
        return self.execute_scalar("SELECT DATABASEPROPERTYEX(DB_NAME(), 'Collation') AS Collation")
    
    def get_sequence(self, sequence_name):
        result = self.execute_fetchall("SELECT name, CAST(start_value as int) as init_value, CAST(increment as int) as increment_by FROM sys.sequences WHERE name = :sequence_name", {"sequence_name": sequence_name})
        sequence = Sequence(sequence_name)
        sequence.description = ""
        sequence.init_value = result[0][1]
        sequence.increment_by = result[0][2]
        return sequence
    
    def get_procedure_names(self):
        result = []
        for row in self.execute_fetchall("SELECT name FROM sys.procedures ORDER BY name"):
            result.append(row[0])
        return result

    def get_procedure(self, procedure_name):
        procedure = Procedure(procedure_name)
        procedure.description = ""
        procedure.content = self.execute_scalar("SELECT definition  FROM sys.sql_modules  WHERE object_id = OBJECT_ID(:procedure_name)", {"procedure_name": procedure_name})
        return procedure


# sqlite
class InspectorSqlite(Inspector):
    def get_database_collation(self):
        for collation in self.execute_fetchall("PRAGMA collation_list"):
            return collation[1]
    def get_procedure_names(self):
        return []
    def get_sequence_names(self):
        return []


# MySql
class InspectorMySql(Inspector):
    def get_database_collation(self):
        return self.execute_scalar("SELECT @@collation_database")


# Postgresql
class InspectorPostgresql(Inspector):
    def get_database_collation(self):
        return self.execute_scalar("SELECT datcollate FROM pg_database WHERE datname = current_database()")


# Oracle
class InspectorOracle(Inspector):
    
    
    
    def get_database_collation(self):
        return self.execute_scalar("SELECT VALUE FROM NLS_DATABASE_PARAMETERS WHERE PARAMETER = 'NLS_CHARACTERSET'")
    def get_table_names(self):
        names = self._inspector.get_table_names()
        return [name.upper() for name in names]    
    def get_table_pk(self, table_name):
        result = self._inspector.get_pk_constraint(table_name)
        if result["name"] != None:
            result["name"] = result.get("name").upper()
            result["constrained_columns"] = [constrained_column.upper() for constrained_column in result["constrained_columns"]]        
        return result    
    def get_table_fks(self, table_name):
        result = self._inspector.get_foreign_keys(table_name)
        for fk in result:
            fk["name"] = fk.get("name").upper()
            fk["constrained_columns"] = [constrained_column.upper() for constrained_column in fk["constrained_columns"]]        
            fk["referred_table"] = fk.get("referred_table").upper()
            fk["referred_columns"] = [constrained_column.upper() for constrained_column in fk["referred_columns"]]        
        return result
    def get_table_columns(self, table_name):
        columns = self._inspector.get_columns(table_name)
        for col in columns:
            col["name"] = col.get("name").upper()
            column_type = col["type"]
            column_type_name = type(column_type).__name__
            if column_type_name == "NUMBER":
                # NUMBER(7) = INT
                precision = 0
                scale = 0
                if hasattr(column_type, "precision"):
                    precision = column_type.precision
                if hasattr(column_type, "scale"):
                    scale = column_type.scale
                if scale == 0:
                    if precision >= 10:
                        col["type"] = {"name": "BIGINT"}
                    elif 4 < precision and precision <= 9:
                        col["type"] = {"name": "INT"}
                    elif precision <= 4:
                        col["type"] = {"name": "SMALLINT"}
                #if isinstance(scale, int) and isinstance(precision, int) and scale != 0 and precision + scale <= 7:
                #    col["type"] = {"name": "FLOAT"}
            elif column_type_name == "VARCHAR" and column_type.length == 1:
                # NUMBER(7) = INT
                col["type"] = {"name": "CHAR", "length": 1}

        return columns
    def get_table_indexes(self, table_name):
        result = self._inspector.get_indexes(table_name)
        for idx in result:
            idx["name"] = idx.get("name").upper()
            if idx.get("expressions") != None:
                idx["column_names"] = idx.get("expressions")
            else:
                idx["column_names"] = [column_name.upper() for column_name in idx["column_names"]]        
        # print()
        # print(result)
        # print()
        # exit()
        return result
    def get_view_names(self):
        names = self._inspector.get_view_names()
        return [name.upper() for name in names]    
    def get_procedure_names(self):
        result = []
        for row in self.execute_fetchall("SELECT OBJECT_NAME FROM USER_PROCEDURES WHERE OBJECT_TYPE = 'PROCEDURE'"):
            result.append(row[0].upper())
        return result
    def get_procedure(self, procedure_name):
        procedure = Procedure(procedure_name)
        procedure.description = ""
        procedure.content = "" # self.execute_scalar("SELECT dbms_metadata.get_ddl('PROCEDURE',:procedure_name,'') FROM dual", {"procedure_name": procedure_name})
        procedure.arguments = []
        for row in self.execute_fetchall("SELECT ARGUMENT_NAME, PLS_TYPE, DEFAULTED, DEFAULT_VALUE, DEFAULT_LENGTH, IN_OUT, DATA_LENGTH, DATA_PRECISION, DATA_SCALE FROM all_arguments WHERE object_name = :procedure_name ORDER BY POSITION", {"procedure_name": procedure_name}):
            name = row[0]
            description = ""
            data_type = datatype_name_to_class(row[1])
            null = (row[2] == 'N')
            size = int(row[6]) if row[6] != None else 0
            precision = int(row[7]) if row[7] != None else 0
            scale = int(row[8]) if row[8] != None else 0
            direction = row[5]
            argument = ProcedureArgument(name, description, data_type, size, precision, scale, null, direction) 
            procedure.arguments.append(argument)
        return procedure
    def get_sequence_names(self):
        names = self._inspector.get_sequence_names()
        return [name.upper() for name in names]    
    def get_sequence(self, sequence_name):
        result = self.execute_fetchall("SELECT MIN_VALUE, INCREMENT_BY FROM USER_SEQUENCES WHERE SEQUENCE_NAME = :sequence_name", {"sequence_name": sequence_name})
        sequence = Sequence(sequence_name)
        sequence.description = ""
        sequence.init_value = result[0][0]
        sequence.increment_by = result[0][1]
        return sequence
    

# factory
def create_inspector(connection_string):
    # create inspector
    engine = create_engine(connection_string)
    if connection_string.startswith("mssql+"):
        inspector = InspectorSqlServer(engine)
    elif connection_string.startswith("sqlite:"):
        inspector = InspectorSqlite(engine)
    elif connection_string.startswith("mysql:"):
        inspector = InspectorMySql(engine)
    elif connection_string.startswith("postgresql"):
        inspector = InspectorPostgresql(engine)
    elif connection_string.startswith("oracle"):
        inspector = InspectorOracle(engine)
    else:    
        inspector = Inspector(engine)
    return inspector
    
    