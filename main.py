import os,sys


from pathlib import Path
import ctypes.wintypes

from SQLmanager import SqlWorker, FileSqlWork
from specs import KNOWNFOLDERID_LIST
from tools import Folders, Scan, time_it, str_of_size, scan_files, make_json, make_csv_by_batch


# def SHGetKnownFolderPath(fid):
#     buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
#     ctypes.windll.shell32.SHGetKnownFolderPath(fid, 0, None, buf)
#     return buf.value


def test():
    cwd = os.getcwd()
    for i in os.scandir(cwd):
        print(i.path, i.stat().st_size / 1024 / 1024)
        break


def scan():
    info, total_info, total_file = scan_files()
    return info


def work_202307():
    cnn = SqlWorker('test4.db')
    cnn.init_file_db()
    info, total_info, total_file = scan_files(cnn)
    cnn.commit()
    make_csv_by_batch(total_file)
    make_json(total_info)
    print(info)

def compare_folder(result, sql_worker):
    # 如果设定是前面路径，后面是source_path字样，那么前面就是需要拷贝的源头
    for i in result:
        db_cmd = f"UPDATE {sql_worker.table_name} SET SAME = 0 WHERE FILE_NAME=\"{i['name']}\" AND RELATIVE_PATH=\"{i['relative_path']}\" AND SIZE= \"{i['size']}\""
        sql_worker.sqlcmd(db_cmd)
    sql_worker.commit()
    return True

def move_folder(sql_worker):
    db_cmd = f'SELECT RELATIVE_PATH, SIZE FROM {sql_worker.table_name} WHERE SAME IS NULL'
    print(db_cmd)
    sql_worker.sqlcmd(db_cmd)
    result = sql_worker.fetch_all()
    size = sum(i[1] for i in result if isinstance(i[1], (int)))
    print(f'You will about to move {len(result)} files, total size: {size}')
    print(f'That\'s {str_of_size(size)}')
def move_files():
    pass

def work_20230831():
    pathdir = sys.argv[1]
    folder = Folders(pathdir)
    sql_worker = SqlWorker('test1.db')
    sql_worker.table_name = 'COMPARE_FOLDER'
    table_name = 'COMPARE_FOLDER'
    rows_set = '''
        FILE_NAME TEXT NOT NULL,\
        PATH TEXT NOT NULL,\
        RELATIVE_PATH TEXT NULL,\
        SIZE BIGINT NOT NULL,\
        SAME BOOL NULL
        '''
    sql_worker.set_db_info(table_name, rows_set)
    # 走新建模式 
    result = folder.walk_through_result(relative_path=True)
    print(result)
    make_json(result)
    if len(sys.argv) == 2:
        sql_worker.init_table()
        for i in result:
            db_cmd = f"insert into {sql_worker.table_name} values (NULL, \"{i['name']}\", \"{i['dir']}\",\"{i['relative_path']}\", \"{i['size']}\", NULL)"
            sql_worker.sqlcmd(db_cmd)
        sql_worker.commit()
    # 走比较模式
    if len(sys.argv) == 3:
        target_path = sys.argv[2]
        if target_path == "source_path":            
            # 如果设定是前面路径，后面是source_path字样，那么前面就是需要拷贝的源头
            compare_folder(result, sql_worker)
            return move_folder(sql_worker)
        if target_path == 'move':
            move_folder(sql_worker)
            return True
    return result

def work_20230904():
    pathdir = sys.argv[1]
    file_worker = FileSqlWork('test23.db')
    folder = Folders(pathdir, sql_worker=file_worker)
    if len(sys.argv) == 2:
        file_worker.init_table()
        result = folder.walk_through_result(relative_path=True)
        for i in result:
            db_cmd = f"insert into {file_worker.table_name} values (NULL, \"{i['name']}\", \"{i['dir']}\", \
                        \"{i['relative_path']}\", \"{i['size']}\", NULL)"
            file_worker.sqlcmd(db_cmd)
        file_worker.commit()
    if len(sys.argv) == 3:
        result = folder.walk_through_result(relative_path=True, update_db=True)
    return True

def work_for_filecounter():
    file_worker = FileSqlWork('test23.db')
    move_folder(file_worker)

if __name__ == "__main__":
    # work_20230831()
    work_20230904()
    # work_for_filecounter()

