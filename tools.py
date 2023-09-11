import csv
import ctypes
import os
import time
import json
from ctypes import wintypes, Structure
from specs import KNOWNFOLDERID_LIST
from functools import wraps
from SQLmanager import SqlWorker


def time_it(func):
    '''
    计时装饰器，统计函数运行时间
    '''
    @wraps(func)
    def decorated(*args, **kwargs):
        start_time = time.time()
        r = func(*args, **kwargs)
        duration = time.time() - start_time
        print('Name: ', func.__name__, 'Duration: ', duration)
        return r

    return decorated


class GUID(Structure):
    _fields_ = [
        ('Data1', wintypes.DWORD),
        ('Data2', wintypes.WORD),
        ('Data3', wintypes.WORD),
        ('Data4', wintypes.BYTE * 8)
    ]

    def __init__(self, l, w1, w2, b1, b2, b3, b4, b5, b6, b7, b8):
        """Create a new GUID."""
        self.Data1 = l
        self.Data2 = w1
        self.Data3 = w2
        self.Data4[:] = (b1, b2, b3, b4, b5, b6, b7, b8)

    def __repr__(self):
        b1, b2, b3, b4, b5, b6, b7, b8 = self.Data4
        return 'GUID(%x-%x-%x-%x%x%x%x%x%x%x%x)' % (
            self.Data1, self.Data2, self.Data3, b1, b2, b3, b4, b5, b6, b7, b8)


class ToGUID(Structure):
    _fields_ = [
        ('Data1', wintypes.DWORD),
        ('Data2', wintypes.WORD),
        ('Data3', wintypes.WORD),
        ('Data4', wintypes.BYTE * 8)
    ]

    def __init__(self, info):
        """Convert to a new GUID."""
        data4 = []
        pure = info.strip('{}').split('-')
        self.Data1 = int(pure[0], 16)
        self.Data2 = int(pure[1], 16)
        self.Data3 = int(pure[2], 16)
        data4.append(int(pure[3][0:2], 16))
        data4.append(int(pure[3][2:4], 16))
        temp1 = pure[4]
        res = [int(temp1[i:i + 2], 16) for i in range(0, len(temp1), 2)]
        data4.extend(res)
        self.Data4[:] = data4

    def __repr__(self):
        b1, b2, b3, b4, b5, b6, b7, b8 = self.Data4
        x = None
        # x = 'GUID(%x-%x-%x-%x%x%x%x%x%x%x%x)' % (
        #          self.Data1, self.Data2, self.Data3, b1, b2, b3, b4, b5, b6, b7, b8)
        return f'{x}+GUID({self.Data1}-{self.Data2}-{self.Data3}-{b1}{b2}{b3}{b4}{b5}{b6}{b7}{b8})'


class Folders(object):
    def __init__(self, path, name=None, files_count=None, folders_count=None, size=None, software=None, alias=None,
                 subfolders=None, sql_worker=None) -> None:
        self.name = name
        self.path = path
        self.files_count = files_count
        self.folders_count = folders_count
        self.size = size
        self.software = software
        self.alias = alias
        self.subfolders = subfolders
        self.sql_worker = sql_worker

    def walk_through_result(self, show_size=False, relative_path=False, create_db=False, update_db=False):
        '''print the folder info shows name dir and sizes
        {'name': 'file name', 'dir': 'whole path', 'size': 111}
        '''
        result = []
        for (root, dirs, files) in os.walk(self.path):  #列出windows目录下的所有文件和文件名
            for file in files:
                fdname = os.path.join(root, file)
                size = os.path.getsize(fdname)
                fixed_size = str_of_size(size)
                member = {'name':file, 'dir':str(fdname), 'size':size}
                if show_size:
                    member['fixed_size'] = fixed_size
                if relative_path:
                    member['relative_path'] = os.path.relpath(fdname, self.path)
                if create_db:
                    self.sql_worker.create_db()
                if update_db:
                    self.sql_worker.update_db((file, fdname, size, member['relative_path']))
                result.append(member)
        return result
    
    def get_folder_size(self):
        pass

    def get_files_count(self):
        pass

    def set_some_folder(self, path_type_id):
        alias = ""
        match path_type_id:
            case 0:
                alias = "Desktop"
            case 5:
                alias = "Documents"
            case 6:
                alias = "Favorites"
            case 13:
                alias = "Music"
            case 14:
                alias = "Videos"
            case 19:
                alias = "Network Shortcuts"
            case 20:
                alias = "Fonts"
            case _:
                return None
        self.path = get_doc_path(path_type_id)
        self.alias = alias
        return True

    def get_known_folder(self, info_dict):
        for key in info_dict:
            self.path = SHGetKnownFolderPath(info_dict[key])
            self.alias = key


class Scan():
    def __init__(self, cnn) -> None:
        self.d = []
        self.s = 0
        self.files_count = 0
        self.total_file = []
        self.cnn = cnn


    def clear(self):
        self.d = []
        self.s = 0
        self.files_count = 0

    def scan(self, dir, alias=None):

        commit_count = 0
        for i in os.scandir(dir):
            if alias == 'Documents' and (i.name in ("My Music", "My Pictures", "My Videos")):
                continue
            if i.is_dir():
                self.scan(i, alias)
            else:
                self.d.append(i.path)
                self.s += i.stat().st_size
                if self.cnn:
                    cmand = f'insert into FILES values(null, "{i.name}", "{i.path}", {i.stat().st_size}, "{alias}")'
                    self.cnn.sqlcmd(cmand)
                # make_csv_by_line(i) #这句是写入csv文件，会严重拖慢速度，暂时关闭
                file_info = [i.name, i.path, i.stat().st_size, i.path.split('.')[-1], alias]
                self.total_file.append(file_info)
                if i.is_file():
                    self.files_count += 1


@time_it
def make_json(info):
    with open('folders.json', 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False)


def make_csv_by_line(z):
    header = ['name', 'path', 'size']
    exist = False
    data = [z.name, z.path, z.stat().st_size]
    if os.path.exists('temp.csv'):
        exist = True

    with open('temp.csv', mode='a', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        if not exist:
            writer.writerow(header)
        writer.writerow(data)

@time_it
def make_csv_by_batch(z):
    header = ['name', 'path', 'size', 'suffix', 'alias']
    with open('btemp.csv', mode='w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(z)

    

def get_doc_path(CSIDL_PERSONAL):
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, 0, buf)
    return buf.value


def SHGetKnownFolderPath(info):
    info = ToGUID(info)
    ptr = ctypes.c_wchar_p()
    ctypes.windll.shell32.SHGetKnownFolderPath(info, 0, None, ctypes.byref(ptr))
    return ptr.value


def str_of_size(size):
    '''
    递归实现，精确为最大单位值 + 小数点后三位
    '''

    def strofsize(integer, remainder, level):
        if integer >= 1024:
            remainder = integer % 1024
            integer //= 1024
            level += 1
            return strofsize(integer, remainder, level)
        else:
            return integer, remainder, level

    units = ['B', 'K', 'M', 'G', 'T', 'PB']
    integer, remainder, level = strofsize(size, 0, 0)
    if level + 1 > len(units):
        level = -1
    return ('{}.{:>03d}{}'.format(integer, remainder, units[level]))


@time_it
def scan_files(cnn=None):
    '''主要方法，进行文件扫描，生成的是总计大小和文件夹信息'''
    path_list = []
    total_size = 0
    total_files_count = 0
    a = Folders()
    s = Scan(cnn)
    for i in range(60):
        # 获取个人文件夹的地址及别名
        if not a.set_some_folder(i):
            # 如果没找到对应的文件夹，就跳过找下一个
            continue
        # s = Scan()
        s.clear()
        s.scan(a.path, a.alias)
        file_dict = {'path': a.path, "name": a.alias,
                     "subfolders": s.d, "size": s.s}
        path_list.append(file_dict)
        total_size += s.s
        total_files_count += s.files_count
    a.get_known_folder(KNOWNFOLDERID_LIST)
    # s = Scan()
    s.clear()
    s.scan(a.path, a.alias)

    subfolders_list = s.d
    file_dict = {'path': a.path, "name": a.alias,
                 "subfolders": subfolders_list, "size": s.s}
    path_list.append(file_dict)
    total_size += s.s
    total_files_count += s.files_count
    total_info = {"st_size": total_size, "size": str_of_size(
        total_size), "files": total_files_count, "path_list": path_list}

    info = f'{str_of_size(total_size)}, total {total_files_count} files'
    # s.cnn.commit()
    return info, total_info, s.total_file
