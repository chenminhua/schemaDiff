#!/usr/bin/env python3
import pymysql
from prettytable import PrettyTable


def getTableList(conn):
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES;")
    return [t[0] for t in cursor]
    cursor.close()


def getDatabaseSchema(conn):
    result = {}
    tableList = getTableList(conn)
    for t in tableList:
        result[t] = getTableSchema(t, conn)
    return result


def getTableSchema(table_name, conn):
    cursor = conn.cursor()
    cursor.execute('desc ' + table_name)
    columns = cursor.fetchall()

    result = {}
    for column in columns:
        (col_name, col_type, col_nullable, col_key, col_default, extra) = column
        result[col_name] = column
    return result


class TableDiff:
    def __init__(self, tableName, table1, table2):
        self.tableName = tableName
        self.table1 = table1
        self.table2 = table2

    def get_defalut_clause(self, default_value):
        if (default_value is None):
            return ""
        if (default_value == ""):
            return "DEFAULT ''"
        return "DEFAULT " + default_value

    def column_info(self, col):
        if col is None:
            return "None"
        (col_name, col_type, col_nullable,
         col_key, col_default, extra) = col
        nullable_clause = " " if col_nullable == "YES" else " NOT NULL "
        return '{} {} {} {}'.format(col_type, nullable_clause, self.get_defalut_clause(col_default), extra)

    def printDiff(self):
        diffTable = PrettyTable(["col_name", "d1", "d2"])
        col_names = sorted(
            set(list(self.table1.keys()) + list(self.table2.keys())))
        diffcount = 0
        for column_name in col_names:
            col1 = self.column_info(self.table1.get(column_name))
            col2 = self.column_info(self.table2.get(column_name))
            if (col1 != col2):
                diffcount += 1
                [col1, col2] = [highlight(col1), highlight(col2)]
                diffTable.add_row(
                    [column_name, col1, col2])
        print('\n========================= {} has {} different columns ==========================='.format(
            self.tableName, diffcount))
        if (diffcount > 0):
            print(diffTable)


def highlight(s, color="red"):
    if color == "red":
	    return '\033[31m' + s + '\033[0m'
    return '\033[32m' + s + '\033[0m'


def diffSchema(schema1, schema2):
    keys = sorted(set(list(schema1.keys()) + list(schema2.keys())))
    diffTable = PrettyTable(["table_name", "d1", "d2"])
    for table_name in keys:
        if (schema1.get(table_name) is None) or (schema2.get(table_name) is None):
            d1_table_exist = highlight("Not Exist") if schema1.get(table_name) is None else highlight("Exist", "green")
            d2_table_exist = highlight("Not Exist") if schema2.get(table_name) is None else highlight("Exist", "green")
            diffTable.add_row([table_name, d1_table_exist, d2_table_exist])
        else:
            diff = TableDiff(table_name, schema1.get(
                table_name), schema2.get(table_name))
            diff.printDiff()

    print(diffTable)


def connect_dbs(args):
    conn1 = pymysql.connect(host=args['h1'],
                            port=args['p1'],
                            user=args['u1'],
                            password=args['pw1'],
                            database=args['d1'])
    conn2 = pymysql.connect(host=args['h2'],
                            port=args['p2'],
                            user=args['u2'],
                            password=args['pw2'],
                            database=args['d2'])
    return [conn1, conn2]


import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-p1', type=int, default=3306,
                    help='db1 port', required=False)
parser.add_argument('-h1', help='db1 host', type=str)
parser.add_argument('-d1', help='db1 name', type=str)
parser.add_argument('-u1', help='db1 user', type=str)
parser.add_argument('-pw1', help='db1 password', type=str)

parser.add_argument('-p2', type=int, default=3306,
                    help='db2 port', required=False)
parser.add_argument('-h2', help='db2 host', type=str)
parser.add_argument('-d2', help='db2 name', type=str)
parser.add_argument('-u2', help='db2 user', type=str)
parser.add_argument('-pw2', help='db2 password', type=str)
args = vars(parser.parse_args())


if (args.get('h1') is None):
    print("请填写数据库 1 地址, -h1")
    exit()
if (args.get('h2') is None):
    print("请填写数据库 2 地址, -h2")
    exit()
if (args.get('u1') is None):
    print("请填写数据库 1 用户, -u1")
    exit()
if (args.get('u2') is None):
    print("请填写数据库 2 用户, -u2")
    exit()
if (args.get('pw1') is None):
    print("请填写数据库 1 密码, -pw1")
    exit()
if (args.get('pw2') is None):
    print("请填写数据库 2 用户, -pw2")
    exit()


[conn1, conn2] = connect_dbs(args)

schema1 = getDatabaseSchema(conn1)
schema2 = getDatabaseSchema(conn2)

diffSchema(schema1, schema2)
