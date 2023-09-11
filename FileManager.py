import csv
import os

from SQLmanager import SqlWorker


class FileManager():
    def __init__(self, path, file_type=None):
        self.path = path
        self.type = file_type

    def read(self):
        encoding = 'utf-8-sig'
        file_type = 'csv'
        if self.type:
            file_type = self.type
        with open(self.path, 'r', encoding=encoding) as f:
            print(eval(file_type))
            reader = eval(file_type).reader(f)
            header = next(reader)
            for row in reader:
                sql_conn = SqlWorker('test_yield.db')
                sql_conn.init_files_db()
                yield sql_conn.sqlcmd(f'insert into files values(\'{row[0]}\',\'{row[1]}\',\'{row[2]}\',')

                print(f'{header[0]}{row[0]}: {header[1]}={row[1]}, {header[2]}={row[2]}')

print(os.getcwd())
t = FileManager('./learn/temp2.csv')
t.read()
