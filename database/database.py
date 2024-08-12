from . import connect
from dataclasses import make_dataclass
import os

myclient = connect.Database(os.path.join(os.getcwd(), 'DataBase.db')).connect()

class DataBase:
    def __init__(self, table: str = None, query: dict = None, data: dict = None):
        self.table = table
        self.data = data
        self.query = query
        self.conn = myclient
        self.cursor = self.conn.cursor()

    def __infer_type(self,value):
        try:
            if '.' in value:
                return float(value)
            elif "datetime" == value:
                return "datetime"
            else:
                return int(value)
        except ValueError:
            return value

    @property
    def nametable(self):
        data_dict = dict()
        for table in connect.config.sections():
            data_dict[table] = table
        fields = [(key, type(self.__infer_type(value))) for key, value in data_dict.items()]
        data = [self.__infer_type(value) for value in data_dict.values()]
        DataClass = make_dataclass("nameLoadTable", fields)
        return DataClass(*data)
    
    def __dataclass(self,table,data):
        data_dict = {key: value for key, value in connect.config[table].items()}
        fields = [(key, type(self.__infer_type(value))) for key, value in data_dict.items()]
        DataClass = make_dataclass(table, fields)
        return DataClass(*data)
        
    @property
    def insert(self):
        if self.data is None:
            raise ValueError("Data is not set.")
        columns = ', '.join(self.data.keys())
        placeholders = ', '.join(['?'] * len(self.data))
        sql = f"INSERT INTO {self.table} ({columns}) VALUES ({placeholders})"
        self.cursor.execute(sql, tuple(self.data.values()))
        self.conn.commit()
        return self.cursor.lastrowid

    @property
    def get(self):
        listdata = []
        query = ' AND '.join([f"{k} = ?" for k in self.query.keys()])
        sql = f"SELECT * FROM {self.table} WHERE {query}"
        self.cursor.execute(sql, tuple(self.query.values()))
        for item in self.cursor.fetchall():
            listdata.append(self.__dataclass(self.table,item))
        return listdata

    @property
    def check(self):
        result = self.get
        return bool(result)
    
    @property
    def all(self):
        listdata = []
        sql = f"SELECT * FROM {self.table}"
        self.cursor.execute(sql)
        for item in self.cursor.fetchall():
            listdata.append(self.__dataclass(self.table,item))
        return listdata

    @property
    def set(self):
        set_query = ', '.join([f"{k} = ?" for k in self.data.keys()])
        query = ' AND '.join([f"{k} = ?" for k in self.query.keys()])
        sql = f"UPDATE {self.table} SET {set_query} WHERE {query}"
        self.cursor.execute(sql, tuple(self.data.values()) + tuple(self.query.values()))
        self.conn.commit()

    @property
    def delete(self):
        query = ' AND '.join([f"{k} = ?" for k in self.query.keys()])
        sql = f"DELETE FROM {self.table} WHERE {query}"
        self.cursor.execute(sql, tuple(self.query.values()))
        self.conn.commit()


