import sqlite3


def create_database():
    conn = sqlite3.connect('test.db')
    print("数据库打开成功")
    c = conn.cursor()
    c.execute('''
    CREATE TABLE FILES
    (ID INT PRIMARY KEY     NOT NULL,
    NAME    TEXT            NOT NULL,
    PATH    TEXT            NOT NULL,
    SIZE    INTEGER         NOT NULL,
    )''')
    conn.commit()
    conn.close()

def insert_files(info):
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    c.execute('''
    INSERT INFO FILES(ID
    ''')


class SqlWorker:

    cmd_count = 0

    def __init__(self, path, *args, **kwargs):
        self.dbpath = path
        self.cnn = sqlite3.connect(path)
        self.cursor = self.cnn.cursor()
        self.table_name = ""
        self.rows = ""
        # super(SqlWorker, self).__init__(*args, **kwargs)

    # def sqlcmd(self, cmdline):
    #     if self.cmd_count > 50:
    #         self.cnn.commit()
    #         self.cmd_count = 0
    #     self.cursor.execute(cmdline)
    #     self.cmd_count+=1
    #     print(self.cmd_count)

    def set_db_info(self, table_name, rows):
        self.table_name, self.rows = table_name, rows
        
    def sqlcmd(self, cmdline):
        self.cursor.execute(cmdline)

    def commit(self):
        self.cnn.commit()

    def rollback(self):
        self.cnn.rollback()

    def close(self):
        self.cursor.close()
        self.cnn.close()

    def connect_test(self, path):
        return sqlite3.connect(path)

    def fetch(self):
        return self.cursor.fetchone()

    def fetch_all(self):
        return self.cursor.fetchall()

    def init_table(self):
        # 判断是否有这个数据库？
        drop_table = f'DROP TABLE IF EXISTS {self.table_name};'
        self.sqlcmd(drop_table)
        self.commit()
        sqline = f'CREATE TABLE IF NOT EXISTS {self.table_name} \
        (id integer primary key, \
        {self.rows})'
        return self.sqlcmd(sqline)
    
    def init_file_db(self):
        self.rows_set = '''name text not null, \
        path text not null, \
        size text not null, \
        alias TEXT NOT NULL'''
        self.table_name = 'FILES'
        return self.init_table()
    #
    #     self.cursor.execute('''
    # CREATE TABLE FILES
    # (ID INTEGER PRIMARY KEY     NOT NULL,
    # NAME    TEXT    NOT NULL,
    # PATH    TEXT    NOT NULL,
    # SIZE    INTEGER NOT NULL,
    # )''')
    #     self.cnn.commit()
    #     self.cnn.close()

    def insert_lines(self, v):
        cmd_line = f"insert into table values(\"{v['name']}\", \"{v['path']}\", \"{v['size']}\")"
        self.sqlcmd(cmd_line)
        self.commit()

class FileSqlWork(SqlWorker):
    '''尝试做一个子类'''
    def __init__(self, path):
        super().__init__(path)
        self.table_name = 'COMPARE_FOLDER'
        self.rows = '''
            FILE_NAME TEXT NOT NULL,\
            PATH TEXT NOT NULL,\
            RELATIVE_PATH TEXT NULL,\
            SIZE BIGINT NOT NULL,\
            SAME BOOL NULL
            '''
        
    def create_db(self):
        print("Good!")
        
    def update_db(self, info):
        file, fdname, size, relative_path = info
        s = self
        _= f'SELECT FILE_NAME, RELATIVE_PATH, SIZE FROM {s.table_name} \
            WHERE FILE_NAME = \"{file}\" AND RELATIVE_PATH = \"{relative_path}\"'
        s.sqlcmd(_)
        result = s.fetch_all()
        if result == []:
            s.sqlcmd(f'insert into {s.table_name} values \
                    (NULL, \"{file}\", \"{fdname}\",\"{relative_path}\", \"{size}\", NULL)')
        elif result[0][2] == size:
            db_cmd = f"UPDATE {s.table_name} SET SAME = 1 \
                WHERE FILE_NAME=\"{file}\" AND RELATIVE_PATH=\"{relative_path}\" AND SIZE= \"{size}\""
            
            s.sqlcmd(db_cmd)
        else:
            _ = f'UPDATE {s.table_name} SET SIZE = \"{size}\" , PATH = \"{fdname}\"\
                WHERE FILE_NAME=\"{file}\" AND RELATIVE_PATH=\"{relative_path}\" '
            s.sqlcmd(_)
        s.commit()
        

class CSVSqlWorker(SqlWorker):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path = args[0]




