from datetime import datetime
from .db_schema import Schema, Column, Table, Index, DataType
from .generator_xml import GeneratorXml

def column_to_net_type(column: Column):
    result = ""
    if column.data_type == DataType.Char:
        result = "char"
    if column.data_type == DataType.Varchar:
        result = "string"
    if column.data_type == DataType.Nchar:
        result = "char"
    if column.data_type == DataType.Nvarchar:
        result = "string"
    if column.data_type == DataType.Binary:
        result = "byte[]"
    if column.data_type == DataType.Varbinary:
        result = "bute[]"
    if column.data_type == DataType.Numeric:
        result = "decimal"
    if column.data_type == DataType.Decimal:
        result = "decimal"
    if column.data_type == DataType.Smallint:
        result = "short"
    if column.data_type == DataType.TinyInt:
        result = "byte"
    if column.data_type == DataType.Int:
        result = "int"
    if column.data_type == DataType.Bigint:
        result = "long"
    if column.data_type == DataType.Float:
        result = "float"
    if column.data_type == DataType.Real:
        result = "double"
    if column.data_type == DataType.Double:
        result = "double"
    if column.data_type == DataType.Boolean:
        result = "bool"
    if column.data_type == DataType.Date:
        result = "System.DateTime"
    if column.data_type == DataType.DateTime:
        result = "System.DateTime"
    if column.data_type == DataType.Time:
        result = "System.TimeSpan"
    if column.data_type == DataType.Timestamp:
        result = "System.TimeSpan"
    if column.data_type == DataType.Interval:
        result = "string"
    if column.data_type == DataType.UniqueIdentifier:
        result = "System.Guid"
    if column.data_type == DataType.Json:
        result = "string"
    if column.null:
        result + "?"
    return result

def get_table_column(table: Table, column_name: str):
    for column in table.columns:
        if column.name == column_name:
            return column
        
def get_pk_columns(table: Table):
    result = []
    for column_name in table.primary_key.columns:
        result.append(get_table_column(table, column_name))
    return result

def get_table_columns_by(table: Table, column_names: list[str]):
    result = []
    for column_name in column_names:
        result.append(get_table_column(table, column_name))
    return result

def get_columns_as_arguments(columns: list[Column]):
    result = []
    for column in columns:
        result.append(column.name)
    return ", ".join(result)

def get_columns_as_arguments_array(columns: list[Column]):
    result = []
    for column in columns:
        result.append(column.name)
    return "[" + ", ".join(result) + "]"

def get_columns_as_arguments_declaration(columns: list[Column]):
    result = []
    for column in columns:
        result.append(column_to_net_type(column) + " " + column.name)
    return ", ".join(result)

def get_columns_as_arguments_curly(columns: list[Column]):
    result = []
    for column in columns:
        result.append("{" + column.name + "}")
    return ", ".join(result)

def get_columns_as_id_array(columns: list[Column]):
    result = []
    for column in columns:
        result.append("id." + column.name + "")
    return "[" + ", ".join(result) + "]"

def get_columns_as_set(columns: list[Column]):
    result = []
    for column in columns:
        result.append(f"this.{column.name} = value.{column.name};")
    return " ".join(result)

def get_columns_as_to_string(columns: list[Column]):
    result = []
    for column in columns:
        result.append(f"this.{column.name}.ToString()")
    return " + ':' + ".join(result)

def get_columns_as_sql_where_and(columns: list[Column]):
    result = []
    for column in columns:
        result.append(f"{column.name}=?")
    return " AND ".join(result)

def get_columns_as_sql_insert(table: Table):
    result = []
    for column in table.columns:
        if not column.is_autoincrement:
            result.append(f"{column.name}")
    return ", ".join(result)

def get_columns_as_sql_insert_placeholder(table: Table):
    result = []
    for column in table.columns:
        if not column.is_autoincrement:
            result.append(f"?")
    return ", ".join(result)

def get_columns_as_sql_insert_array(table: Table):
    result = []
    for column in table.columns:
        if not column.is_autoincrement:
            result.append(f"entity.{column.name}")
    return "[" + ", ".join(result) + "]"

def get_columns_as_sql_update(table: Table):
    result = []
    for column in table.columns:
        if not column.name in table.primary_key.columns:
            result.append(f"{column.name}=?")
    return ", ".join(result)

def get_columns_as_sql_update_array(table: Table):
    result = []
    for column in table.columns:
        if not column.name in table.primary_key.columns:
            result.append(f"entity.{column.name}")
    for column_name in table.primary_key.columns:
        result.append(f"entity.{column_name}")
    return "[" + ", ".join(result) + "]"

def get_columns_as_sql_delete_array(table: Table):
    result = []
    for column_name in table.primary_key.columns:
        result.append(f"entity.{column_name}")
    return "[" + ", ".join(result) + "]"

def get_table_name_plural(table:Table):
    return table.name + "s"

def get_index_alias(table:Table, index:Index):
    result = []
    for column_name in index.columns:
        result.append(to_camel_case(column_name))
    return "".join(result)

def to_camel_case(snake_case_string):
    titleCaseVersion =  snake_case_string.title().replace("_", "")
    camelCaseVersion = titleCaseVersion[0].upper() + titleCaseVersion[1:]
    return camelCaseVersion

class GeneratorCsV1():

    # ctor
    def __init__(self, schema, settings):
        self._schema = schema
        self._settings = settings

    # static methods
    def create(schema: Schema, settings: dict):
        return GeneratorCsV1(schema, settings)    
    
    # methods
    def generate(self):
        name = self._settings.get("name", "") or "DBContext"
        namespace = self._settings.get("namespace", "MyNamespace")
        xml = GeneratorXml.create(self._schema).generate()
        code = []
        code.append(f"using System;")
        code.append(f"using System.Threading.Tasks;")
        code.append(f"using DProjects.Db;")
        code.append(f"using DProjects.Db.Schema;")
        code.append(f"")
        # namespace
        code.append(f"namespace {namespace} {{")
        code.append(f"")
        # dbcontext
        code.append(f"    //autogenerated on {datetime.now()}")
        code.append(f"    public class {name}([FromKeyedServices(\"{name}\")] IDBConnection dbConnection) {{")
        code.append(f"        //props")
        code.append(f"        public static DBSchemaDatabase DBSchema => DBSchemaDatabase.FromXmlDocument(@\"\n            {xml.replace("\"","\"\"").replace("\n", "\n            ")}\");")
        code.append(f"        public IDBConnection DBConnection => dbConnection;")
        for table in self._schema.tables:
            plural = get_table_name_plural(table)
            code.append(f"        public {plural} {plural} => new(DBConnection);")
        code.append(f"        //methods")
        code.append(f"        public void ApplySchemaChanges(bool applyChanges, ILogger<IDBConnection> logger) {{")
        code.append(f"            DBConnection.ApplySchemaChanges(DBSchema, applyChanges, logger);")
        code.append(f"        }}")
        code.append(f"        public void BeginTrans() {{")
        code.append(f"            DBConnection.BeginTrans();")
        code.append(f"        }}")
        code.append(f"        public void RollBackTrans() {{")
        code.append(f"            DBConnection.RollBackTrans();")
        code.append(f"        }}")
        code.append(f"        public void CommitTrans() {{")
        code.append(f"            DBConnection.CommitTrans();")
        code.append(f"        }}")
        code.append(f"    }}")
        code.append(f"")
        # vos
        for table in self._schema.tables:
            pk_columns = get_pk_columns(table)
            code.append(f"    public class {table.name} {{")
            code.append(f"        //id")
            code.append(f"        public class {table.name}Id({get_columns_as_arguments_declaration(pk_columns)}) {{")
            for column in pk_columns:
                code.append(f"            public {column_to_net_type(column)} {column.name} {{ get; set; }} = {column.name};")
            code.append(f"            public override string ToString() => {get_columns_as_to_string(pk_columns)};")
            code.append(f"        }}")
            code.append(f"        public {table.name}Id Id {{ get {{ return new {table.name}Id({get_columns_as_arguments(pk_columns)}); }} set {{ {get_columns_as_set(pk_columns)} }} }}")
            code.append(f"        //properties")
            for column in table.columns:
                code.append(f"        public {column_to_net_type(column)} {column.name} {{ get; set; }} = default;")
            code.append(f"    }}")
            code.append(f"")
        # repositories
        for table in self._schema.tables:
            plural = get_table_name_plural(table)
            pk_columns = get_pk_columns(table)
            code.append(f"    public class {plural}(IDBConnection dbConnection) {{")
            # find
            code.append(f"        //find")
            code.append(f"        public async Task<{table.name}?> FindByAsync(string where, object?[] arguments) {{")
            code.append(f"            return (await SelectRawAsync(BuildSqlSelect(\"*\", where), arguments)).FirstOrDefault<{table.name}>();")
            code.append(f"        }}")
            code.append(f"        public async Task<{table.name}?> FindAsync({table.name}.{table.name}Id id) {{")
            code.append(f"            return await FindByAsync(\"{get_columns_as_sql_where_and(pk_columns)}\", {get_columns_as_id_array(pk_columns)});")
            code.append(f"        }}")
            code.append(f"        public async Task<{table.name}?> FindAsync({ get_columns_as_arguments_declaration(pk_columns)}) {{")
            code.append(f"            return await FindByAsync(\"{get_columns_as_sql_where_and(pk_columns)}\", {get_columns_as_arguments_array(pk_columns)});")
            code.append(f"        }}")
            for index in table.indexes:
                if index.unique:
                    index_columns = get_table_columns_by(table, index.columns)
                    code.append(f"        public async Task<{table.name}?> FindBy{get_index_alias(table, index)}Async({get_columns_as_arguments_declaration(index_columns)}) {{")
                    code.append(f"            return await FindByAsync(\"{get_columns_as_sql_where_and(index_columns)}\", {get_columns_as_arguments_array(index_columns)});")
                    code.append(f"        }}")
            # get
            code.append(f"        //get")
            code.append(f"        public async Task<{table.name}> GetByAsync(string where, object?[] arguments) {{")
            code.append(f"            var result = (await SelectRawAsync(BuildSqlSelect(\"*\", where), arguments)).FirstOrDefault<{table.name}>();")
            code.append(f"            if (result == null) throw new Exception($\"Unable to get entity: not found: {{arguments}}\");")
            code.append(f"            return result;")
            code.append(f"        }}")
            code.append(f"        public async Task<{table.name}> GetAsync({table.name}.{table.name}Id id) {{")
            code.append(f"            var result = await FindByAsync(\"{get_columns_as_sql_where_and(pk_columns)}\", {get_columns_as_id_array(pk_columns)});")
            code.append(f"            if (result == null) throw new Exception($\"Unable to get entity: not found: {{id}}\");");
            code.append(f"            return result;")
            code.append(f"        }}")
            code.append(f"        public async Task<{table.name}> GetAsync({ get_columns_as_arguments_declaration(pk_columns)}) {{")
            code.append(f"            var result = await FindByAsync(\"{get_columns_as_sql_where_and(pk_columns)}\", {get_columns_as_arguments_array(pk_columns)});")
            code.append(f"            if (result == null) throw new Exception($\"Unable to get entity: not found: {get_columns_as_arguments_curly(pk_columns)}\");")
            code.append(f"            return result;")
            code.append(f"        }}")
            for index in table.indexes:
                if index.unique:
                    index_columns = get_table_columns_by(table, index.columns)
                    code.append(f"        public async Task<{table.name}?> GetBy{get_index_alias(table, index)}Async({get_columns_as_arguments_declaration(index_columns)}) {{")
                    code.append(f"            var result = await FindByAsync(\"{get_columns_as_sql_where_and(index_columns)}\", {get_columns_as_arguments_array(index_columns)});")
                    code.append(f"            if (result == null) throw new Exception($\"Unable to get entity: not found: {get_columns_as_arguments_curly(index_columns)}\");")
                    code.append(f"            return result;")
                    code.append(f"        }}")
            # count
            code.append(f"        //count")
            code.append(f"        public async Task<long> CountByAsync(string where, object?[] arguments) {{")
            code.append(f"            return await dbConnection.ExecuteScalarAsync<long>(BuildSqlSelect(\"COUNT(*)\", where), arguments);")
            code.append(f"        }}")
            for index in table.indexes:
                index_columns = get_table_columns_by(table, index.columns)
                code.append(f"        public async Task<long> CountBy{get_index_alias(table, index)}Async({get_columns_as_arguments_declaration(index_columns)}) {{")
                code.append(f"            return await CountByAsync(\"{get_columns_as_sql_where_and(index_columns)}\", {get_columns_as_arguments_array(index_columns)});")
                code.append(f"        }}")
            # exists
            code.append(f"        //exists")
            code.append(f"        public async Task<bool> ExistAsync({ get_columns_as_arguments_declaration(pk_columns)}) {{")
            code.append(f"            return await CountByAsync(\"{get_columns_as_sql_where_and(pk_columns)}\", {get_columns_as_arguments_array(pk_columns)}) > 0;")
            code.append(f"        }}")
            code.append(f"        public async Task<bool> ExistAsync({table.name}.{table.name}Id id) {{")
            code.append(f"            return await CountByAsync(\"{get_columns_as_sql_where_and(pk_columns)}\", {get_columns_as_id_array(pk_columns)}) > 0;")
            code.append(f"        }}")
            for index in table.indexes:
                index_columns = get_table_columns_by(table, index.columns)
                code.append(f"        public async Task<bool> ExistBy{get_index_alias(table, index)}Async({get_columns_as_arguments_declaration(index_columns)}) {{")
                code.append(f"            return await CountByAsync(\"{get_columns_as_sql_where_and(index_columns)}\", {get_columns_as_arguments_array(index_columns)}) > 0;")
                code.append(f"        }}")
            # select
            code.append(f"        //select")
            code.append(f"        public async Task<IReadOnlyList<{table.name}>> SelectByAsync(string where, object?[] arguments, string? orderBy = null, long offset = 0, int length = -1) {{")
            code.append(f"            return await SelectRawAsync(BuildSqlSelect(\"*\", where, orderBy, offset, length), arguments);")
            code.append(f"        }}")
            code.append(f"        public async Task<IReadOnlyList<{table.name}>> SelectAllAsync(string? orderBy = null, long offset = 0, int length = -1) {{")
            code.append(f"            return await SelectRawAsync(BuildSqlSelect(\"*\", \"\", orderBy, offset, length), []);")
            code.append(f"        }}")
            # selectAsStream
            code.append(f"        //selectAsStream")
            code.append(f"        public IAsyncEnumerable<{table.name}> SelectAsStreamAsync(string where, object?[] arguments, string? orderBy = null, long offset = 0, int length = -1) {{")
            code.append(f"            return SelectAsStreamAsync(BuildSqlSelect(\"*\", where, orderBy, offset, length), arguments);")
            code.append(f"        }}")
            code.append(f"        public IAsyncEnumerable<{table.name}> SelectAllAsStreamAsync(string? orderBy = null, long offset = 0, int length = -1) {{")
            code.append(f"            return SelectAsStreamAsync(BuildSqlSelect(\"*\", \"\", orderBy, offset, length), []);")
            code.append(f"        }}")
            # selectId
            code.append(f"        //selectId")
            code.append(f"        public async Task<{table.name}.{table.name}Id?> SelectIdAsync(string where, object?[] arguments) {{")
            code.append(f"            var dbTable = await dbConnection.ExecuteTableAsync(BuildSqlSelect(\"id_error\", where), arguments);")
            code.append(f"            if (dbTable.Rows.Count > 0) return MapToId(dbTable.Rows[0]);")
            code.append(f"            return null;")
            code.append(f"        }}")
            for index in table.indexes:
                if index.unique:
                    index_columns = get_table_columns_by(table, index.columns)
                    code.append(f"        public async Task<{table.name}.{table.name}Id?> SelectIdBy{get_index_alias(table, index)}Async({get_columns_as_arguments_declaration(index_columns)}) {{")
                    code.append(f"            return await SelectIdAsync(\"{get_columns_as_sql_where_and(index_columns)}\", {get_columns_as_arguments_array(index_columns)});")
                    code.append(f"        }}")
            # selectScalar
            code.append(f"        //selectScalar")
            code.append(f"        public async Task<T?> SelectScalarByAsync<T>(string column, string where, object?[] arguments, T? defaultValue = default) {{")
            code.append(f"            var dbTable = await dbConnection.ExecuteTableAsync(BuildSqlSelect(column, where), arguments);")
            code.append(f"            if (dbTable.Rows.Count > 0) return DProjects.Utils.ConvertUtils.To<T>(dbTable.Rows[0][0]);")
            code.append(f"            return defaultValue;")
            code.append(f"        }}")
            code.append(f"        public async Task<T?> SelectScalarAsync<T>(string column, { get_columns_as_arguments_declaration(pk_columns)}, T? defaultValue = default) {{")
            code.append(f"            return await SelectScalarByAsync<T>(column, \"{get_columns_as_sql_where_and(pk_columns)}\", {get_columns_as_arguments_array(pk_columns)}, defaultValue);")
            code.append(f"        }}")
            for index in table.indexes:
                if index.unique:
                    index_columns = get_table_columns_by(table, index.columns)
                    code.append(f"        public async Task<T?> SelectScalarBy{get_index_alias(table, index)}Async<T>(string column, {get_columns_as_arguments_declaration(index_columns)}, T? defaultValue = default) {{")
                    code.append(f"            return await SelectScalarByAsync<T>(column, \"{get_columns_as_sql_where_and(index_columns)}\", {get_columns_as_arguments_array(index_columns)}, defaultValue);")
                    code.append(f"        }}")
            # insert
            code.append(f"        //insert")
            code.append(f"        public async Task InsertAsync({table.name} entity) {{")
            code.append(f"            Validate(entity);")
            code.append(f"            await dbConnection.ExecuteNonQueryAsync(BuildSqlInsert(), {get_columns_as_sql_insert_array(table)});")
            code.append(f"        }}")
            # update
            code.append(f"        //upadte")
            code.append(f"        public async Task UpdateAsync({table.name} entity) {{")
            code.append(f"            Validate(entity);")
            code.append(f"            await dbConnection.ExecuteNonQueryAsync(BuildSqlUpdate(), {get_columns_as_sql_update_array(table)});")
            code.append(f"        }}")
            # delete
            code.append(f"        //delete")
            code.append(f"        public async Task<long> DeleteByAsync(string where, object?[] arguments) {{")
            code.append(f"            return await dbConnection.ExecuteNonQueryAsync(BuildSqlDelete(where), arguments);")
            code.append(f"        }}")
            code.append(f"        public async Task<long> DeleteAsync({table.name} entity) {{")
            code.append(f"            return await DeleteByAsync(\"{get_columns_as_sql_where_and(pk_columns)}\", {get_columns_as_sql_delete_array(table)});")
            code.append(f"        }}")
            code.append(f"        public async Task<long> DeleteAsync({table.name}.{table.name}Id id) {{")
            code.append(f"            return await DeleteByAsync(\"{get_columns_as_sql_where_and(pk_columns)}\", {get_columns_as_id_array(pk_columns)});")
            code.append(f"        }}")
            code.append(f"        public async Task<long> DeleteAsync({ get_columns_as_arguments_declaration(pk_columns)}) {{")
            code.append(f"            return await DeleteByAsync(\"{get_columns_as_sql_where_and(pk_columns)}\", {get_columns_as_arguments_array(pk_columns)});")
            code.append(f"        }}")
            for index in table.indexes:
                if index.unique:
                    index_columns = get_table_columns_by(table, index.columns)
                    code.append(f"        public async Task<long> DeleteBy{get_index_alias(table, index)}Async<T>({get_columns_as_arguments_declaration(index_columns)}) {{")
                    code.append(f"            return await DeleteByAsync(\"{get_columns_as_sql_where_and(index_columns)}\", {get_columns_as_arguments_array(index_columns)});")
                    code.append(f"        }}")
            # private
            code.append(f"        //private")
            code.append(f"        private async Task<IReadOnlyList<{table.name}>> SelectRawAsync(string sql, object?[] parameters) {{")
            code.append(f"            var result = new List<{table.name}>();")
            code.append(f"            using (var dbReader = await dbConnection.ExecuteReaderAsync(sql, parameters)) {{")
            code.append(f"                do {{")
            code.append(f"                    var dbRow = await dbReader.ReadAsync();")
            code.append(f"                    if (dbRow == null) break;")
            code.append(f"                    result.Add(MapTo(dbRow));")
            code.append(f"                }} while (true);")
            code.append(f"            }}")
            code.append(f"            return result.ToArray();")
            code.append(f"        }}")
            code.append(f"        private async IAsyncEnumerable<{table.name}> SelectRawAsStreamAsync(string sql, object?[] parameters) {{")
            code.append(f"            using (var dbReader = await dbConnection.ExecuteReaderAsync(sql, parameters)) {{")
            code.append(f"                do {{")
            code.append(f"                    var dbRow = await dbReader.ReadAsync();")
            code.append(f"                    if (dbRow == null) break;")
            code.append(f"                    yield return MapTo(dbRow);")
            code.append(f"                }} while (true);")
            code.append(f"            }}")
            code.append(f"        }}")
            code.append(f"        private {table.name} MapTo(DBRow dbRow) {{")
            code.append(f"            return new {table.name}(){{")
            for column in table.columns:
                code.append(f"                {column.name} = dbRow.GetAs<{column_to_net_type(column)}>(\"{column.name}\"),")
            code.append(f"            }};")
            code.append(f"        }}")
            code.append(f"        private {table.name}.{table.name}Id MapToId(DBRow dbRow) {{")
            code.append(f"            return new {table.name}.{table.name}Id(")
            index = 0
            for column in get_pk_columns(table):
                if index > 0:
                    code.append(f"                ,")    
                code.append(f"                dbRow.GetAs<{column_to_net_type(column)}>(\"{column.name}\")")
                index += 1
            code.append(f"            );")
            code.append(f"        }}")
            code.append(f"        private void Validate({table.name} entity) {{")
            for column in table.columns:
                if column.size > 0:
                    code.append(f"            if (entity.{column.name} != null && entity.{column.name}.Length > {column.size}) entity.{column.name} = entity.{column.name}.Substring(0, {column.size});")
            code.append(f"        }}")
            code.append(f"        private string BuildSqlSelect(string columns, string where, string? orderBy = null, long offset = 0, int length = -1) {{")
            code.append(f"            return \"SELECT \" + columns + \" FROM {table.name} \" + (where.Length > 0 ? \"WHERE \" + where : \"\") + (!string.IsNullOrEmpty(orderBy) ? \" ORDER BY \" + orderBy : \"\") + (offset!=0 && length!=-1 ? dbConnection.GetSqlSelectOffsetLimit(offset, length) : \"\");")
            code.append(f"        }}")
            code.append(f"        private string BuildSqlInsert() {{")
            code.append(f"            return \"INSERT INTO {table.name} ({get_columns_as_sql_insert(table)}) VALUES ({get_columns_as_sql_insert_placeholder(table)})\";")
            code.append(f"        }}")
            code.append(f"        private string BuildSqlUpdate() {{")
            code.append(f"            return \"UPDATE {table.name} SET {get_columns_as_sql_update(table)} WHERE {get_columns_as_sql_where_and(pk_columns)}\";")
            code.append(f"        }}")
            code.append(f"        private string BuildSqlDelete(string where) {{")
            code.append(f"            return \"DELETE FROM {table.name} \" + (where.Length > 0 ? \"WHERE \" + where : \"\");")
            code.append(f"        }}")
            code.append(f"    }}")
            code.append(f"")
        code.append(f"}}")
        # return
        return "\n".join(code)
    