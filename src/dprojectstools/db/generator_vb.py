import re
import locale
from datetime import datetime
from .db_schema import Schema, Column, Table, Index, DataType, Procedure
from .generator_xml import GeneratorXml
import fnmatch

def column_to_net_type(column: Column):
    result = ""
    if column.data_type == DataType.Char:
        result = "Char"
    if column.data_type == DataType.Varchar:
        result = "String"
    if column.data_type == DataType.Nchar:
        result = "Char"
    if column.data_type == DataType.Nvarchar:
        result = "String"
    if column.data_type == DataType.Binary:
        result = "Byte[]"
    if column.data_type == DataType.Varbinary:
        result = "byte[]"
    if column.data_type == DataType.Numeric:
        if column.scale == 0 and column.precision == 0:
            result = "Decimal"
        elif column.scale == 22 and column.precision == 7:
            result = "Decimal"
        elif column.scale == 0 and column.precision >= 1:
            result = "Decimal"
        elif column.scale == 2 and column.precision == 5:
            result = "Decimal"
        elif column.precision <= 7:
            result = "Single"
        elif column.precision <= 15:
            result = "Double"    
        else:
            result = "Decimal"
    if column.data_type == DataType.Decimal:
        result = "Decimal"
    if column.data_type == DataType.Smallint:
        result = "Int16"
    if column.data_type == DataType.Tinyint:
        result = "Byte"
    if column.data_type == DataType.Int:
        result = "Int32"
    if column.data_type == DataType.Bigint:
        result = "Int64"
    if column.data_type == DataType.Float:
        result = "Single"
    if column.data_type == DataType.Real:
        result = "Double"
    if column.data_type == DataType.Double:
        result = "Double"
    if column.data_type == DataType.Boolean:
        result = "Boolean"
    if column.data_type == DataType.Date:
        result = "DateTime"
    if column.data_type == DataType.DateTime:
        result = "DateTime"
    if column.data_type == DataType.Time:
        result = "TimeSpan"
    if column.data_type == DataType.Timestamp:
        result = "TimeSpan"
    if column.data_type == DataType.Interval:
        result = "String"
    if column.data_type == DataType.UniqueIdentifier:
        result = "Guid"
    if column.data_type == DataType.Json:
        result = "String"
    if column.null:
        result + "?"
    return result

def get_table_column(table: Table, column_name: str):
    for column in table.columns:
        if column.name.lower() == column_name.lower():
            return column
        
def get_pk_columns(table: Table):
    result = []
    if table.primary_key == None:
        raise ValueError(f"Table does not have pk: {table.name}")
    for column_name in table.primary_key.columns:
        result.append(get_table_column(table, column_name))
    return result

def get_table_columns_by(table: Table, column_names: list[str]):
    result = []
    for column_name in column_names:
        result.append(get_table_column(table, column_name))
    return result

#def get_columns_as_arguments(columns: list[Column]):
#    result = []
#    for column in columns:
#        result.append(column.name)
#    return ", ".join(result)

#def get_columns_as_arguments_array(columns: list[Column]):
#    result = []
#    for column in columns:
#        result.append(column.name)
#    return "[" + ", ".join(result) + "]"

#def get_columns_as_arguments_declaration(columns: list[Column]):
#    result = []
#    for column in columns:
#        result.append(column_to_net_type(column) + " " + column.name)
#    return ", ".join(result)

#def get_columns_as_arguments_curly(columns: list[Column]):
#    result = []
#    for column in columns:
#        result.append("{" + column.name + "}")
#    return ", ".join(result)

#def get_columns_as_id_array(columns: list[Column]):
#    result = []
#    for column in columns:
#        result.append("id." + column.name + "")
#    return "[" + ", ".join(result) + "]"

#def get_columns_as_set(columns: list[Column]):
#    result = []
#    for column in columns:
#        result.append(f"this.{column.name} = value.{column.name};")
#    return " ".join(result)

#def get_columns_as_to_string(columns: list[Column]):
#    result = []
#    for column in columns:
#        result.append(f"this.{column.name}.ToString()")
#    return " + ':' + ".join(result)


#def get_columns_as_sql_insert(table: Table):
#    result = []
#    for column in table.columns:
#        if not column.is_autoincrement:
#            result.append(f"{column.name}")
#    return ", ".join(result)

#def get_columns_as_sql_insert_placeholder(table: Table):
#    result = []
#    for column in table.columns:
#        if not column.is_autoincrement:
#            result.append(f"?")
#    return ", ".join(result)

#def get_columns_as_sql_insert_array(table: Table):
#    result = []
#    for column in table.columns:
#        if not column.is_autoincrement:
#            result.append(f"entity.{column.name}")
#    return "[" + ", ".join(result) + "]"

#def get_columns_as_sql_update(table: Table):
#    result = []
#    for column in table.columns:
#        if not column.name in table.primary_key.columns:
#            result.append(f"{column.name}=?")
#    return ", ".join(result)

#def get_columns_as_sql_update_array(table: Table):
#    result = []
#    for column in table.columns:
#        if not column.name in table.primary_key.columns:
#            result.append(f"entity.{column.name}")
#    for column_name in table.primary_key.columns:
#        result.append(f"entity.{column_name}")
#    return "[" + ", ".join(result) + "]"

#def get_columns_as_sql_delete_array(table: Table):
#    result = []
#    for column_name in table.primary_key.columns:
#        result.append(f"entity.{column_name}")
#    return "[" + ", ".join(result) + "]"

#def get_table_name_plural(table:Table):
#    return table.name + "s"

#def get_index_alias(table:Table, index:Index):
#    result = []
#    for column_name in index.columns:
#        result.append(to_camel_case(column_name))
#    return "".join(result)

#def to_camel_case(snake_case_string):
#    titleCaseVersion =  snake_case_string.title().replace("_", "")
#    camelCaseVersion = titleCaseVersion[0].upper() + titleCaseVersion[1:]
#    return camelCaseVersion

def case_insensitive_replace(text, old, new):
    return re.sub(re.escape(old), new, text, flags=re.IGNORECASE)

def to_property_name(column_name: str, column_case: str = ""):
    if column_name.lower().startswith("set_"):
        column_name = re.sub(re.escape("SET_"), "SET__", column_name, flags=re.IGNORECASE)    
    if column_case == "pascal":
        column_name = snake_to_camel(column_name)
    return column_name

def get_columns_as_method_parameters(table: Table, column_names: list[str], column_case: str = ""):
    result = ""
    index = 0
    for column_name in column_names:
        column = get_table_column(table, column_name)
        if column != None:
            column_net_type = column_to_net_type(column)                
            column_name = to_property_name(column.name, column_case)                    
            if index > 0:
                result += ", "
            result += column_name + " As " + column_net_type
            index += 1
    return result
def get_columns_as_method_parameters_array(table: Table, column_names: list[str]):
    result = ""
    index = 0
    for column_name in column_names:
        column = get_table_column(table, column_name)
        if column != None:
            column_net_type = column_to_net_type(column)                
            if index > 0:
                result += ", "
            result += snake_to_camel(column.name) + "Array As " + column_net_type + "()"
            index += 1
        pass
    return result
def get_columns_as_object_array_parameters(table: Table, column_names: list[str], column_case: str = ""):
    result = ""
    index = 0
    for column_name in column_names:
        column = get_table_column(table, column_name)
        if column != None:
            column_name = to_property_name(column.name, column_case).strip()                    
            if index > 0:
                result += ", "
            result += column_name
            index += 1
    return result.strip()
def get_columns_as_object_array_parameters_instance(table: Table, column_names: list[str], column_case: str):
    result = ""
    index = 0
    for column_name in column_names:
        column = get_table_column(table, column_name)
        if column != None:
            column_name = to_property_name(column.name, column_case)                    
            if index > 0:
                result += ", "
            result += "objInstance." + column_name
            index += 1
    return result

def snake_to_camel(value: str, avoid_consecutive_upper: bool = False) -> str:
    if avoid_consecutive_upper:
        return "".join(part.capitalize() for part in value.split("_") if part)
    else:
        parts = [part for part in value.split("_") if part]
        return "".join(part[:1].upper() + part[1:] for part in parts)

def get_columns_as_sql_where(table: Table, columns: list[str], include_table_name:bool = False):
    result = []
    for column_name in columns:
        column = get_table_column(table, column_name)
        if column != None:
            result.append(f"{table.name + "." if include_table_name else ""}{column.name} = ? ")
    return " AND ".join(result)

def get_columns_if_confition_nothing(table: Table, columns: list[str], require_space_when_null, column_case: str = ""):
    result = ""
    index = 0
    for column_name in columns:
        column = get_table_column(table, column_name)
        column_net_type = column_to_net_type(column)
        property_name = to_property_name(column.name, column_case)
        if index > 0:
            result += " Or "
        if column_net_type == "Int16" or column_net_type == "Int32" or column_net_type == "Int64":
            result += "objInstance." + property_name + " = 0"
        elif column_net_type == "Decimal":
            result += "objInstance." + property_name + " = 0"
        elif column_net_type == "Char" and require_space_when_null and not column.null:
            result += "objInstance." + property_name + " = \" \"c"
        elif column_net_type == "DateTime":
            result += "objInstance." + property_name + " = CDate(Nothing)"
        else:
            result += "objInstance." + property_name + " Is Nothing"
        index += 1
    return result

def get_procedure_arguments(procedure: Procedure):
    result = ""
    index = 0
    for argument in procedure.arguments:
        if index > 0:
            result += ","
        argument_net_type = column_to_net_type(argument)        
        if argument.direction == "IN":
            result += f"ByVal "
        else:
            result += f"ByRef "
        if argument_net_type == "String":
            result += f"{argument.name} As String"
        else:
            result += f"{argument.name} As Nullable(Of {argument_net_type})"
        index += 1
    return result

class GeneratorVbV1():

    # ctor
    def __init__(self, schema, settings):
        self._schema = schema
        self._settings = settings

    # static methods
    def create(schema: Schema, settings: dict):
        return GeneratorVbV1(schema, settings)    
    
    # methods
    def generate(self):
        name = self._settings.get("name", "") or "DBContext"
        clss = self._settings.get("clss", "") or "DBContext"
        tables = self._settings.get("tables") or []
        if isinstance(tables, str):
            tables = [tables]
        views = self._settings.get("views") or []
        if isinstance(views, str):
            views = [views]
        procedures = self._settings.get("procedures") or []
        if isinstance(procedures, str):
            procedures = [procedures]
        connection = self._settings.get("connection", "")
        namespace = self._settings.get("namespace", "MyNamespace")
        columns_case = self._settings.get("columns_case", "")
        xml = GeneratorXml.create(self._schema).generate()
        require_space_when_null = ("GIET" in connection)
        code = []
        code.append(f"Imports System")
        code.append(f"Imports System.Text")
        code.append(f"Imports System.Collections")
        code.append(f"Imports System.Data")
        code.append(f"Imports System.Collections.Generic")
        code.append(f"Imports System.ComponentModel")
        code.append(f"Imports DProjects.Cache")
        code.append(f"Imports System.Linq")
        code.append(f"Imports Microsoft.Extensions.Caching.Memory")
        code.append(f"Imports Microsoft.Extensions.Configuration")
        code.append(f"")
        # namespace
        code.append(f"Namespace {namespace}")
        code.append(f"")
        # class
        code.append(f"    Public Class {clss}")
        code.append(f"        Inherits Base")
        code.append(f"")
        code.append(f"        'constructor")
        code.append(f"        Public Sub New(objContext As Context)")
        code.append(f"            MyBase.New(objContext)")
        code.append(f"        End Sub")
        code.append(f"")
        code.append(f"#Region \"VO + DAL Autogenerated\"")
        # VOs
        locale.setlocale(locale.LC_COLLATE, 'en_US.UTF-8')
        code.append(f"        'ValueObjects")
        for table in sorted(self._schema.tables, key=lambda table: locale.strxfrm(table.name.upper())):
            table_valid = False
            for pattern in tables:
                if fnmatch.fnmatch(table.name.lower(), pattern.lower()):
                    table_valid = True
                    break
            if not table_valid:
                continue
            code.append(f"        Public Class {table.name}VO")
            code.append(f"            Inherits DProjects.Cett.Classes.ValueObject")
            for column in table.columns:
                column_net_type = column_to_net_type(column)                
                column_name = to_property_name(column.name, columns_case)
                property_name = column_name
                if property_name == "ALIAS":
                    property_name = "[ALIAS]"
                code.append(f"            Public Property {property_name} As {column_net_type}{f" 'size={column.size}" if column.size > 0 else ""}")
                code.append(f"                Get")
                code.append(f"                    Return MyBase.Attributes.GetAs(Of {column_net_type})(\"{column_name}\")")
                code.append(f"                End Get")
                code.append(f"                Set(value As {column_net_type})")
                code.append(f"                    MyBase.Attributes(\"{column_name}\") = value")
                code.append(f"                End Set")
                code.append(f"            End Property")
            code.append(f"            Public Sub New()")
            code.append(f"                MyBase.New()")
            code.append(f"                Me.MimeType = \"{table.name}\"")
            for column in table.columns:
                defaultValue = ""
                column_net_type = column_to_net_type(column)                
                column_name = to_property_name(column.name, columns_case)
                if column.default == None:
                    if column.null:
                        defaultValue = "Nothing"
                        if column_net_type == "Int64" or column_net_type == "Int32" or column_net_type == "Int16" or column_net_type == "Int8":
                            defaultValue = "0"
                        elif column_net_type == "Single" or column_net_type == "Double" or column_net_type == "Decimal":
                            #defaultValue = "0.0"
                            pass
                        elif column_net_type == "Date" or column_net_type == "DateTime":
                            defaultValue = "CDate(Nothing)"
                        else:
                            defaultValue = "Nothing"
                    else:
                        if column_net_type == "Int64" or column_net_type == "Int32" or column_net_type == "Int16" or column_net_type == "Int8":
                            defaultValue = "0"
                        elif column_net_type == "Decimal":
                            defaultValue = "CDec(0.0)"
                        elif column_net_type == "Single" or column_net_type == "Double":
                            defaultValue = "0.0"
                        elif column_net_type == "String":
                            defaultValue = "\"\""
                        elif column_net_type == "DateTime":
                            defaultValue = "CDate(Date.Now)"
                        elif column_net_type == "Char":
                            defaultValue = "\" \"c"
                        elif column_net_type == "Boolean":
                            defaultValue = "False"
                        else:
                            defaultValue = "Nothing"
                else:
                    defaultValue = column.default
                    if column_net_type == "Boolean":
                        if column.default == "0":
                            defaultValue = "False"
                        elif column.default == "1":
                            defaultValue = "False"
                        elif column.default:
                            defaultValue = f"CBool({column.default})"
                        else:
                            defaultValue = "False"
                    elif column.default == "now":
                        defaultValue = "Date.Now"
                    elif column.default.startswith("'"):
                        defaultValue = column.default.strip().replace("'","\"")
                        if column.size == 1:
                            if defaultValue == "\"\"":
                                defaultValue = "\" \""
                            defaultValue += "c"

                code.append(f"                Me.{column_name} = {defaultValue}")
            code.append(f"            End Sub")
            code.append(f"            Public Sub New(objDataRow As DataRow)")
            code.append(f"                MyBase.New()")
            code.append(f"                Me.MimeType = \"{table.name}\"")
            for column_name in table.primary_key.columns:
                code.append(f"                Me.Path = \"/{table.name}\" & CStr(objDataRow(\"{column_name}\"))")
            for column in table.columns:
                column_net_type = column_to_net_type(column)                
                column_name = to_property_name(column.name, columns_case)
                if column.null:
                    code.append(f"                If objDataRow.IsNull(\"{column.name}\") Then")
                    code.append(f"                    Me.{column_name} = Nothing")
                    code.append(f"                Else")
                    code.append(f"                    Me.{column_name} = Convert.To{column_net_type}(objDataRow(\"{column.name}\"))")
                    code.append(f"                End If")
                else:
                    code.append(f"                Me.{column_name} = Convert.To{column_net_type}(objDataRow(\"{column.name}\"))")
            code.append(f"            End Sub")
            code.append(f"            Public Sub New(objValueObject As DProjects.Cett.Classes.ValueObject)")
            code.append(f"                MyBase.New(objValueObject)")
            code.append(f"            End Sub")
            code.append(f"            Public Overloads Function IsEqual(objInstance As {table.name}VO) As Boolean")
            code.append(f"                Dim strDifferences As String = \"\"")
            code.append(f"                Return IsEqual(objInstance, strDifferences)")
            code.append(f"            End Function")
            code.append(f"            Public Overloads Function IsEqual(objInstance As {table.name}VO, ByRef differences As String) As Boolean")
            code.append(f"                Dim differencesSB As New StringBuilder")
            code.append(f"                Dim result As Boolean = True")
            code.append(f"                If objInstance Is Nothing Then Return False")
            for column in table.columns:
                column_net_type = column_to_net_type(column)
                column_name = to_property_name(column.name, columns_case)
                if column_net_type == "String":
                    code.append(f"                If Not (\"\" & Me.{column_name}).Equals(objInstance.{column_name}, StringComparison.Ordinal) Then")
                else:
                    code.append(f"                If Me.{column_name} <> objInstance.{column_name} Then")
                code.append(f"                    If differencesSB.Length <> 0 Then differencesSB.Append(\",\")")
                code.append(f"                    differencesSB.Append(\"{to_property_name(column.name, columns_case)}\")")
                code.append(f"                    result = False")
                code.append(f"                End If")
            code.append(f"                differences = differencesSB.ToString()")
            code.append(f"                Return result")
            code.append(f"            End Function")
            code.append(f"        End Class")

        # Methods
        for table in sorted(self._schema.tables, key=lambda table: locale.strxfrm(table.name.upper())):
            table_valid = False
            for pattern in tables:
                if fnmatch.fnmatch(table.name.lower(), pattern.lower()):
                    table_valid = True
                    break
            if not table_valid:
                continue
            code.append(f"        '{table.name}")
            code.append(f"        <Description(\"Selects rows of data by filter from table '{table.name}'\")>")
            # SelectAll
            code.append(f"        Public Function {table.name}_SelectAll(orderby As String, Optional startIndex As Integer = 0, Optional length As Integer = -1) As {table.name}VO()")
            code.append(f"            Return {table.name}_SelectByFilter(\"\", New Object() {{}}, orderby, startIndex, length)")
            code.append(f"        End Function")
            # SelectCount
            code.append(f"        Public Function {table.name}_SelectCount(filter As String, filterValues As Object()) As Integer")
            code.append(f"            Return {table.name}_SelectByFilter(filter, filterValues, \"\").Length")
            code.append(f"        End Function")
            # SelectSingleByVO
            code.append(f"        Public Function {table.name}_SelectSingleByVO(objInstance As {table.name}VO) As {table.name}VO")
            code.append(f"            Dim filter As New StringBuilder")
            code.append(f"            Dim filterValues As New ArrayList")
            column_index = 0
            for column_name in table.primary_key.columns:
                code.append(f"            filter.Append(\"{" AND " if column_index > 0 else ""} {column_name} = ? \")")
                code.append(f"            filterValues.Add(objInstance.{to_property_name(column_name, columns_case)})")
                column_index += 1
            code.append(f"            Dim result As {table.name}VO() = {table.name}_SelectByFilter(filter.ToString(), filterValues.ToArray(), \"\")")
            code.append(f"            If result.Length = 0 Then Return Nothing")
            code.append(f"            Return result(0)")
            code.append(f"        End Function")
            # SelectSingleByFilter
            code.append(f"        Public Function {table.name}_SelectSingleByFilter(filter As String, filterValues As Object()) As {table.name}VO")
            code.append(f"            Dim result As {table.name}VO() = {table.name}_SelectByFilter(filter, filterValues, \"\")")
            code.append(f"            If result.Length = 0 Then Return Nothing")
            code.append(f"            Return result(0)")
            code.append(f"        End Function")
            # SelectScalarBy
            code.append(f"        Public Function {table.name}_SelectScalarBy(column As String, filter As String, filterValues As Object()) As Object")
            code.append(f"            Dim objSqlBuilder As New StringBuilder")
            code.append(f"            objSqlBuilder.Append(\"SELECT \" & column & \" FROM {table.name} WHERE \" & filter)")
            code.append(f"            Return mContext.DBConnections({connection}).ExecuteScalar(objSqlBuilder.ToString(), filterValues)")
            code.append(f"        End Function")
            # SelectByFilter
            code.append(f"        Public Function {table.name}_SelectByFilter(filter As String, filterValues As Object(), orderby As String, Optional startIndex As Integer = 0, Optional length As Integer = -1) As {table.name}VO()")
            code.append(f"            Dim objSqlBuilder As StringBuilder")
            code.append(f"            Dim objResult As New List(Of {table.name}VO)")
            code.append(f"            objSqlBuilder = New StringBuilder()")
            code.append(f"            objSqlBuilder.Append(\"SELECT {table.name}.*\")")
            code.append(f"            objSqlBuilder.Append(\" FROM {table.name} \")")
            code.append(f"            If filter <> \"\" Then")
            code.append(f"                objSqlBuilder.Append(\" WHERE \")")
            code.append(f"                objSqlBuilder.Append(filter)")
            code.append(f"            End If")
            code.append(f"            If orderby <> \"\" Then")
            code.append(f"                objSqlBuilder.Append(\" ORDER BY \")")
            code.append(f"                Dim iOrderByParts As Integer = 0")
            code.append(f"                For Each orderByPart As String In orderBy.Split(\",\"c)")
            code.append(f"                    orderByPart = orderByPart.Trim()")
            code.append(f"                    If iOrderByParts > 0 Then objSqlBuilder.Append(\",\")")
            code.append(f"                    If orderByPart.indexOf(\".\") = -1 Then")
            code.append(f"                        objSqlBuilder.Append(\"{table.name}.\" & orderByPart)")
            code.append(f"                    Else")
            code.append(f"                        objSqlBuilder.Append(orderbyPart)")
            code.append(f"                    End If")
            code.append(f"                    iOrderByParts += 1")
            code.append(f"                Next")
            code.append(f"            End If")
            code.append(f"            Dim counter As Integer = 0")
            code.append(f"            For Each objDataRow As DataRow In mContext.DBConnections({connection}).ExecuteDataTable(objSqlBuilder.ToString(), filterValues).Rows")
            code.append(f"                Dim includeRecord As Boolean = startIndex <= counter And (length = -1 Or (length <> -1 And counter < startIndex + length))")
            code.append(f"                If includeRecord Then")
            code.append(f"                    objResult.Add(New {table.name}VO(objDataRow))")
            code.append(f"                End If")
            code.append(f"                counter += 1")
            code.append(f"            Next")
            code.append(f"            Return objResult.ToArray()")
            code.append(f"        End Function")
            # SelectByFilterAsDataTable
            code.append(f"        Public Function {table.name}_SelectByFilterAsDataTable(columns As String, filter As String, filterValues As Object(), orderby As String, Optional startIndex As Integer = 0, Optional length As Integer = -1) As Datatable")
            code.append(f"            Dim objSqlBuilder As StringBuilder")
            code.append(f"            objSqlBuilder = New StringBuilder()")
            code.append(f"            objSqlBuilder.Append(\"SELECT \")")
            code.append(f"            If columns = \"\" Then")
            code.append(f"                objSqlBuilder.Append(\"{table.name}.*\")")
            code.append(f"            Else")
            code.append(f"                objSqlBuilder.Append(columns)")
            code.append(f"            End If")
            code.append(f"            objSqlBuilder.Append(\" FROM {table.name} \")")
            code.append(f"            If filter <> \"\" Then")
            code.append(f"                objSqlBuilder.Append(\" WHERE \")")
            code.append(f"                objSqlBuilder.Append(filter)")
            code.append(f"            End If")
            code.append(f"            If orderby <> \"\" Then")
            code.append(f"                objSqlBuilder.Append(\" ORDER BY \")")
            code.append(f"                Dim iOrderByParts As Integer = 0")
            code.append(f"                For Each orderByPart As String In orderBy.Split(\",\"c)")
            code.append(f"                    orderByPart = orderByPart.Trim()")
            code.append(f"                    If iOrderByParts > 0 Then objSqlBuilder.Append(\",\")")
            code.append(f"                    If orderByPart.indexOf(\".\") = -1 Then")
            code.append(f"                        objSqlBuilder.Append(\"{table.name}.\" & orderByPart)")
            code.append(f"                    Else")
            code.append(f"                        objSqlBuilder.Append(orderbyPart)")
            code.append(f"                    End If")
            code.append(f"                    iOrderByParts += 1")
            code.append(f"                Next")
            code.append(f"            End If")
            code.append(f"            Return mContext.DBConnections({connection}).ExecuteDataTablePaginated(objSqlBuilder.ToString(), startIndex, length, filterValues)")
            code.append(f"        End Function")
            # SelectIDsByFilter
            if len(table.primary_key.columns) == 1:
                column = get_table_column(table, table.primary_key.columns[0])
                column_net_type = column_to_net_type(column)
                code.append(f"        <Description(\"Selects ids by filter from table '{table.name}'\")>")
                code.append(f"        Public Function {table.name}_SelectIDsByFilter(filter As String, filterValues As Object(), orderby As String, Optional startIndex As Integer = 0, Optional length As Integer = -1) As {column_net_type}()")
                code.append(f"            Dim objSqlBuilder As StringBuilder")
                code.append(f"            Dim objResult As New List(Of {column_net_type})")
                code.append(f"            objSqlBuilder = New StringBuilder()")
                for column_name in table.primary_key.columns:
                    code.append(f"            objSqlBuilder.Append(\"SELECT {column_name}\")")
                code.append(f"            objSqlBuilder.Append(\" FROM {table.name} \")")
                code.append(f"            If filter <> \"\" Then")
                code.append(f"                objSqlBuilder.Append(\" WHERE \")")
                code.append(f"                objSqlBuilder.Append(filter)")
                code.append(f"            End If")
                code.append(f"            If orderby <> \"\" Then")
                code.append(f"                objSqlBuilder.Append(\" ORDER BY \")")
                code.append(f"                objSqlBuilder.Append(orderby)")
                code.append(f"            End If")
                code.append(f"            Dim counter As Integer = 0")
                code.append(f"            Dim objDataTable As DataTable = mContext.DBConnections({connection}).ExecuteDataTable(objSqlBuilder.ToString(), filterValues)")
                code.append(f"            For Each objDataRow As DataRow In objDataTable.Rows")
                code.append(f"                Dim includeRecord As Boolean = startIndex <= counter And (length = -1 Or (length <> -1 And counter < startIndex + length))")
                code.append(f"                If includeRecord Then")
                code.append(f"                    objResult.Add(Convert.To{column_net_type}(objDataRow(0)))")
                code.append(f"                End If")
                code.append(f"                counter += 1")
                code.append(f"            Next")
                code.append(f"            Return objResult.ToArray()")
                code.append(f"        End Function")            
            # SelectByPK
            code.append(f"        <Description(\"Selects record by primary key from table '{table.name}'\")>")
            code.append(f"        Public Overloads Function {table.name}_SelectByPK({get_columns_as_method_parameters(table, table.primary_key.columns)}) As {table.name}VO")
            code.append(f"            Dim filterExpression As String = \"{get_columns_as_sql_where(table, table.primary_key.columns)}\"")
            code.append(f"            Dim filterValues As Object() = New Object() {{{get_columns_as_object_array_parameters(table, table.primary_key.columns)}}}")
            code.append(f"            Dim result As {table.name}VO() = {table.name}_SelectByFilter(filterExpression, filterValues, \"\")")
            code.append(f"            If result.Length > 0 Then")
            code.append(f"                Return result(0)")
            code.append(f"            Else")
            code.append(f"                Return Nothing")
            code.append(f"            End If")
            code.append(f"        End Function")
            # SelectByPKs
            if len(table.primary_key.columns) == 1:
                column = get_table_column(table, table.primary_key.columns[0])
                column_net_type = column_to_net_type(column)
                code.append(f"        <Description(\"Selects records by primary keys from table '{table.name}'\")>")
                code.append(f"        Public Overloads Function {table.name}_SelectByPKs(ids As {column_net_type}(), Optional orderby As String = \"\") As {table.name}VO()")
                code.append(f"            Dim filterExpression As StringBuilder = New StringBuilder()")
                code.append(f"            Dim counter As Int32 = 0")
                for column_name in table.primary_key.columns:
                    code.append(f"            filterExpression.Append(\"{column_name} IN (\")")
                    code.append(f"            For Each id As {column_net_type} In ids")
                    code.append(f"                If counter > 0 Then filterExpression.Append(\",\")")
                    code.append(f"                filterExpression.Append(mContext.DBConnections({connection}).GetSqlEncodedValue(id, GetType({column_net_type}), False))")
                    code.append(f"                counter += 1")
                    code.append(f"            Next")
                    code.append(f"            If counter = 0 Then filterExpression.Append(\"-1\")")
                    code.append(f"            filterExpression.Append(\")\")")
                code.append(f"            Return {table.name}_SelectByFilter(filterExpression.ToString(), New Object() {{}}, orderby)")
                code.append(f"        End Function")
            # SelectBy by FK
            for fk in sorted(table.foreign_keys, key=lambda fk: locale.strxfrm(fk.name.upper())):
                fkname = snake_to_camel(fk.name, True).replace("$","")
                code.append(f"        <Description(\"Selects rows by foreign key '{fkname}' from table '{table.name}'\")>")
                code.append(f"        Public Overloads Function {table.name}_SelectBy{fkname}({get_columns_as_method_parameters(table, fk.columns, columns_case)}, Optional orderby As String = \"\", Optional startIndex As Integer = 0, Optional length As Integer = -1) As {table.name}VO()")
                code.append(f"            Dim filterExpression As String = \"{get_columns_as_sql_where(table, fk.columns)}\"")
                code.append(f"            Dim filterValues As Object() = New Object() {{{get_columns_as_object_array_parameters(table, fk.columns, columns_case)}}}")
                code.append(f"            Return {table.name}_SelectByFilter(filterExpression, filterValues, orderby, startIndex, length)")
                code.append(f"        End Function")
            # SelectBy by FK
            for fk in sorted(table.foreign_keys, key=lambda fk: locale.strxfrm(fk.name.upper())):
                fkname = snake_to_camel(fk.name, True).replace("$","")
                target_column_name = ""
                target_column_net_type = ""
                for column_name in fk.columns:
                    column = get_table_column(table, column_name)
                    target_column_name = column.name
                    target_column_net_type = column_to_net_type(column)
                code.append(f"        <Description(\"Selects rows by foreign key '{fkname}' from table '{table.name}'\")>")
                code.append(f"        Public Overloads Function {table.name}_SelectBy{fkname}({snake_to_camel(target_column_name, True)}Array As {target_column_net_type}(), Optional orderby As String = \"\", Optional startIndex As Integer = 0, Optional length As Integer = -1) As {table.name}VO()")
                code.append(f"            Dim filterExpression As StringBuilder = New StringBuilder()")
                code.append(f"            Dim counter As Int32 = 0")
                code.append(f"            filterExpression.Append(\"{target_column_name} IN (\")")
                code.append(f"            For Each id As {target_column_net_type} In {snake_to_camel(target_column_name, True)}Array")
                code.append(f"                If counter > 0 Then filterExpression.Append(\",\")")
                code.append(f"                filterExpression.Append(mContext.DBConnections({connection}).GetSqlEncodedValue(id, GetType({target_column_net_type}), False))")
                code.append(f"                counter += 1")
                code.append(f"            Next")
                code.append(f"            If counter = 0 Then filterExpression.Append(\"-1\")")
                code.append(f"            filterExpression.Append(\")\")")
                code.append(f"            Return {table.name}_SelectByFilter(filterExpression.ToString(), New Object() {{}}, orderby, startIndex, length)")
                code.append(f"        End Function")

            # SelectBy by INDEX
            for index in table.indexes:
                idxname = snake_to_camel(index.name, True).replace("$","")
                if index.unique:                    
                    code.append(f"        <Description(\"Selects row by index '{idxname}' from table '{table.name}'\")>")
                    code.append(f"        Public Function {table.name}_SelectByIndex{idxname}({get_columns_as_method_parameters(table, index.columns, columns_case)}) As {table.name}VO")
                    code.append(f"            Dim filterExpression As String = \"{get_columns_as_sql_where(table, index.columns, True)}\"")
                    code.append(f"            Dim filterValues As Object() = New Object() {{{get_columns_as_object_array_parameters(table, index.columns, columns_case)}}}")
                    code.append(f"            Dim result As {table.name}VO() = {table.name}_SelectByFilter(filterExpression, filterValues, \"\")")
                    code.append(f"            If result.Length > 0 Then")
                    code.append(f"                Return result(0)")
                    code.append(f"            Else")
                    code.append(f"                Return Nothing")
                    code.append(f"            End If")
                    code.append(f"        End Function")
                    if len(index.columns) == 1:
                        #target_column_name = ""
                        #target_column_net_type = ""
                        #for column_name in fk.columns:
                        #    column = get_table_column(table, column_name)
                        #    target_column_name = column.name
                        #    target_column_net_type = column_to_net_type(column)
                        code.append(f"        <Description(\"Selects row id by index '{idxname}' from table '{table.name}'\")>")
                        code.append(f"        Public Function {table.name}_SelectIdByIndex{idxname}({get_columns_as_method_parameters(table, index.columns, columns_case)}, Optional orderby As String = \"\", Optional startIndex As Integer = 0, Optional length As Integer = -1) As Int32")
                        code.append(f"            Dim filterExpression As String = \"{get_columns_as_sql_where(table, index.columns, True)}\"")
                        code.append(f"            Dim filterValues As Object() = New Object() {{{get_columns_as_object_array_parameters(table, index.columns, columns_case)}}}")
                        code.append(f"            Dim result As Int32() = {table.name}_SelectIDsByFilter(filterExpression, filterValues, \"\")")
                        code.append(f"            If result.Length > 0 Then")
                        code.append(f"                Return result(0)")
                        code.append(f"            Else")
                        code.append(f"                Return Nothing")
                        code.append(f"            End If")
                        code.append(f"        End Function")
                else:
                    code.append(f"        <Description(\"Selects rows by index '{idxname}' from table '{table.name}'\")>")
                    code.append(f"        Public Function {table.name}_SelectByIndex{idxname}({get_columns_as_method_parameters(table, index.columns, columns_case)}, Optional orderby As String = \"\", Optional startIndex As Integer = 0, Optional length As Integer = -1) As {table.name}VO()")
                    code.append(f"            Dim filterExpression As String = \"{get_columns_as_sql_where(table, index.columns, True)}\"")
                    code.append(f"            Dim filterValues As Object() = New Object() {{{get_columns_as_object_array_parameters(table, index.columns, columns_case)}}}")
                    code.append(f"            Return {table.name}_SelectByFilter(filterExpression, filterValues, orderby, startIndex, length)")
                    code.append(f"        End Function")
            # SelectBy by Index Pk
            pkidxname = snake_to_camel(table.primary_key.name, True).replace("$","")
            code.append(f"        <Description(\"Selects row by index '{pkidxname}' from table '{table.name}'\")>")
            code.append(f"        Public Function {table.name}_SelectByIndex{pkidxname}({get_columns_as_method_parameters(table, table.primary_key.columns, columns_case)}) As {table.name}VO")
            code.append(f"            Dim filterExpression As String = \"{get_columns_as_sql_where(table, table.primary_key.columns, True)}\"")
            code.append(f"            Dim filterValues As Object() = New Object() {{{get_columns_as_object_array_parameters(table, table.primary_key.columns, columns_case)}}}")
            code.append(f"            Dim result As {table.name}VO() = {table.name}_SelectByFilter(filterExpression, filterValues, \"\")")
            code.append(f"            If result.Length > 0 Then")
            code.append(f"                Return result(0)")
            code.append(f"            Else")
            code.append(f"                Return Nothing")
            code.append(f"            End If")
            code.append(f"        End Function")
            if len(table.primary_key.columns) == 1:
                column = get_table_column(table, table.primary_key.columns[0])
                column_net_type = column_to_net_type(column)
                code.append(f"        <Description(\"Selects row id by index '{pkidxname}' from table '{table.name}'\")>")
                code.append(f"        Public Function {table.name}_SelectIdByIndex{pkidxname}({get_columns_as_method_parameters(table, table.primary_key.columns, columns_case)}, Optional orderby As String = \"\", Optional startIndex As Integer = 0, Optional length As Integer = -1) As {column_net_type}")
                code.append(f"            Dim filterExpression As String = \"{get_columns_as_sql_where(table, table.primary_key.columns, True)}\"")
                code.append(f"            Dim filterValues As Object() = New Object() {{{get_columns_as_object_array_parameters(table, table.primary_key.columns, columns_case)}}}")
                code.append(f"            Dim result As {column_net_type}() = {table.name}_SelectIDsByFilter(filterExpression, filterValues, \"\")")
                code.append(f"            If result.Length > 0 Then")
                code.append(f"                Return result(0)")
                code.append(f"            Else")
                code.append(f"                Return Nothing")
                code.append(f"            End If")
                code.append(f"        End Function")
            # insert
            code.append(f"        ' Insert row")
            code.append(f"        <Description(\"Insert record to table '{table.name}'\")>")           
            code.append(f"        Public Sub {table.name}_Insert(objInstance As {table.name}VO)")
            code.append(f"            Dim objSqlBuilder As StringBuilder")
            for column in table.columns:
                column_net_type = column_to_net_type(column)
                property_name = to_property_name(column.name, columns_case)
                if column_net_type == "String" and column.size > 0:
                    code.append(f"            If Not objInstance.{property_name} Is Nothing AndAlso objInstance.{property_name}.length > {column.size} Then objInstance.{property_name} = objInstance.{property_name}.SubString(0, {column.size})")
            code.append(f"            Dim objSqlArguments As New List(Of Object)")
            code.append(f"            objSqlBuilder = New StringBuilder()")
            code.append(f"            objSqlBuilder.Append(\"INSERT \")")
            code.append(f"            objSqlBuilder.Append(\"INTO {table.name} (\")")
            index = 0
            for column in table.columns:
                if column.is_autoincrement:
                    pass
                else:
                    code.append(f"            objSqlBuilder.Append(\"{", " if index > 0 else ""}{column.name}\")")
                    index += 1
            code.append(f"            objSqlBuilder.Append(\") VALUES (\")")
            index = 0
            for column in table.columns:
                if column.is_autoincrement:
                    pass
                else:
                    code.append(f"            objSqlBuilder.Append(\"{", " if index > 0 else ""}?\")")
                    index += 1
            code.append(f"            objSqlBuilder.Append(\")\")")
            index = 0
            for column in table.columns:
                if column.is_autoincrement:
                    pass
                else:
                    column_net_type = column_to_net_type(column)
                    property_name = to_property_name(column.name, columns_case)
                    if (column_net_type == "Int16" or column_net_type == "Int32" or column_net_type == "Int64") and column.null:
                        code.append(f"            If objInstance.{property_name} = 0 Then")
                        code.append(f"                objSqlArguments.Add(Nothing)")
                        code.append(f"            Else")
                        code.append(f"                objSqlArguments.Add(objInstance.{property_name})")
                        code.append(f"            End If")
                    else:
                        code.append(f"            objSqlArguments.Add(objInstance.{property_name})")
                    index += 1
            code.append(f"            mContext.DBConnections({connection}).ExecuteNonQuery(objSqlBuilder.ToString(), objSqlArguments.ToArray())")
            for column in table.columns:
                if column.is_autoincrement:
                    column_net_type = column_to_net_type(column)
                    property_name = to_property_name(column.name, columns_case)
                    code.append(f"            objInstance.{property_name} = CType(mContext.DBConnections({connection}).ExecuteScalar(mContext.DBConnections({connection}).GetSqlSelectAutoincrementStatement()), {column_net_type.replace("Int32","Integer")})")
                    break

            code.append(f"        End Sub")
            # UpdateOrInsertOrDelete by FK
            for fk in sorted(table.foreign_keys, key=lambda fk: locale.strxfrm(fk.name.upper())):
                fkname = snake_to_camel(fk.name, True).replace("$","")
                code.append(f"        <Description(\"Update Insert or Deletes rows by foreign key '{fkname}' from table '{table.name}'\")>")
                code.append(f"        Public Overloads Function {table.name}_UpdateOrInsertOrDeleteBy{fkname}({get_columns_as_method_parameters(table, fk.columns, columns_case)}, objInstances As List(Of {table.name}VO)) As Integer")
                code.append(f"            Dim recordsAffected As Integer = 0")
                code.append(f"            For Each objInstance As {table.name}VO In objInstances")
                code.append(f"                Dim instanceIsNew As Boolean = False")
                for column_name in table.primary_key.columns:
                    column = get_table_column(table, column_name)
                    column_net_type = column_to_net_type(column)
                    property_name = to_property_name(column.name, columns_case)
                    if column_net_type == "String":
                        code.append(f"                If objInstance.{property_name} Is Nothing Then instanceIsNew = True")
                    elif column_net_type == "Char":
                        code.append(f"                If objInstance.{property_name} = CChar(Nothing) Then instanceIsNew = True")
                    elif column_net_type == "DateTime":
                        code.append(f"                If objInstance.{property_name} = CDate(Nothing) Then instanceIsNew = True")
                    else:
                        code.append(f"                If objInstance.{property_name} = 0 Then instanceIsNew = True")
                code.append(f"")
                for column_name in fk.columns:
                    column = get_table_column(table, column_name)
                    column_net_type = column_to_net_type(column)
                    property_name = to_property_name(column.name, columns_case)
                    if column_net_type == "String":
                        code.append(f"                If objInstance.{property_name} Is Nothing Then instanceIsNew = True")
                    elif column_net_type == "Char":
                        code.append(f"                If objInstance.{property_name} = CChar(Nothing) Then instanceIsNew = True")
                    elif column_net_type == "DateTime":
                        code.append(f"                If objInstance.{property_name} = CDate(Nothing) Then instanceIsNew = True")
                    else:
                        code.append(f"                If objInstance.{property_name} = 0 Then instanceIsNew = True")
                code.append(f"                If instanceIsNew Then")
                for column_name in fk.columns:
                    column = get_table_column(table, column_name)
                    property_name = to_property_name(column.name, columns_case)
                    code.append(f"                    objInstance.{property_name} = {property_name}")
                code.append(f"                    {table.name}_Insert(objInstance)")
                code.append(f"                    recordsAffected += 1")
                code.append(f"                Else")
                for column_name in fk.columns:
                    column = get_table_column(table, column_name)
                    property_name = to_property_name(column.name, columns_case)
                    code.append(f"                    objInstance.{property_name} = {property_name}")
                code.append(f"                    Dim differences As String = {table.name}_GetDifferencesWithDB(objInstance)")
                code.append(f"                    If differences <> \"EXIST:\" Then")
                code.append(f"                        {table.name}_Update(objInstance)")
                code.append(f"                        recordsAffected += 1")
                code.append(f"                    End If")
                code.append(f"                End If")
                code.append(f"            Next")
                code.append(f"            For Each objOriginalInstance As {table.name}VO In {table.name}_SelectBy{fkname}({get_columns_as_object_array_parameters(table, fk.columns, columns_case)})")
                code.append(f"                Dim existsOriginalInstanceInList As Boolean = False")
                code.append(f"                For Each objInstance As {table.name}VO In objInstances")
                for column_name in table.primary_key.columns:
                    column = get_table_column(table, column_name)
                    property_name = to_property_name(column.name, columns_case)
                    code.append(f"                    If objOriginalInstance.{property_name} = objInstance.{property_name} Then existsOriginalInstanceInList = True")
                code.append(f"                Next")
                code.append(f"                If Not existsOriginalInstanceInList Then 'objInstances.IndexOf(objOriginalInstance)=-1 Then")
                code.append(f"                    {table.name}_Delete(objOriginalInstance)")
                code.append(f"                    recordsAffected += 1")
                code.append(f"                End If")
                code.append(f"            Next")
                code.append(f"            Return recordsAffected")
                code.append(f"        End Function")
                code.append(f"        Public Overloads Function {table.name}_UpdateOrInsertOrDeleteBy{fkname}({get_columns_as_method_parameters(table, fk.columns, columns_case)}, objInstances As System.Array) As Integer")
                code.append(f"            Dim result As Integer")
                code.append(f"            Dim list As New List(Of {table.name}VO)")
                code.append(f"            For Each objInstance As Object In objInstances")
                code.append(f"                If TypeOf objInstance Is {table.name}VO Then")
                code.append(f"                    list.Add(CType(objInstance, {table.name}VO))")
                code.append(f"                ElseIf TypeOf objInstance Is DProjects.Cett.Classes.ValueObject Then")
                code.append(f"                    list.Add(New {table.name}VO(CType(objInstance, DProjects.Cett.Classes.ValueObject)))")
                code.append(f"                End If")
                code.append(f"            Next")
                code.append(f"            result = {table.name}_UpdateOrInsertOrDeleteBy{fkname}({get_columns_as_object_array_parameters(table, fk.columns, columns_case)} , list)")
                code.append(f"            Dim counter As Integer = 0")
                code.append(f"            For Each objInstance As Object In objInstances")
                code.append(f"                If TypeOf objInstance Is DProjects.Cett.Classes.ValueObject Then")
                for column_name in table.primary_key.columns:
                    column = get_table_column(table, column_name)
                    property_name = to_property_name(column.name, columns_case)
                    code.append(f"                    CType(objInstance, DProjects.Cett.Classes.ValueObject)(\"{property_name}\") = list(counter).{property_name}")
                code.append(f"                End If")
                code.append(f"                counter += 1")
                code.append(f"            Next")
                code.append(f"            Return result")
                code.append(f"        End Function")
            # delete
            code.append(f"        ' Deletes rows by filter ")
            code.append(f"        <Description(\"Deletes records by filter from table '{table.name}'\")>")
            code.append(f"        Public Function {table.name}_DeleteByFilter(filter As String, filterValues As Object()) As Integer")
            code.append(f"            Dim objSqlBuilder As StringBuilder")
            code.append(f"            objSqlBuilder = New StringBuilder()")
            code.append(f"            objSqlBuilder.Append(\"DELETE \")")
            code.append(f"            objSqlBuilder.Append(\" FROM {table.name} \")")
            code.append(f"            objSqlBuilder.Append(\" WHERE \")")
            code.append(f"            objSqlBuilder.Append(filter)")
            code.append(f"            Dim recordsAffected As Integer = 0")
            code.append(f"            recordsAffected = mContext.DBConnections({connection}).ExecuteNonQuery(objSqlBuilder.ToString(), filterValues)")
            code.append(f"            Return recordsAffected")
            code.append(f"        End Function")
            # deleteAll
            code.append(f"        <Description(\"Deletes all records from table '{table.name}'\")>")
            code.append(f"        Public Function {table.name}_DeleteAll() As Integer")
            code.append(f"            Dim filterExpression As String = \"1=1\"")
            code.append(f"            Dim filterValues As Object() = New Object() {{}}")
            code.append(f"            Return {table.name}_DeleteByFilter(filterExpression, filterValues)")
            code.append(f"        End Function")
            # delete
            code.append(f"        <Description(\"Deletes record from table '{table.name}'\")>")
            code.append(f"        Public Function {table.name}_Delete(objInstance As {table.name}VO) As Boolean")
            code.append(f"            Return {table.name}_DeleteByPK({get_columns_as_object_array_parameters_instance(table, table.primary_key.columns, columns_case)})")
            code.append(f"        End Function")
            # delete by pk
            code.append(f"        <Description(\"Deleted record by primary key from table '{table.name}'\")>")
            code.append(f"        Public Function {table.name}_DeleteByPK({get_columns_as_method_parameters(table, table.primary_key.columns)}) As Boolean")
            code.append(f"            Dim filterExpression As String = \"{get_columns_as_sql_where(table, table.primary_key.columns)}\"")
            code.append(f"            Dim filterValues As Object() = New Object() {{{get_columns_as_object_array_parameters(table, table.primary_key.columns)}}}")
            code.append(f"            Return ({table.name}_DeleteByFilter(filterExpression, filterValues) = 1)")
            code.append(f"        End Function")
            # delete by fk
            for fk in sorted(table.foreign_keys, key=lambda fk: locale.strxfrm(fk.name.upper())):
                fkname = snake_to_camel(fk.name, True)
                code.append(f"        <Description(\"Deletes rows by foreign key '{fkname}' from table '{table.name}'\")>")
                code.append(f"        Public Function {table.name}_DeleteBy{fkname}({get_columns_as_method_parameters(table, fk.columns, columns_case)}) As Integer")
                code.append(f"            Dim filterExpression As String = \"{get_columns_as_sql_where(table, fk.columns)}\"")
                code.append(f"            Dim filterValues As Object() = New Object() {{{get_columns_as_object_array_parameters(table, fk.columns, columns_case)}}}")
                code.append(f"            Return {table.name}_DeleteByFilter(filterExpression, filterValues)")
                code.append(f"        End Function")
            # update
            code.append(f"        ' Update")
            code.append(f"        <Description(\"Update record from table '{table.name}'\")>")
            code.append(f"        Public Function {table.name}_Update(objInstance As {table.name}VO) As Boolean")
            code.append(f"            Dim objSqlBuilder As StringBuilder")
            code.append(f"            Dim objSqlArguments As New List(Of Object)")
            for column in table.columns:
                column_net_type = column_to_net_type(column)
                property_name = to_property_name(column.name, columns_case)
                if column_net_type == "String" and column.size > 0:
                    code.append(f"            If Not objInstance.{property_name} Is Nothing AndAlso objInstance.{property_name}.length > {column.size} Then objInstance.{property_name} = objInstance.{property_name}.SubString(0, {column.size})")
            for column in table.columns:
                if column.name == "data_modificacio":
                    code.append(f"            objInstance.{to_property_name(column.name, columns_case)} = Date.Now")
            code.append(f"            objSqlBuilder = New StringBuilder()")
            code.append(f"            objSqlBuilder.Append(\"UPDATE \")")
            code.append(f"            objSqlBuilder.Append(\" {table.name} \")")
            code.append(f"            objSqlBuilder.Append(\" SET \")")
            index = 0
            for column in table.columns:
                if column.is_autoincrement:
                    pass
                else:
                    code.append(f"            objSqlBuilder.Append(\"{"," if index > 0 else ""} {column.name} = ? \")")
                    property_name = to_property_name(column.name, columns_case)
                    column_net_type = column_to_net_type(column)
                    if (column_net_type == "Int16" or column_net_type == "Int32" or column_net_type == "Int64") and column.null:
                        code.append(f"            If objInstance.{property_name} = 0 Then")
                        code.append(f"                objSqlArguments.Add(Nothing)")
                        code.append(f"            Else")
                        code.append(f"                objSqlArguments.Add(objInstance.{property_name})")
                        code.append(f"            End If")
                    else:
                        code.append(f"            objSqlArguments.Add(objInstance.{property_name})")
                    index += 1
            code.append(f"            objSqlBuilder.Append(\" WHERE \")")
            index = 0
            for column_name in table.primary_key.columns:
                property_name = to_property_name(column_name, columns_case)
                code.append(f"            objSqlBuilder.Append(\"{" AND " if index > 0 else ""} {column_name} = ? \")")
                code.append(f"            objSqlArguments.Add(objInstance.{property_name})")
                index += 1

            code.append(f"            Dim recordsAffected As Integer = mContext.DBConnections({connection}).ExecuteNonQuery(objSqlBuilder.ToString(), objSqlArguments.ToArray())")
            code.append(f"            Return recordsAffected > 0")
            code.append(f"        End Function")
            # updateOnlyModified
            code.append(f"        ' Update only modified ")
            code.append(f"        <Description(\"Update record from table\")>")
            code.append(f"        Public Function {table.name}_UpdateOnlyModified(ByVal objInstance As {table.name}VO) As Boolean")
            code.append(f"            Dim objSqlBuilder As StringBuilder")
            code.append(f"            Dim isChanged As Boolean = False")
            code.append(f"            Dim objSqlArguments As New List(Of Object)")
            for column in table.columns:
                column_net_type = column_to_net_type(column)
                property_name = to_property_name(column.name, columns_case)
                if column_net_type == "String" and column.size > 0:
                    code.append(f"            If Not objInstance.{property_name} Is Nothing AndAlso objInstance.{property_name}.length > {column.size} Then objInstance.{property_name} = objInstance.{property_name}.SubString(0, {column.size})")
            for column in table.columns:
                if column.name == "data_modificacio":
                    code.append(f"            objInstance.{to_property_name(column.name, columns_case)} = Date.Now")
            code.append(f"            Dim objVO As {table.name}VO = {table.name}_SelectSingleByVO(objInstance)")
            code.append(f"            If objVO Is Nothing Then Return False")
            code.append(f"            objSqlBuilder = New StringBuilder()")
            code.append(f"            objSqlBuilder.Append(\"UPDATE \")")
            code.append(f"            objSqlBuilder.Append(\" {table.name} \")")
            code.append(f"            objSqlBuilder.Append(\" SET \")")
            index = 0
            for column in table.columns:
                if column.is_autoincrement:
                    pass
                else:
                    column_net_type = column_to_net_type(column)
                    property_name = to_property_name(column.name, columns_case)
                    if column_net_type == "String":
                        code.append(f"            If Not (\"\" & objVO.{property_name}).Equals(\"\" & objInstance.{property_name}) Then")
                    else:
                        code.append(f"            If Not objVO.{property_name} = objInstance.{property_name} Then")
                    code.append(f"                If isChanged Then objSqlBuilder.Append(\", \")")                    
                    if (column_net_type == "Int16" or column_net_type == "Int32" or column_net_type == "Int64") and column.null:
                        code.append(f"                objSqlBuilder.Append(\" {column.name} = ? \")")
                    elif (column_net_type == "Int16"):
                        code.append(f"                objSqlBuilder.Append(\" {column.name} = ? \")")
                    else:
                        code.append(f"                objSqlBuilder.Append(\"{column.name} = ? \")")
                    if (column_net_type == "Int16" or column_net_type == "Int32" or column_net_type == "Int64") and column.null:
                        code.append(f"                If objInstance.{property_name} = 0 Then")
                        code.append(f"                    objSqlArguments.Add(Nothing)")
                        code.append(f"                Else")
                        code.append(f"                    objSqlArguments.Add(objInstance.{property_name})")
                        code.append(f"                End If")
                    elif (column_net_type == "String"):
                        code.append(f"                If objInstance.{property_name} Is Nothing Then")
                        if not column.null and require_space_when_null:
                            code.append(f"                    objSqlArguments.Add(\" \")")
                        else:
                            code.append(f"                    objSqlArguments.Add(Nothing)")
                        code.append(f"                Else")
                        code.append(f"                    objSqlArguments.Add(objInstance.{property_name}.Trim())")
                        code.append(f"                End If")
                    else:
                        code.append(f"                objSqlArguments.Add(objInstance.{property_name})")
                    code.append(f"                isChanged = True")
                    code.append(f"            End If")
                    index += 1
            code.append(f"            objSqlBuilder.Append(\" WHERE \")")
            index = 0
            for column_name in table.primary_key.columns:
                column_net_type = column_to_net_type(column)
                property_name = to_property_name(column_name, columns_case)
                code.append(f"            objSqlBuilder.Append(\"{" AND " if index > 0 else ""} {column_name} = ? \")")
                code.append(f"            objSqlArguments.Add(objInstance.{property_name})")
                index += 1
            code.append(f"            Dim recordsAffected As Integer = 0")
            code.append(f"            If Not isChanged Then")
            code.append(f"                recordsAffected = 1")
            code.append(f"            Else")
            code.append(f"                recordsAffected = mContext.DBConnections({connection}).ExecuteNonQuery(objSqlBuilder.ToString(), objSqlArguments.ToArray())")
            code.append(f"            End If")
            code.append(f"            Return recordsAffected > 0")
            code.append(f"        End Function")
            # exists
            code.append(f"        <Description(\"Check if a record exist\")>")
            code.append(f"        Public Function {table.name}_Exists(objInstance As {table.name}VO) As Boolean")
            code.append(f"            Dim result As Boolean = False")
            code.append(f"            If {get_columns_if_confition_nothing(table, table.primary_key.columns, require_space_when_null, columns_case)} Then")
            code.append(f"                result = False")
            code.append(f"            Else")
            code.append(f"                Dim objInstanceDB As {table.name}VO = {table.name}_SelectByPK({get_columns_as_object_array_parameters_instance(table, table.primary_key.columns, columns_case)})")
            code.append(f"                If objInstanceDB Is Nothing Then")
            code.append(f"                    result = False")
            code.append(f"                Else")
            code.append(f"                    result = True")
            code.append(f"                End If")
            code.append(f"            End If")
            code.append(f"            Return result")
            code.append(f"        End Function")
            # GetDifferencesWithDB
            code.append(f"        <Description(\"Check differences between Instance And existing record\")>")
            code.append(f"        Public Function {table.name}_GetDifferencesWithDB(objInstance As {table.name}VO) As String")
            code.append(f"            Dim result As New StringBuilder()")
            code.append(f"            If {get_columns_if_confition_nothing(table, table.primary_key.columns, require_space_when_null, columns_case)} Then")
            code.append(f"                result.Append(\"NOEXIST\")")
            code.append(f"            Else")
            code.append(f"                Dim objInstanceDB As {table.name}VO = {table.name}_SelectByPK({get_columns_as_object_array_parameters_instance(table, table.primary_key.columns, columns_case)})")
            code.append(f"                If objInstanceDB Is Nothing Then")
            code.append(f"                    result.Append(\"NOEXIST\")")
            code.append(f"                Else")
            code.append(f"                    Dim differences As String = \"\"")
            code.append(f"                    objInstanceDB.IsEqual(objInstance, differences)")
            code.append(f"                    result.Append(\"EXIST:\").Append(differences)")
            code.append(f"                End If")
            code.append(f"            End If")
            code.append(f"            Return result.ToString")
            code.append(f"        End Function")
            code.append(f"")

        # views
        for view in sorted(self._schema.views, key=lambda view: locale.strxfrm(view.name.upper())):
            if not view.name in views:
                continue
            code.append(f"        '{view.name}")
            code.append(f"        Public Function {view.name}_SelectScalarBy(column As String, filter As String, filterValues As Object()) As Object")
            code.append(f"            Dim objSqlBuilder As New StringBuilder")
            code.append(f"            objSqlBuilder.Append(\"SELECT \" & column & \" FROM {view.name} WHERE \" & filter)")
            code.append(f"            Return mContext.DBConnections({connection}).ExecuteScalar(objSqlBuilder.ToString(), filterValues)")
            code.append(f"        End Function")
            code.append(f"        Public Function {view.name}_SelectByFilterAsDataTable(columns As String, filter As String, filterValues As Object(), orderby As String, Optional startIndex As Integer = 0, Optional length As Integer = -1) As Datatable")
            code.append(f"            Dim objSqlBuilder As StringBuilder")
            code.append(f"            objSqlBuilder = New StringBuilder()")
            code.append(f"            objSqlBuilder.Append(\"SELECT \")")
            code.append(f"            If columns = \"\" Then")
            code.append(f"                objSqlBuilder.Append(\"{view.name}.*\")")
            code.append(f"            Else")
            code.append(f"                objSqlBuilder.Append(columns)")
            code.append(f"            End If")
            code.append(f"            objSqlBuilder.Append(\" FROM {view.name} \")")
            code.append(f"            If filter <> \"\" Then")
            code.append(f"                objSqlBuilder.Append(\" WHERE \")")
            code.append(f"                objSqlBuilder.Append(filter)")
            code.append(f"            End If")
            code.append(f"            If orderby <> \"\" Then")
            code.append(f"                objSqlBuilder.Append(\" ORDER BY \")")
            code.append(f"                Dim iOrderByParts As Integer = 0")
            code.append(f"                For Each orderByPart As String In orderBy.Split(\",\"c)")
            code.append(f"                    orderByPart = orderByPart.Trim()")
            code.append(f"                    If iOrderByParts > 0 Then objSqlBuilder.Append(\",\")")
            code.append(f"                    If orderByPart.indexOf(\".\") = -1 Then")
            code.append(f"                        objSqlBuilder.Append(\"{view.name}.\" & orderByPart)")
            code.append(f"                    Else")
            code.append(f"                        objSqlBuilder.Append(orderbyPart)")
            code.append(f"                    End If")
            code.append(f"                    iOrderByParts += 1")
            code.append(f"                Next")
            code.append(f"            End If")
            code.append(f"            Return mContext.DBConnections({connection}).ExecuteDataTablePaginated(objSqlBuilder.ToString(), startIndex, length, filterValues)")
            code.append(f"        End Function")
            code.append(f"")


        # Procedures
        for procedure in sorted(self._schema.procedures, key=lambda procedure: locale.strxfrm(procedure.name.upper())):
            if not procedure.name in procedures:
                continue
            code.append(f"        <Description(\"Execute sp named {procedure.name}\")>")
            code.append(f"        Public Sub Exec_{procedure.name}({get_procedure_arguments(procedure)})")
            code.append(f"            Try ")
            code.append(f"                Dim cmd As IDbCommand = mContext.DBConnections({connection}).CreateCommand(\"\", New Object() {{}})")
            code.append(f"                cmd.CommandText = \"{procedure.name}\"")
            code.append(f"                cmd.CommandType = CommandType.StoredProcedure")
            index = 0
            for argument in procedure.arguments:
                argument_net_type = column_to_net_type(argument)
                code.append(f"                Dim param{index} As IDbDataParameter = cmd.CreateParameter()")
                code.append(f"                param{index}.ParameterName = \"{argument.name}\"")
                # value
                if argument_net_type == "String":
                    code.append(f"                param{index}.Value = {argument.name}")
                else:
                    code.append(f"                param{index}.Value = If({argument.name}.HasValue, CType({argument.name}.Value, Nullable(Of Decimal)), Nothing)")
                # size
                if argument.size > 0:
                    code.append(f"                param{index}.Size = {argument.size}")
                # direction
                if argument.direction == "IN":
                    code.append(f"                param{index}.Direction = ParameterDirection.Input")
                elif argument.direction == "IN-OUT":
                    code.append(f"                param{index}.Direction = ParameterDirection.InputOutput")
                elif argument.direction == "OUT":
                    code.append(f"                param{index}.Direction = ParameterDirection.Output")
                # type
                if argument_net_type == "Decimal":
                    code.append(f"                param{index}.DbType = DbType.Decimal")
                else:
                    code.append(f"                param{index}.DbType = DbType.String")
                index += 1 
            index = 0
            for argument in procedure.arguments:
                code.append(f"                cmd.Parameters.Add(param{index})")
                index += 1 
            code.append(f"                cmd.ExecuteNonQuery()")
            # todo .. read output arguments
            code.append(f"            Catch e As Exception")
            code.append(f"                Throw")
            code.append(f"            End Try")
            code.append(f"        End Sub")
            

        # debug !!!
        #code = code[code.index("xxxx"):]

        code.append(f"#End Region")
        code.append(f"")
        code.append(f"        'Business Logic")
        code.append(f"")
        code.append(f"    End Class")
        # end namespace
        code.append(f"End Namespace")
        # return
        return "\n".join(code)
    